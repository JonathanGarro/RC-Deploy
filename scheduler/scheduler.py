"""
Custom Celery beat scheduler that uses the database for configuration.
"""
import logging
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from celery import current_app
from celery.beat import Scheduler, ScheduleEntry
from celery.schedules import crontab, schedule
from .models import ScheduledTask

logger = logging.getLogger(__name__)

class DatabaseScheduleEntry(ScheduleEntry):
    """
    Schedule entry that wraps a ScheduledTask model instance.
    """
    def __init__(self, task):
        self.task = task
        self.app = current_app
        
        # Create the schedule based on the task's schedule_type
        self.schedule = self._make_schedule()
        
        # Set up the entry
        super().__init__(
            name=task.name,
            task=task.task,
            last_run_at=task.last_run_at,
            total_run_count=task.total_run_count,
            schedule=self.schedule,
            options={},
            app=self.app
        )
    
    def _make_schedule(self):
        """
        Create a celery.schedules.schedule or celery.schedules.crontab
        based on the task's schedule_type.
        """
        if self.task.schedule_type == 'interval':
            # Calculate the total seconds for the interval
            interval_seconds = 0
            if self.task.interval_seconds:
                interval_seconds += self.task.interval_seconds
            if self.task.interval_minutes:
                interval_seconds += self.task.interval_minutes * 60
            if self.task.interval_hours:
                interval_seconds += self.task.interval_hours * 60 * 60
            if self.task.interval_days:
                interval_seconds += self.task.interval_days * 24 * 60 * 60
            
            # Default to 1 hour if no interval is set
            if interval_seconds == 0:
                interval_seconds = 60 * 60
            
            return schedule(timedelta(seconds=interval_seconds))
        
        elif self.task.schedule_type == 'crontab':
            return crontab(
                minute=self.task.crontab_minute or '*',
                hour=self.task.crontab_hour or '*',
                day_of_week=self.task.crontab_day_of_week or '*',
                day_of_month=self.task.crontab_day_of_month or '*',
                month_of_year=self.task.crontab_month_of_year or '*'
            )
        
        # Default to hourly schedule
        return schedule(timedelta(hours=1))
    
    def is_due(self):
        """
        Check if the task is due to run.
        """
        if not self.task.enabled:
            return False, 60.0  # Not due, check again in 60 seconds
        
        return self.schedule.is_due(self.last_run_at)
    
    def __next__(self):
        """
        Return a new instance of this entry with updated last_run_at and total_run_count.
        """
        self.task.last_run_at = self.app.now()
        self.task.total_run_count += 1
        
        # Save the task to the database
        with transaction.atomic():
            self.task.save(update_fields=['last_run_at', 'total_run_count'])
        
        return self.__class__(self.task)


class DatabaseScheduler(Scheduler):
    """
    Scheduler that uses the database for configuration.
    """
    def __init__(self, *args, **kwargs):
        self.sync_every = kwargs.pop('sync_every', 60)  # Sync with DB every minute by default
        self.last_sync = None
        super().__init__(*args, **kwargs)
    
    def setup_schedule(self):
        """
        Set up the schedule from the database.
        """
        self.sync_with_database()
        self.install_default_entries(self.schedule)
        self.update_from_dict(self.app.conf.beat_schedule)
    
    def sync_with_database(self):
        """
        Sync the schedule with the database.
        """
        self.last_sync = timezone.now()
        
        # Get all enabled tasks from the database
        tasks = ScheduledTask.objects.all()
        
        # Clear the schedule
        self.schedule.clear()
        
        # Add each task to the schedule
        for task in tasks:
            entry = DatabaseScheduleEntry(task)
            self.schedule[task.name] = entry
            logger.debug(f"Added task {task.name} to schedule")
    
    def tick(self, *args, **kwargs):
        """
        Run a tick - check if we need to sync with the database.
        """
        if not self.last_sync or timezone.now() - self.last_sync > timedelta(seconds=self.sync_every):
            self.sync_with_database()
        
        return super().tick(*args, **kwargs)