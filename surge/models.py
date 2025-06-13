"""
Models for the surge app.
"""
from django.db import models


class Country(models.Model):
    """
    Model to store country information from the IFRC API.
    """
    iso = models.CharField(max_length=2, blank=True, null=True)
    iso3 = models.CharField(max_length=3, blank=True, null=True)
    api_id = models.IntegerField(unique=True)
    record_type = models.IntegerField(blank=True, null=True)
    record_type_display = models.CharField(max_length=100, blank=True, null=True)
    region = models.IntegerField(blank=True, null=True)
    independent = models.BooleanField(default=True)
    is_deprecated = models.BooleanField(default=False)
    fdrs = models.CharField(max_length=10, blank=True, null=True)
    average_household_size = models.FloatField(blank=True, null=True)
    society_name = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    translation_module_original_language = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class MolnixTag(models.Model):
    """
    Model to store Molnix tag information from the IFRC API.
    """
    api_id = models.IntegerField(unique=True)
    molnix_id = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    tag_type = models.CharField(max_length=50, blank=True, null=True)
    groups = models.JSONField(default=list)

    def __str__(self):
        return self.name


class SurgeAlert(models.Model):
    """
    Model to store surge alert information from the IFRC API.
    """
    api_id = models.IntegerField(unique=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    deployment_needed = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    event = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    atype = models.IntegerField(blank=True, null=True)
    atype_display = models.CharField(max_length=100, blank=True, null=True)
    category = models.IntegerField(blank=True, null=True)
    category_display = models.CharField(max_length=100, blank=True, null=True)
    molnix_id = models.IntegerField(blank=True, null=True)
    molnix_tags = models.ManyToManyField(MolnixTag, blank=True)
    molnix_status = models.IntegerField(blank=True, null=True)
    molnix_status_display = models.CharField(max_length=100, blank=True, null=True)
    opens = models.DateTimeField(blank=True, null=True)
    closes = models.DateTimeField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    operation = models.TextField(blank=True, null=True)
    translation_module_original_language = models.CharField(max_length=10, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Alert {self.api_id}: {self.message}"