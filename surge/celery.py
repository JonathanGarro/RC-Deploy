"""
Celery configuration for the surge app.
"""
from celery import shared_task
from celery.schedules import crontab
from django.conf import settings

# Define the schedule for the surge alert fetching task
CELERYBEAT_SCHEDULE = {
    'fetch-surge-alerts-every-hour': {
        'task': 'surge.tasks.fetch_surge_alerts',
        'schedule': crontab(minute=0, hour='*/1'),  # Run every hour at minute 0
        'args': (),
    },
}