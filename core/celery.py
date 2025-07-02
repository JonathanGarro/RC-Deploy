"""
Celery configuration for core project.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure the Celery beat scheduler to use the database scheduler
app.conf.beat_scheduler = 'scheduler.scheduler.DatabaseScheduler'

# Import the default schedule as a fallback
try:
    from surge.celery import CELERYBEAT_SCHEDULE
    # Use the default schedule if no tasks are defined in the database
    app.conf.beat_schedule = CELERYBEAT_SCHEDULE
except ImportError:
    app.conf.beat_schedule = {}
