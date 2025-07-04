"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('surge/', include('surge.urls', namespace='surge')),
    path('scheduler/', include('scheduler.urls', namespace='scheduler')),
    # User app URLs
    path('users/', include('users.urls', namespace='users')),
    # Redirect root URL to surge alerts list
    path('', RedirectView.as_view(pattern_name='surge:alert_list', permanent=False)),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Also serve from STATICFILES_DIRS for development
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
