"""
Celery tasks for the surge app.
"""
import logging
import requests
from datetime import datetime
from django.conf import settings
from django.db import transaction
from celery import shared_task
from .models import Country, MolnixTag, SurgeAlert

logger = logging.getLogger(__name__)


@shared_task
def fetch_surge_alerts():
    """
    Fetch surge alerts from the IFRC API and store them in the database.
    Handles pagination and checks for new and updated records.
    """
    logger.info("Starting surge alert data fetch")

    url = settings.IFRC_API_URL
    next_page = url
    total_created = 0
    total_updated = 0

    while next_page:
        logger.info(f"Fetching data from: {next_page}")
        try:
            response = requests.get(next_page)
            response.raise_for_status()
            data = response.json()

            # Process the results
            results = data.get('results', [])
            process_results(results)

            # Update counters
            total_created += len([r for r in results if r.get('_created', False)])
            total_updated += len([r for r in results if r.get('_updated', False)])

            # Check for next page
            next_page = data.get('next')

        except requests.RequestException as e:
            logger.error(f"Error fetching data from API: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error processing data: {e}")
            break

    logger.info(f"Completed surge alert data fetch. Created: {total_created}, Updated: {total_updated}")
    return {'created': total_created, 'updated': total_updated}


def process_results(results):
    """
    Process the results from the API and save to the database.
    """
    for item in results:
        with transaction.atomic():
            try:
                # Process country data if present
                country_obj = None
                if item.get('country'):
                    country_obj = process_country(item['country'])

                # Process surge alert
                process_surge_alert(item, country_obj)

            except Exception as e:
                logger.error(f"Error processing item {item.get('id')}: {e}")


def process_country(country_data):
    """
    Process country data and return the Country object.
    """
    if not country_data or not country_data.get('id'):
        return None

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
        logger.info(f"Created new country: {country.name}")

    return country


def process_surge_alert(alert_data, country_obj):
    """
    Process surge alert data and save to the database.
    """
    if not alert_data or not alert_data.get('id'):
        return None

    # Check if alert exists
    try:
        alert = SurgeAlert.objects.get(api_id=alert_data['id'])
        created = False
    except SurgeAlert.DoesNotExist:
        alert = SurgeAlert(api_id=alert_data['id'])
        created = True

    # Update alert fields
    alert.country = country_obj
    alert.deployment_needed = alert_data.get('deployment_needed', False)
    alert.is_private = alert_data.get('is_private', False)

    # Handle event field which can be either a number or a complex object
    event = alert_data.get('event')
    if isinstance(event, dict):
        # If event is a dictionary, try to extract the id
        alert.event = event.get('id') if event else None
    else:
        # Otherwise use the value directly
        alert.event = event

    alert.created_at = parse_datetime(alert_data.get('created_at'))
    alert.atype = alert_data.get('atype')
    alert.atype_display = alert_data.get('atype_display')
    alert.category = alert_data.get('category')
    alert.category_display = alert_data.get('category_display')
    alert.molnix_id = alert_data.get('molnix_id')
    alert.molnix_status = alert_data.get('molnix_status')
    alert.molnix_status_display = alert_data.get('molnix_status_display')
    alert.opens = parse_datetime(alert_data.get('opens'))
    alert.closes = parse_datetime(alert_data.get('closes'))
    alert.start = parse_datetime(alert_data.get('start'))
    alert.end = parse_datetime(alert_data.get('end'))
    alert.message = alert_data.get('message')
    alert.operation = alert_data.get('operation')
    alert.translation_module_original_language = alert_data.get('translation_module_original_language')

    alert.save()

    # Process molnix tags
    if alert_data.get('molnix_tags'):
        process_molnix_tags(alert, alert_data['molnix_tags'])

    # Mark if created or updated for reporting
    alert_data['_created'] = created
    alert_data['_updated'] = not created

    if created:
        logger.info(f"Created new surge alert: {alert.api_id}")
    else:
        logger.info(f"Updated surge alert: {alert.api_id}")

    return alert


def process_molnix_tags(alert, tags_data):
    """
    Process molnix tags data and associate with the surge alert.
    """
    if not tags_data:
        return

    # Clear existing tags
    alert.molnix_tags.clear()

    for tag_data in tags_data:
        if not tag_data or not tag_data.get('id'):
            continue

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
            logger.info(f"Created new molnix tag: {tag.name}")

        # Add tag to alert
        alert.molnix_tags.add(tag)


def parse_datetime(dt_str):
    """
    Parse datetime string from API to Python datetime object.
    """
    if not dt_str:
        return None

    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        logger.warning(f"Could not parse datetime: {dt_str}")
        return None
