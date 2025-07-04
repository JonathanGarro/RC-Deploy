"""
Celery tasks for the surge app.
"""
import logging
import requests
from datetime import datetime
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from celery import shared_task
from .models import Country, MolnixTag, SurgeAlert, ApiStatus

logger = logging.getLogger(__name__)


@shared_task
def fetch_surge_alerts():
    """
    Fetch surge alerts from the IFRC API and store them in the database.
    Handles pagination and checks for new and updated records.
    """
    logger.info("Starting surge alert data fetch")
    logger.debug(f"Using API URL: {settings.IFRC_API_URL}")

    url = settings.IFRC_API_URL
    next_page = url
    total_created = 0
    total_updated = 0
    page_count = 0

    while next_page:
        page_count += 1
        logger.info(f"Fetching data from page {page_count}: {next_page}")
        try:
            logger.debug(f"Sending GET request to: {next_page}")
            response = requests.get(next_page)
            response.raise_for_status()

            logger.debug(f"Received response with status code: {response.status_code}")
            data = response.json()

            # Process the results
            results = data.get('results', [])
            logger.info(f"Retrieved {len(results)} records from page {page_count}")

            if not results:
                logger.warning("No results found in the API response")

            process_results(results)

            # Update counters
            new_created = len([r for r in results if r.get('_created', False)])
            new_updated = len([r for r in results if r.get('_updated', False)])
            total_created += new_created
            total_updated += new_updated

            logger.info(f"Page {page_count} processing complete. Created: {new_created}, Updated: {new_updated}")

            # Check for next page
            next_page = data.get('next')
            if next_page:
                logger.debug(f"Next page URL: {next_page}")
            else:
                logger.debug("No more pages to fetch")

        except requests.RequestException as e:
            logger.error(f"Error fetching data from API: {e}")
            logger.exception("Full exception details:")
            break
        except ValueError as e:
            logger.error(f"Error parsing JSON response: {e}")
            logger.exception("Full exception details:")
            break
        except Exception as e:
            logger.error(f"Unexpected error processing data: {e}")
            logger.exception("Full exception details:")
            break

    logger.info(f"Completed surge alert data fetch. Total pages: {page_count}, Created: {total_created}, Updated: {total_updated}")

    # Update the API status
    api_status, created = ApiStatus.objects.update_or_create(
        name='surge_alerts',
        defaults={'last_run': timezone.now()}
    )
    logger.info(f"Updated API status: {api_status}")

    return {'created': total_created, 'updated': total_updated}


def process_results(results):
    """
    Process the results from the API and save to the database.
    """
    logger.debug(f"Processing {len(results)} results")

    for i, item in enumerate(results):
        logger.debug(f"Processing item {i+1}/{len(results)} with ID: {item.get('id')}")
        with transaction.atomic():
            try:
                # Process country data if present
                country_obj = None
                if item.get('country'):
                    logger.debug(f"Processing country data for item ID: {item.get('id')}")
                    country_obj = process_country(item['country'])
                else:
                    logger.debug(f"No country data for item ID: {item.get('id')}")

                # Process surge alert
                process_surge_alert(item, country_obj)

            except Exception as e:
                logger.error(f"Error processing item {item.get('id')}: {e}")
                logger.exception("Full exception details:")


def process_country(country_data):
    """
    Process country data and return the Country object.
    """
    if not country_data:
        logger.warning("Empty country data received")
        return None

    if not country_data.get('id'):
        logger.warning(f"Country data missing ID: {country_data}")
        return None

    logger.debug(f"Processing country with ID: {country_data['id']}, Name: {country_data.get('name', 'Unknown')}")

    try:
        country, created = Country.objects.update_or_create(
            api_id=country_data['id'],
            defaults={
                'iso': country_data.get('iso'),
                'iso3': country_data.get('iso3'),
                'record_type': country_data.get('record_type'),
                'record_type_display': country_data.get('record_type_display'),
                'region': country_data.get('region'),
                'independent': country_data.get('independent', True),
                'is_deprecated': country_data.get('is_deprecated', False),
                'fdrs': country_data.get('fdrs'),
                'average_household_size': country_data.get('average_household_size'),
                'society_name': country_data.get('society_name'),
                'name': country_data.get('name', 'Unknown'),
                'translation_module_original_language': country_data.get('translation_module_original_language')
            }
        )

        if created:
            logger.info(f"Created new country: {country.name} (ID: {country.api_id})")
        else:
            logger.debug(f"Updated existing country: {country.name} (ID: {country.api_id})")

        return country
    except Exception as e:
        logger.error(f"Error processing country with ID {country_data['id']}: {e}")
        logger.exception("Full exception details:")
        return None


def process_surge_alert(alert_data, country_obj):
    """
    Process surge alert data and save to the database.
    """
    if not alert_data:
        logger.warning("Empty surge alert data received")
        return None

    if not alert_data.get('id'):
        logger.warning(f"Surge alert data missing ID: {alert_data}")
        return None

    logger.debug(f"Processing surge alert with ID: {alert_data['id']}")

    try:
        # Check if alert exists
        try:
            alert = SurgeAlert.objects.get(api_id=alert_data['id'])
            created = False
            logger.debug(f"Found existing surge alert with ID: {alert_data['id']}")
        except SurgeAlert.DoesNotExist:
            alert = SurgeAlert(api_id=alert_data['id'])
            created = True
            logger.debug(f"Creating new surge alert with ID: {alert_data['id']}")

        # Update alert fields
        alert.country = country_obj
        if country_obj:
            logger.debug(f"Associating surge alert {alert_data['id']} with country: {country_obj.name}")
        else:
            logger.debug(f"No country associated with surge alert {alert_data['id']}")

        alert.deployment_needed = alert_data.get('deployment_needed', False)
        alert.is_private = alert_data.get('is_private', False)

        # Handle event field which can be either a number or a complex object
        event = alert_data.get('event')
        if isinstance(event, dict):
            # If event is a dictionary, try to extract the id
            alert.event = event.get('id') if event else None
            logger.debug(f"Extracted event ID {alert.event} from event object for surge alert {alert_data['id']}")
        else:
            # Otherwise use the value directly
            alert.event = event
            logger.debug(f"Using direct event value {alert.event} for surge alert {alert_data['id']}")

        # Parse datetime fields
        for field_name in ['created_at', 'opens', 'closes', 'start', 'end']:
            field_value = alert_data.get(field_name)
            if field_value:
                logger.debug(f"Parsing datetime for field {field_name}: {field_value}")
            parsed_value = parse_datetime(field_value)
            setattr(alert, field_name, parsed_value)

        # Set other fields
        alert.atype = alert_data.get('atype')
        alert.atype_display = alert_data.get('atype_display')
        alert.category = alert_data.get('category')
        alert.category_display = alert_data.get('category_display')
        alert.molnix_id = alert_data.get('molnix_id')
        alert.molnix_status = alert_data.get('molnix_status')
        alert.molnix_status_display = alert_data.get('molnix_status_display')
        alert.message = alert_data.get('message')
        alert.operation = alert_data.get('operation')
        alert.translation_module_original_language = alert_data.get('translation_module_original_language')

        logger.debug(f"Saving surge alert with ID: {alert_data['id']}")
        alert.save()

        # Process molnix tags
        if alert_data.get('molnix_tags'):
            logger.debug(f"Processing {len(alert_data['molnix_tags'])} molnix tags for surge alert {alert_data['id']}")
            process_molnix_tags(alert, alert_data['molnix_tags'])
        else:
            logger.debug(f"No molnix tags for surge alert {alert_data['id']}")

        # Mark if created or updated for reporting
        alert_data['_created'] = created
        alert_data['_updated'] = not created

        if created:
            logger.info(f"Created new surge alert: {alert.api_id}, Type: {alert.atype_display}, Category: {alert.category_display}")
        else:
            logger.info(f"Updated surge alert: {alert.api_id}, Type: {alert.atype_display}, Category: {alert.category_display}")

        return alert
    except Exception as e:
        logger.error(f"Error processing surge alert with ID {alert_data.get('id')}: {e}")
        logger.exception("Full exception details:")
        return None


def process_molnix_tags(alert, tags_data):
    """
    Process molnix tags data and associate with the surge alert.
    """
    if not tags_data:
        logger.debug(f"No tags data provided for alert ID: {alert.api_id}")
        return

    logger.debug(f"Processing {len(tags_data)} molnix tags for alert ID: {alert.api_id}")

    # Clear existing tags
    logger.debug(f"Clearing existing tags for alert ID: {alert.api_id}")
    alert.molnix_tags.clear()

    for i, tag_data in enumerate(tags_data):
        if not tag_data:
            logger.warning(f"Empty tag data at index {i} for alert ID: {alert.api_id}")
            continue

        if not tag_data.get('id'):
            logger.warning(f"Tag data missing ID at index {i} for alert ID: {alert.api_id}: {tag_data}")
            continue

        logger.debug(f"Processing tag {i+1}/{len(tags_data)} with ID: {tag_data['id']} for alert ID: {alert.api_id}")

        try:
            tag, created = MolnixTag.objects.update_or_create(
                api_id=tag_data['id'],
                defaults={
                    'molnix_id': tag_data.get('molnix_id'),
                    'name': tag_data.get('name', 'Unknown'),
                    'description': tag_data.get('description'),
                    'color': tag_data.get('color'),
                    'tag_type': tag_data.get('tag_type'),
                    'groups': tag_data.get('groups', [])
                }
            )

            if created:
                logger.info(f"Created new molnix tag: {tag.name} (ID: {tag.api_id})")
            else:
                logger.debug(f"Updated existing molnix tag: {tag.name} (ID: {tag.api_id})")

            # Add tag to alert
            logger.debug(f"Adding tag {tag.name} to alert ID: {alert.api_id}")
            alert.molnix_tags.add(tag)
        except Exception as e:
            logger.error(f"Error processing molnix tag with ID {tag_data.get('id')} for alert ID {alert.api_id}: {e}")
            logger.exception("Full exception details:")


def parse_datetime(dt_str):
    """
    Parse datetime string from API to Python datetime object.
    """
    if not dt_str:
        logger.debug("Empty datetime string received")
        return None

    try:
        logger.debug(f"Parsing datetime string: {dt_str}")
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except (ValueError, TypeError) as e:
        logger.warning(f"Could not parse datetime: {dt_str}, Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing datetime {dt_str}: {e}")
        logger.exception("Full exception details:")
        return None
