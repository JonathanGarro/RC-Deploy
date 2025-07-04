"""
Admin configuration for the users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Language, Region, UserProfile, Airport, LanguageProficiency


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'iata_code')
    search_fields = ('name', 'city', 'iata_code')
    list_filter = ('country',)


@admin.register(LanguageProficiency)
class LanguageProficiencyAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'language', 'proficiency')
    list_filter = ('language', 'proficiency')
    search_fields = ('user_profile__user__username', 'language__name')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    filter_horizontal = ('preferred_regions', 'restricted_countries', 'qualified_profiles')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_languages')

    def get_languages(self, obj):
        return ", ".join([f"{lang_prof.language.name} ({lang_prof.get_proficiency_display()})" 
                         for lang_prof in obj.profile.language_proficiencies.all()])
    get_languages.short_description = 'Languages'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
