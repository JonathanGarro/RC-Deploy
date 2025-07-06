from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('airports/search/', views.search_airports, name='search_airports'),
    path('alerts/save/<int:alert_id>/', views.save_alert, name='save_alert'),
    path('alerts/remove/<int:alert_id>/', views.remove_alert, name='remove_alert'),
]
