"""
Context processors for the surge app.
"""
from .models import ApiStatus
from django.utils import timezone

def api_status(request):
    """
    Add API status to the template context.
    """
    try:
        surge_status = ApiStatus.objects.get(name='surge_alerts')
        last_run = surge_status.last_run
    except ApiStatus.DoesNotExist:
        last_run = None
    
    return {
        'surge_api_last_run': last_run,
    }