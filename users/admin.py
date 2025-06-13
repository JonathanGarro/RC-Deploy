"""
Admin configuration for the users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Language, Region, UserProfile


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    filter_horizontal = ('languages', 'preferred_regions', 'restricted_countries', 'qualified_profiles')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_languages')
    
    def get_languages(self, obj):
        return ", ".join([lang.name for lang in obj.profile.languages.all()])
    get_languages.short_description = 'Languages'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)