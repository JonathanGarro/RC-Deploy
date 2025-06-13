"""
Management command to fetch surge alerts from the IFRC API.
This command is intended for manual use in development.
"""
from django.core.management.base import BaseCommand
from surge.tasks import fetch_surge_alerts


class Command(BaseCommand):
    help = 'Fetch surge alerts from the IFRC API and store them in the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to fetch surge alerts...'))
        
        # Call the task directly (not as a Celery task)
        result = fetch_surge_alerts()
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully fetched surge alerts. Created: {result["created"]}, Updated: {result["updated"]}'
        ))