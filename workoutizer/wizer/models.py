import os
import logging
import datetime
import json

from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify

log = logging.getLogger(__name__)


class Sport(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=24, unique=True, verbose_name="Sport Name:")
    color = models.CharField(max_length=24, verbose_name="Color:")
    icon = models.CharField(max_length=24, verbose_name="Icon:")
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Sport, self).save(*args, **kwargs)


class Traces(models.Model):

    def __str__(self):
        return self.file_name

    path_to_file = models.CharField(max_length=200)
    file_name = models.CharField(max_length=100, editable=False)
    md5sum = models.CharField(max_length=32, unique=True)
    coordinates = models.CharField(max_length=10000000000, default="[]")
    # elevation
    elevation = models.CharField(max_length=10000000000, default="[]")
    max_altitude = models.FloatField(blank=True, null=True)
    min_altitude = models.FloatField(blank=True, null=True)
    # heart rate
    heart_rate_list = models.CharField(max_length=10000000000, default="[]")
    avg_heart_rate = models.IntegerField(null=True, blank=True)
    max_heart_rate = models.IntegerField(null=True, blank=True)
    min_heart_rate = models.IntegerField(null=True, blank=True)
    # cadence
    cadence_list = models.CharField(max_length=10000000000, default="[]")
    avg_cadence = models.IntegerField(null=True, blank=True)
    max_cadence = models.IntegerField(null=True, blank=True)
    min_cadence = models.IntegerField(null=True, blank=True)
    # speed
    speed_list = models.CharField(max_length=10000000000, default="[]")
    avg_speed = models.FloatField(null=True, blank=True)
    max_speed = models.FloatField(null=True, blank=True)
    min_speed = models.FloatField(null=True, blank=True)
    # temperature
    temperature_list = models.CharField(max_length=10000000000, default="[]")
    avg_temperature = models.IntegerField(null=True, blank=True)
    max_temperature = models.IntegerField(null=True, blank=True)
    min_temperature = models.IntegerField(null=True, blank=True)
    # training effect
    aerobic_training_effect = models.FloatField(blank=True, null=True)
    anaerobic_training_effect = models.FloatField(blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        log.debug(f"creating file name from path {self.path_to_file} -> {self.file_name}")
        self.file_name = self.path_to_file.split("/")[-1]
        if self.elevation:
            if not isinstance(self.elevation, list):
                ele = json.loads(self.elevation)
                self.elevation = list(ele)
            if len(self.elevation) > 0:
                self.max_altitude = round(float(max(self.elevation)), 2)
                self.min_altitude = round(float(min(self.elevation)), 2)
                log.debug(f"found min: {self.min_altitude} and max: {self.max_altitude} altitude")
        if self.heart_rate_list:
            self.min_heart_rate = min(self.heart_rate_list)
        if self.cadence_list:
            self.min_cadence = min(self.cadence_list)
        if self.speed_list:
            self.min_speed = min(self.speed_list)
        if self.temperature_list:
            self.min_temperature = min(self.temperature_list)
        super(Traces, self).save()


class Activity(models.Model):

    def __str__(self):
        return f"{self.name} ({self.sport})"

    name = models.CharField(max_length=200, verbose_name="Activity Name:", default="unknown")
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, verbose_name="Sport:")
    date = models.DateField(blank=False, default=timezone.now, verbose_name="Date:")
    duration = models.DurationField(verbose_name="Duration:", default=datetime.timedelta(minutes=30))
    distance = models.FloatField(blank=True, null=True, verbose_name="Distance:", default=0)
    description = models.CharField(max_length=600, blank=True, null=True, verbose_name="Description:")
    trace_file = models.ForeignKey(Traces, on_delete=models.CASCADE, blank=True, null=True)
    calories = models.IntegerField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        if self.trace_file:
            self.trace_file.delete()
            log.debug(f"deleted trace object {self.trace_file}")
            if os.path.isfile(self.trace_file.path_to_file):
                os.remove(self.trace_file.path_to_file)
                log.debug(f"deleted trace file also: {self.name}")
        super(Activity, self).delete(*args, **kwargs)
        log.debug(f"deleted activity: {self.name}")


class Settings(models.Model):
    days_choices = [(9999, 'all'), (365, 365), (180, 180), (90, 90), (30, 30), (10, 10)]
    plotting_choices = [('bar', 'stacked bar chart'), ('line', 'multiline')]

    path_to_trace_dir = models.CharField(max_length=120, default="/home/pi/traces/",
                                         verbose_name="Path to Traces Directory:")
    path_to_garmin_device = models.CharField(max_length=120, default="/run/user/1000/gvfs/",
                                             verbose_name="Path to Garmin Device:")
    file_checker_interval = models.IntegerField(default=60, verbose_name="File Checker Time Interval:")
    number_of_days = models.IntegerField(choices=days_choices, default=30)
    trace_width = models.FloatField(max_length=20, default=3.0, verbose_name="Width of Traces:")
    trace_opacity = models.FloatField(max_length=20, default=0.7, verbose_name="Opacity of Traces:")
    plotting_style = models.CharField(choices=plotting_choices, default='bar', max_length=120,
                                      verbose_name="Plotting Style:")
