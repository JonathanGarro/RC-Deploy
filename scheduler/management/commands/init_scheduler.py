"""
Management command to initialize the scheduler with default tasks.
"""
from django.core.management.base import BaseCommand
from scheduler.models import ScheduledTask
from surge.celery import CELERYBEAT_SCHEDULE


class Command(BaseCommand):
    help = 'Initialize the scheduler with default tasks'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to initialize scheduler...'))

        # Get the default tasks from the CELERYBEAT_SCHEDULE
        default_tasks = CELERYBEAT_SCHEDULE

        # Create a task for each entry in the default schedule
        for name, config in default_tasks.items():
            task_name = name.replace('-', ' ').title()
            task_path = config['task']

            # Check if the task already exists
            if ScheduledTask.objects.filter(name=task_name).exists():
                self.stdout.write(self.style.WARNING(f'Task {task_name} already exists, skipping...'))
                continue

            # Create the task
            schedule = config.get('schedule')

            # Create a new ScheduledTask
            task = ScheduledTask(
                name=task_name,
                task=task_path,
                enabled=True
            )

            # Set the schedule based on the type
            if hasattr(schedule, 'run_every'):
                # This is an interval schedule
                task.schedule_type = 'interval'

                # Convert timedelta to seconds
                seconds = schedule.run_every.total_seconds()

                # Set the interval fields
                days, remainder = divmod(seconds, 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes, seconds = divmod(remainder, 60)

                if days > 0:
                    task.interval_days = int(days)
                if hours > 0:
                    task.interval_hours = int(hours)
                if minutes > 0:
                    task.interval_minutes = int(minutes)
                if seconds > 0:
                    task.interval_seconds = int(seconds)
            else:
                # This is a crontab schedule
                task.schedule_type = 'crontab'

                # Ensure crontab values are not too long (max 64 chars)
                task.crontab_minute = str(getattr(schedule, 'minute', '*'))[:64]
                task.crontab_hour = str(getattr(schedule, 'hour', '*'))[:64]
                task.crontab_day_of_week = str(getattr(schedule, 'day_of_week', '*'))[:64]
                task.crontab_day_of_month = str(getattr(schedule, 'day_of_month', '*'))[:64]
                task.crontab_month_of_year = str(getattr(schedule, 'month_of_year', '*'))[:64]

                self.stdout.write(self.style.WARNING(
                    f'Crontab values: {task.crontab_minute} {task.crontab_hour} {task.crontab_day_of_month} '
                    f'{task.crontab_month_of_year} {task.crontab_day_of_week}'
                ))

            # Save the task
            task.save()
            self.stdout.write(self.style.SUCCESS(f'Created task {task_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully initialized scheduler'))
