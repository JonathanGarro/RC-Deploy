"""
Management command to populate initial data for languages and regions.
"""
import logging
from django.core.management.base import BaseCommand
from users.models import Language, Region

logger = logging.getLogger(__name__)

LANGUAGES = [
    {'name': 'English', 'code': 'en'},
    {'name': 'Spanish', 'code': 'es'},
    {'name': 'French', 'code': 'fr'},
    {'name': 'Arabic', 'code': 'ar'},
    {'name': 'Russian', 'code': 'ru'},
    {'name': 'Chinese', 'code': 'zh'},
    {'name': 'Portuguese', 'code': 'pt'},
]

REGIONS = [
    {'name': 'Africa', 'code': 'AF'},
    {'name': 'Americas', 'code': 'AM'},
    {'name': 'Asia Pacific', 'code': 'AP'},
    {'name': 'Europe', 'code': 'EU'},
    {'name': 'Middle East and North Africa', 'code': 'MENA'},
]


class Command(BaseCommand):
    help = 'Populate initial data for languages and regions'

    def handle(self, *args, **options):
        self.stdout.write('Populating initial data...')
        
        # Populate languages
        for lang_data in LANGUAGES:
            language, created = Language.objects.get_or_create(
                code=lang_data['code'],
                defaults={'name': lang_data['name']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created language: {language.name}'))
            else:
                self.stdout.write(f'Language already exists: {language.name}')
        
        # Populate regions
        for region_data in REGIONS:
            region, created = Region.objects.get_or_create(
                code=region_data['code'],
                defaults={'name': region_data['name']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created region: {region.name}'))
            else:
                self.stdout.write(f'Region already exists: {region.name}')
        
        self.stdout.write(self.style.SUCCESS('Initial data population completed!'))