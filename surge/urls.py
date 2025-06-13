"""
URL patterns for the surge app.
"""
from django.urls import path
from . import views

app_name = 'surge'

urlpatterns = [
    path('', views.SurgeAlertListView.as_view(), name='alert_list'),
    path('<int:api_id>/', views.SurgeAlertDetailView.as_view(), name='alert_detail'),
]