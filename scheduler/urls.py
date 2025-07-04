from django.urls import path
from . import views

app_name = 'scheduler'

urlpatterns = [
    path('run-task/<int:task_id>/', views.run_task, name='run_task'),
]