"""
Admin configuration for the surge app.
"""
from django.contrib import admin
from .models import Country, MolnixTag, SurgeAlert


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'iso', 'iso3', 'api_id', 'society_name')
    search_fields = ('name', 'iso', 'iso3', 'society_name')
    list_filter = ('region', 'independent', 'is_deprecated')


@admin.register(MolnixTag)
class MolnixTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_id', 'molnix_id', 'tag_type')
    search_fields = ('name', 'description')
    list_filter = ('tag_type',)


class MolnixTagInline(admin.TabularInline):
    model = SurgeAlert.molnix_tags.through
    extra = 0


@admin.register(SurgeAlert)
class SurgeAlertAdmin(admin.ModelAdmin):
    list_display = ('api_id', 'message', 'country', 'molnix_status_display', 'created_at', 'last_updated')
    list_filter = ('molnix_status_display', 'atype_display', 'category_display', 'country')
    search_fields = ('message', 'operation')
    date_hierarchy = 'created_at'
    readonly_fields = ('last_updated',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('api_id', 'message', 'country', 'event', 'operation')
        }),
        ('Status Information', {
            'fields': ('molnix_id', 'molnix_status', 'molnix_status_display', 'atype', 'atype_display', 
                      'category', 'category_display')
        }),
        ('Dates', {
            'fields': ('created_at', 'opens', 'closes', 'start', 'end', 'last_updated')
        }),
        ('Flags', {
            'fields': ('deployment_needed', 'is_private')
        }),
        ('Other', {
            'fields': ('translation_module_original_language',)
        }),
    )
    inlines = [MolnixTagInline]
    exclude = ('molnix_tags',)