"""
Models for the users app.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from surge.models import Country, MolnixTag, SurgeAlert
from django.core.validators import RegexValidator


class Language(models.Model):
    """
    Model to store language information.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Region(models.Model):
    """
    Model to store region information.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class Airport(models.Model):
    """
    Model to store airport information.
    """
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    iata_code = models.CharField(max_length=3, unique=True, validators=[
        RegexValidator(
            regex=r'^[A-Z]{3}$',
            message='IATA code must be 3 uppercase letters',
        )
    ])

    def __str__(self):
        return f"{self.name} ({self.iata_code})"


class LanguageProficiency(models.Model):
    """
    Model to store language proficiency levels for users.
    """
    PROFICIENCY_CHOICES = [
        ('native', 'Native'),
        ('expert', 'Expert'),
        ('intermediate', 'Intermediate'),
        ('beginner', 'Beginner'),
    ]

    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='language_proficiencies')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES)

    class Meta:
        unique_together = ('user_profile', 'language')
        verbose_name_plural = 'Language Proficiencies'

    def __str__(self):
        return f"{self.user_profile.user.username}'s {self.language.name} proficiency: {self.proficiency}"


class UserProfile(models.Model):
    """
    Model to store user profile information.
    """
    ROTATION_CHOICES = [
        ('any', 'Any Rotation'),
        ('first', 'First Rotation'),
        ('second', 'Second Rotation'),
        ('third', 'Third Rotation'),
        ('fourth', 'Fourth Rotation'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Languages are now handled through the LanguageProficiency model
    preferred_regions = models.ManyToManyField(Region, blank=True, related_name='preferred_by_users')
    restricted_countries = models.ManyToManyField(Country, blank=True, related_name='restricted_for_users')
    qualified_profiles = models.ManyToManyField(MolnixTag, blank=True, limit_choices_to={'tag_type': 'regular'})
    saved_alerts = models.ManyToManyField(SurgeAlert, blank=True, related_name='saved_by_users')
    rotation_availability = models.CharField(max_length=10, choices=ROTATION_CHOICES, default='any')
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    accept_sms = models.BooleanField(default=False, help_text="Check if you accept SMS messages")
    closest_airport = models.ForeignKey(Airport, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Signal to create a user profile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
