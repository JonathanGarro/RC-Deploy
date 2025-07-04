from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import ScheduledTask
from surge.tasks import fetch_surge_alerts

@staff_member_required
def run_task(request, task_id):
    """
    View to manually run a scheduled task.
    Currently only supports the fetch_surge_alerts task.
    """
    task = get_object_or_404(ScheduledTask, id=task_id)

    if task.task == 'surge.tasks.fetch_surge_alerts':
        try:
            result = fetch_surge_alerts()
            messages.success(
                request, 
                f'Successfully ran task "{task.name}". Created: {result["created"]}, Updated: {result["updated"]}'
            )
        except Exception as e:
            messages.error(request, f'Error running task "{task.name}": {str(e)}')
    else:
        messages.warning(request, f'Manual execution not supported for task "{task.name}"')

    # Redirect back to the admin page
    return HttpResponseRedirect(reverse('admin:scheduler_scheduledtask_changelist'))
