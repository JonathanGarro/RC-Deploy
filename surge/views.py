"""
Views for the surge app.
"""
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import SurgeAlert, Country, MolnixTag


class SurgeAlertListView(ListView):
    """
    View to display a list of surge alerts.
    """
    model = SurgeAlert
    template_name = 'surge/surge_alert_list.html'
    context_object_name = 'alerts'
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Get the list of items for this view.
        Filter by country, status, or tag if provided in GET parameters.
        """
        queryset = super().get_queryset()
        
        # Filter by country if provided
        country_id = self.request.GET.get('country')
        if country_id:
            queryset = queryset.filter(country__api_id=country_id)
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(molnix_status_display=status)
        
        # Filter by tag if provided
        tag_id = self.request.GET.get('tag')
        if tag_id:
            queryset = queryset.filter(molnix_tags__api_id=tag_id)
        
        return queryset

    def get_context_data(self, **kwargs):
        """
        Add countries and statuses to context for filtering.
        """
        context = super().get_context_data(**kwargs)
        context['countries'] = Country.objects.all().order_by('name')
        context['statuses'] = SurgeAlert.objects.values_list(
            'molnix_status_display', flat=True
        ).distinct().order_by('molnix_status_display')
        context['tags'] = MolnixTag.objects.all().order_by('name')
        return context


class SurgeAlertDetailView(DetailView):
    """
    View to display details of a surge alert.
    """
    model = SurgeAlert
    template_name = 'surge/surge_alert_detail.html'
    context_object_name = 'alert'
    
    def get_object(self, queryset=None):
        """
        Get the object this view is displaying.
        Use the api_id from the URL instead of the primary key.
        """
        if queryset is None:
            queryset = self.get_queryset()
        
        api_id = self.kwargs.get('api_id')
        return queryset.get(api_id=api_id)