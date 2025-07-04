"""
Management command to fetch airport data from a CSV file and populate the Airport model.
"""
import logging
import requests
import csv
import io
from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import Airport
from surge.models import Country

logger = logging.getLogger(__name__)

# CSV file URL for airport data
AIRPORT_CSV_URL = "https://raw.githubusercontent.com/lxndrblz/Airports/main/airports.csv"

# For debugging
print(f"Using CSV URL: {AIRPORT_CSV_URL}")

class Command(BaseCommand):
    help = 'Fetch airport data from a CSV file and populate the Airport model'

    def handle(self, *args, **options):
        self.stdout.write('Starting to fetch airport data...')

        # Check if countries exist in the database
        from surge.models import Country
        countries_count = Country.objects.count()
        self.stdout.write(f'Total countries in database: {countries_count}')

        if countries_count > 0:
            # Get a sample of countries to see what ISO codes they have
            sample_countries = Country.objects.all()[:5]
            for c in sample_countries:
                self.stdout.write(f'Sample country: {c.name}, ISO: {c.iso}, ISO3: {c.iso3}')
        else:
            self.stdout.write(self.style.WARNING('No countries found in the database. Please populate the Country model first.'))
            return

        # First, let's check if DCA already exists
        from users.models import Airport
        dca = Airport.objects.filter(iata_code='DCA').first()
        if dca:
            self.stdout.write(f"DCA already exists in the database: {dca}")
        else:
            self.stdout.write("DCA not found in the database, creating it...")
            # Create the US country if it doesn't exist
            us_country = Country.objects.filter(iso='US').first()
            if not us_country:
                self.stdout.write("Creating US country...")
                us_country = Country.objects.create(
                    name='United States',
                    iso='US',
                    iso3='USA',
                    api_id=-999  # Use a unique negative ID
                )
                self.stdout.write(self.style.SUCCESS(f"Created US country: {us_country}"))

            # Create the DCA airport
            dca = Airport.objects.create(
                iata_code='DCA',
                name='Ronald Reagan National Airport',
                city='Washington',
                country=us_country
            )
            self.stdout.write(self.style.SUCCESS(f"Created DCA airport: {dca}"))

        # Call the function to fetch and process airport data
        result = fetch_airports(self)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully fetched airport data. Created: {result["created"]}, Updated: {result["updated"]}, Skipped: {result["skipped"]}'
        ))

def fetch_airports(command=None):
    """
    Fetch airport data from the CSV file and store it in the database.

    Args:
        command: The Command instance, used for writing to stdout
    """
    logger.info("Starting airport data fetch")
    logger.debug(f"Using CSV URL: {AIRPORT_CSV_URL}")

    total_created = 0
    total_updated = 0
    total_skipped = 0

    try:
        logger.debug(f"Sending GET request to: {AIRPORT_CSV_URL}")
        response = requests.get(AIRPORT_CSV_URL)
        response.raise_for_status()

        logger.debug(f"Received response with status code: {response.status_code}")

        # Parse CSV data
        csv_data = io.StringIO(response.text)

        # For debugging, print the first 10 lines of the CSV file
        print("First 10 lines of CSV file:")
        csv_lines = response.text.splitlines()[:10]
        for i, line in enumerate(csv_lines):
            print(f"{i}: {line}")

        # Check if DCA is in the CSV file
        dca_line = None
        for i, line in enumerate(response.text.splitlines()):
            if "DCA" in line:
                dca_line = line
                print(f"Found DCA in CSV at line {i}: {line}")
                break
        if not dca_line:
            print("DCA not found in CSV file!")

        # Reset the CSV data for parsing
        csv_data = io.StringIO(response.text)
        reader = csv.DictReader(csv_data)
        airports = list(reader)

        logger.info(f"Retrieved {len(airports)} airports from CSV")

        if command:
            command.stdout.write(f"Retrieved {len(airports)} airports from CSV")

        # Check if DCA is in the list of airports
        dca_airports = [a for a in airports if a.get('code') == 'DCA']
        if dca_airports:
            logger.info(f"Found DCA in airports list: {dca_airports}")
            if command:
                command.stdout.write(f"Found DCA in airports list: {dca_airports}")
        else:
            logger.warning("DCA not found in airports list!")
            if command:
                command.stdout.write(command.style.WARNING("DCA not found in airports list!"))

            # Print a sample of the data to understand its structure
            if airports:
                command.stdout.write("Sample of airport data:")
                for i, airport in enumerate(airports[:5]):
                    command.stdout.write(f"  Row {i+1}: {airport}")

        # Process the results
        for airport_data in airports:
            # Get the IATA code from the data (in the 'code' column)
            iata_code = airport_data.get('code', '')

            # Special handling for DCA to debug
            if iata_code == 'DCA':
                if command:
                    command.stdout.write(f"Found DCA in CSV: {airport_data}")
                logger.info(f"Found DCA in CSV: {airport_data}")
                # Force processing of DCA
                logger.info("Forcing processing of DCA")
                if command:
                    command.stdout.write("Forcing processing of DCA")
                result = process_airport(iata_code, airport_data, command)
                if result == 'created':
                    total_created += 1
                    logger.info("DCA was created")
                    if command:
                        command.stdout.write(command.style.SUCCESS("DCA was created"))
                elif result == 'updated':
                    total_updated += 1
                    logger.info("DCA was updated")
                    if command:
                        command.stdout.write(command.style.SUCCESS("DCA was updated"))
                else:
                    total_skipped += 1
                    logger.warning("DCA was skipped")
                    if command:
                        command.stdout.write(command.style.WARNING("DCA was skipped"))
                continue

            # Skip airports without IATA code or with invalid IATA code
            if not iata_code or len(iata_code) != 3 or not iata_code.isalpha() or not iata_code.isupper():
                logger.debug(f"Skipping airport with invalid IATA code: {iata_code}")
                if command:
                    command.stdout.write(f"Skipping airport with invalid IATA code: {iata_code}")
                total_skipped += 1
                continue

            # Process the airport
            result = process_airport(iata_code, airport_data, command)
            if result == 'created':
                total_created += 1
            elif result == 'updated':
                total_updated += 1
            else:
                total_skipped += 1

        logger.info(f"Completed airport data fetch. Created: {total_created}, Updated: {total_updated}, Skipped: {total_skipped}")

    except requests.RequestException as e:
        logger.error(f"Error fetching data from API: {e}")
        logger.exception("Full exception details:")
    except ValueError as e:
        logger.error(f"Error parsing JSON response: {e}")
        logger.exception("Full exception details:")
    except Exception as e:
        logger.error(f"Unexpected error processing data: {e}")
        logger.exception("Full exception details:")

    return {'created': total_created, 'updated': total_updated, 'skipped': total_skipped}

def process_airport(iata_code, airport_data, command=None):
    """
    Process airport data and save to the database.

    Args:
        iata_code: The IATA code of the airport
        airport_data: The data for the airport (CSV row)
        command: The Command instance, used for writing to stdout
    """
    # Special handling for DCA to debug
    if iata_code == 'DCA':
        logger.info(f"Processing DCA airport: {airport_data}")
        if command:
            command.stdout.write(f"Processing DCA airport: {airport_data}")
    if not airport_data:
        logger.warning(f"Empty airport data received for IATA code: {iata_code}")
        return 'skipped'

    # Get airport name and city from CSV data
    airport_name = airport_data.get('name', 'Unknown')
    city_name = airport_data.get('city', 'Unknown')

    logger.debug(f"Processing airport with IATA code: {iata_code}, Name: {airport_name}")

    try:
        # Get country by ISO code (in the 'country' field)
        country_code = airport_data.get('country')
        country_name = country_code  # In CSV, we only have the country code

        if command:
            command.stdout.write(f"Processing airport: {iata_code}, Name: {airport_name}")
            command.stdout.write(f"  Country code: {country_code}, City: {city_name}")

        if not country_code:
            logger.warning(f"No country code for airport with IATA code: {iata_code}")
            if command:
                command.stdout.write(command.style.WARNING(f"  No country code for airport: {iata_code}"))
            return 'skipped'

        # Try to find country by iso or iso3
        country = None
        if len(country_code) == 2:
            country = Country.objects.filter(iso=country_code).first()
            if command and country:
                command.stdout.write(f"  Found country by ISO: {country.name}")
        elif len(country_code) == 3:
            country = Country.objects.filter(iso3=country_code).first()
            if command and country:
                command.stdout.write(f"  Found country by ISO3: {country.name}")

        # If we couldn't find by ISO, try by name
        if not country and country_name:
            # Try to find a country with a similar name
            country = Country.objects.filter(name__icontains=country_name).first()
            if command and country:
                command.stdout.write(f"  Found country by name: {country.name}")

        # If we still couldn't find a country, try a hardcoded mapping for common countries
        if not country:
            # Map of common country codes to names in our database
            country_map = {
                'US': 'United States of America',
                'GB': 'United Kingdom',
                'CA': 'Canada',
                'AU': 'Australia',
                'FR': 'France',
                'DE': 'Germany',
                'JP': 'Japan',
                'CN': 'China',
                'IN': 'India',
                'BR': 'Brazil',
                'RU': 'Russian Federation',
                'IT': 'Italy',
                'ES': 'Spain',
                'MX': 'Mexico',
            }

            if country_code in country_map:
                country = Country.objects.filter(name__icontains=country_map[country_code]).first()
                if command and country:
                    command.stdout.write(f"  Found country by mapping: {country.name}")

        if not country:
            # Create a new country if it doesn't exist
            logger.warning(f"Could not find country with code: {country_code} for airport: {iata_code}, creating it")
            if command:
                command.stdout.write(command.style.WARNING(f"  Could not find country with code: {country_code} for airport: {iata_code}, creating it"))

            # Use a better name for common country codes
            better_country_map = {
                'US': 'United States',
                'GB': 'United Kingdom',
                'CA': 'Canada',
                'AU': 'Australia',
                'FR': 'France',
                'DE': 'Germany',
                'JP': 'Japan',
                'CN': 'China',
                'IN': 'India',
                'BR': 'Brazil',
                'RU': 'Russian Federation',
                'IT': 'Italy',
                'ES': 'Spain',
                'MX': 'Mexico',
                'NL': 'Netherlands',
                'CH': 'Switzerland',
                'SE': 'Sweden',
                'NO': 'Norway',
                'DK': 'Denmark',
                'FI': 'Finland',
                'IE': 'Ireland',
                'NZ': 'New Zealand',
                'SG': 'Singapore',
                'AE': 'United Arab Emirates',
                'SA': 'Saudi Arabia',
                'ZA': 'South Africa',
                'AR': 'Argentina',
                'CL': 'Chile',
                'CO': 'Colombia',
                'PE': 'Peru',
                'VE': 'Venezuela',
                'TH': 'Thailand',
                'MY': 'Malaysia',
                'ID': 'Indonesia',
                'PH': 'Philippines',
                'VN': 'Vietnam',
                'TR': 'Turkey',
                'IL': 'Israel',
                'EG': 'Egypt',
                'MA': 'Morocco',
                'NG': 'Nigeria',
                'KE': 'Kenya',
                'GH': 'Ghana',
                'TZ': 'Tanzania',
                'UG': 'Uganda',
                'ET': 'Ethiopia',
                'ZW': 'Zimbabwe',
                'ZM': 'Zambia',
                'MZ': 'Mozambique',
                'NA': 'Namibia',
                'BW': 'Botswana',
                'SN': 'Senegal',
                'CI': 'Ivory Coast',
                'CM': 'Cameroon',
                'GN': 'Guinea',
                'ML': 'Mali',
                'BF': 'Burkina Faso',
                'NE': 'Niger',
                'TD': 'Chad',
                'SD': 'Sudan',
                'ER': 'Eritrea',
                'DJ': 'Djibouti',
                'SO': 'Somalia',
                'KR': 'South Korea',
                'KP': 'North Korea',
                'TW': 'Taiwan',
                'HK': 'Hong Kong',
                'MO': 'Macau',
                'LK': 'Sri Lanka',
                'NP': 'Nepal',
                'BD': 'Bangladesh',
                'BT': 'Bhutan',
                'MM': 'Myanmar',
                'LA': 'Laos',
                'KH': 'Cambodia',
                'PK': 'Pakistan',
                'AF': 'Afghanistan',
                'IR': 'Iran',
                'IQ': 'Iraq',
                'SY': 'Syria',
                'JO': 'Jordan',
                'LB': 'Lebanon',
                'PS': 'Palestine',
                'KW': 'Kuwait',
                'BH': 'Bahrain',
                'QA': 'Qatar',
                'OM': 'Oman',
                'YE': 'Yemen',
                'GE': 'Georgia',
                'AM': 'Armenia',
                'AZ': 'Azerbaijan',
                'KZ': 'Kazakhstan',
                'UZ': 'Uzbekistan',
                'TM': 'Turkmenistan',
                'KG': 'Kyrgyzstan',
                'TJ': 'Tajikistan',
                'MN': 'Mongolia',
                'UA': 'Ukraine',
                'BY': 'Belarus',
                'MD': 'Moldova',
                'RO': 'Romania',
                'BG': 'Bulgaria',
                'RS': 'Serbia',
                'HR': 'Croatia',
                'BA': 'Bosnia and Herzegovina',
                'ME': 'Montenegro',
                'MK': 'North Macedonia',
                'AL': 'Albania',
                'GR': 'Greece',
                'CY': 'Cyprus',
                'MT': 'Malta',
                'PT': 'Portugal',
                'LU': 'Luxembourg',
                'BE': 'Belgium',
                'IS': 'Iceland',
                'LI': 'Liechtenstein',
                'AD': 'Andorra',
                'MC': 'Monaco',
                'SM': 'San Marino',
                'VA': 'Vatican City',
                'PL': 'Poland',
                'CZ': 'Czech Republic',
                'SK': 'Slovakia',
                'HU': 'Hungary',
                'SI': 'Slovenia',
                'EE': 'Estonia',
                'LV': 'Latvia',
                'LT': 'Lithuania',
            }

            # Use the better name if available, otherwise use the country code
            country_name = better_country_map.get(country_code, country_code)

            # Create the country with a unique negative api_id based on the country code
            # Convert the country code to a number (sum of ASCII values) and make it negative
            unique_api_id = -sum(ord(c) for c in country_code)

            # Check if this api_id is already used
            while Country.objects.filter(api_id=unique_api_id).exists():
                unique_api_id -= 1

            country = Country.objects.create(
                name=country_name,
                iso=country_code if len(country_code) == 2 else None,
                iso3=country_code if len(country_code) == 3 else None,
                api_id=unique_api_id
            )
            logger.info(f"Created new country: {country.name} (ISO: {country.iso}, ISO3: {country.iso3})")
            if command:
                command.stdout.write(command.style.SUCCESS(f"  Created new country: {country.name}"))

        # Create or update airport
        airport, created = Airport.objects.update_or_create(
            iata_code=iata_code,
            defaults={
                'name': airport_name,
                'city': city_name,
                'country': country,
            }
        )

        if created:
            logger.info(f"Created new airport: {airport.name} ({airport.iata_code})")
            return 'created'
        else:
            logger.debug(f"Updated existing airport: {airport.name} ({airport.iata_code})")
            return 'updated'

    except Exception as e:
        logger.error(f"Error processing airport with IATA code {iata_code}: {e}")
        logger.exception("Full exception details:")
        return 'skipped'
