from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ScheduledTask

@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'task', 'schedule_display', 'enabled', 'last_run_at', 'total_run_count', 'run_now_button')
    list_filter = ('enabled', 'task', 'schedule_type')
    search_fields = ('name', 'task')
    readonly_fields = ('last_run_at', 'total_run_count', 'date_created', 'date_changed')
    fieldsets = (
        (None, {
            'fields': ('name', 'task', 'enabled')
        }),
        ('Schedule', {
            'fields': ('schedule_type',),
            'description': 'Choose the type of schedule for this task.'
        }),
        ('Interval Schedule', {
            'fields': ('interval_days', 'interval_hours', 'interval_minutes', 'interval_seconds'),
            'classes': ('collapse',),
            'description': 'Set the interval at which this task should run. Only used if Schedule Type is "Interval".'
        }),
        ('Crontab Schedule', {
            'fields': ('crontab_minute', 'crontab_hour', 'crontab_day_of_week', 'crontab_day_of_month', 'crontab_month_of_year'),
            'classes': ('collapse',),
            'description': 'Set the crontab schedule for this task. Only used if Schedule Type is "Crontab".'
        }),
        ('Run Information', {
            'fields': ('last_run_at', 'total_run_count'),
            'classes': ('collapse',),
            'description': 'Information about when this task was last run.'
        }),
        ('Metadata', {
            'fields': ('date_created', 'date_changed'),
            'classes': ('collapse',),
            'description': 'Metadata about this task.'
        }),
    )

    def schedule_display(self, obj):
        if obj.schedule_type == 'interval':
            parts = []
            if obj.interval_days:
                parts.append(f"{obj.interval_days} day(s)")
            if obj.interval_hours:
                parts.append(f"{obj.interval_hours} hour(s)")
            if obj.interval_minutes:
                parts.append(f"{obj.interval_minutes} minute(s)")
            if obj.interval_seconds:
                parts.append(f"{obj.interval_seconds} second(s)")
            return ", ".join(parts) if parts else "No interval set"
        elif obj.schedule_type == 'crontab':
            return f"{obj.crontab_minute} {obj.crontab_hour} {obj.crontab_day_of_month} {obj.crontab_month_of_year} {obj.crontab_day_of_week}"
        return "Unknown schedule type"

    schedule_display.short_description = "Schedule"

    def run_now_button(self, obj):
        """
        Generate a button to manually run the task.
        Only enabled for the fetch_surge_alerts task.
        """
        if obj.task == 'surge.tasks.fetch_surge_alerts':
            url = reverse('scheduler:run_task', args=[obj.id])
            return format_html(
                '<a href="{}" class="button" style="background-color: #79aec8; padding: 5px 10px; '
                'color: white; text-decoration: none; border-radius: 4px;">Run Now</a>',
                url
            )
        return "-"

    run_now_button.short_description = "Manual Run"
    run_now_button.allow_tags = True
