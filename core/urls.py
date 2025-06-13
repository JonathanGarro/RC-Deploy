"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('surge/', include('surge.urls', namespace='surge')),
    # Add user app URLs when they are created
    # path('users/', include('users.urls')),
    # Redirect root URL to surge alerts list
    path('', RedirectView.as_view(pattern_name='surge:alert_list', permanent=False)),
]
