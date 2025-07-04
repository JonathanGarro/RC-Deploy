from django.db import models
from django.core.validators import MinValueValidator

class ScheduledTask(models.Model):
    """
    Model to store configuration for scheduled tasks.
    """
    TASK_CHOICES = [
        ('surge.tasks.fetch_surge_alerts', 'Fetch Surge Alerts'),
    ]

    SCHEDULE_TYPE_CHOICES = [
        ('interval', 'Interval'),
        ('crontab', 'Crontab'),
    ]

    name = models.CharField(max_length=255, unique=True)
    task = models.CharField(max_length=255, choices=TASK_CHOICES)
    enabled = models.BooleanField(default=True)

    # Schedule type
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPE_CHOICES, default='interval')

    # Interval schedule fields
    interval_seconds = models.IntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(1)],
        help_text="Interval in seconds"
    )
    interval_minutes = models.IntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(1)],
        help_text="Interval in minutes"
    )
    interval_hours = models.IntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(1)],
        help_text="Interval in hours"
    )
    interval_days = models.IntegerField(
        null=True, blank=True, 
        validators=[MinValueValidator(1)],
        help_text="Interval in days"
    )

    # Crontab schedule fields
    crontab_minute = models.CharField(
        max_length=64, null=True, blank=True, 
        default='*',
        help_text="Crontab minute (0-59, '*', '*/15', etc.)"
    )
    crontab_hour = models.CharField(
        max_length=64, null=True, blank=True, 
        default='*',
        help_text="Crontab hour (0-23, '*', '*/2', etc.)"
    )
    crontab_day_of_week = models.CharField(
        max_length=64, null=True, blank=True, 
        default='*',
        help_text="Crontab day of week (0-6 or mon,tue,wed,thu,fri,sat,sun)"
    )
    crontab_day_of_month = models.CharField(
        max_length=64, null=True, blank=True, 
        default='*',
        help_text="Crontab day of month (1-31, '*', etc.)"
    )
    crontab_month_of_year = models.CharField(
        max_length=64, null=True, blank=True, 
        default='*',
        help_text="Crontab month of year (1-12, jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,dec)"
    )

    # Last run information
    last_run_at = models.DateTimeField(null=True, blank=True)
    total_run_count = models.PositiveIntegerField(default=0)

    # Metadata
    date_created = models.DateTimeField(auto_now_add=True)
    date_changed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Scheduled Task"
        verbose_name_plural = "Scheduled Tasks"
        ordering = ['name']
