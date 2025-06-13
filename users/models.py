"""
Models for the users app.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from surge.models import Country, MolnixTag


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
    languages = models.ManyToManyField(Language, blank=True)
    preferred_regions = models.ManyToManyField(Region, blank=True, related_name='preferred_by_users')
    restricted_countries = models.ManyToManyField(Country, blank=True, related_name='restricted_for_users')
    qualified_profiles = models.ManyToManyField(MolnixTag, blank=True, limit_choices_to={'tag_type': 'regular'})
    rotation_availability = models.CharField(max_length=10, choices=ROTATION_CHOICES, default='any')
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
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