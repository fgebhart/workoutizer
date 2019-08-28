import logging

from django.db import models
from django.conf import settings
from django.utils import timezone

from .tools import sanitize

log = logging.getLogger("wizer")


class Sport(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=24, unique=True)
    slug = models.CharField(max_length=24, unique=True, editable=False)
    color = models.CharField(max_length=24, unique=True)
    icon = models.CharField(max_length=24)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = sanitize(self.name)
        log.debug(f"converting name {self.name} to slug {self.slug}")
        super(Sport, self).save()


class TraceFiles(models.Model):

    def __str__(self):
        return self.file_name

    path_to_file = models.CharField(max_length=200)
    file_name = models.CharField(max_length=100, editable=False)
    md5sum = models.CharField(max_length=32, unique=True)
    center_lat = models.FloatField(max_length=20)
    center_lon = models.FloatField(max_length=20)
    zoom_level = models.IntegerField(blank=True, null=True)
    geojson = models.CharField(max_length=100000)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.file_name = self.path_to_file.split("/")[-1]
        log.debug(f"creating file name from path {self.path_to_file} -> {self.file_name}")
        super(TraceFiles, self).save()


class Activity(models.Model):

    def __str__(self):
        return f"{self.title} ({self.sport})"

    title = models.CharField(max_length=50)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True)
    date = models.DateField(blank=False, default=timezone.now)
    duration = models.IntegerField()
    distance = models.FloatField(blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    trace_file = models.ForeignKey(TraceFiles, on_delete=models.CASCADE, blank=True, null=True)


class Settings(models.Model):
    days_choices = [(365, 365), (180, 180), (30, 30), (10, 10), (5, 5)]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=settings.AUTH_USER_MODEL)
    path_to_trace_dir = models.CharField(max_length=120)
    gpx_checker_interval = models.IntegerField()
    number_of_days = models.IntegerField(choices=days_choices, default=30)
