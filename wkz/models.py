from pathlib import Path
import os
import logging
import datetime

from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from colorfield.fields import ColorField

from workoutizer import settings as django_settings
from wkz.file_importer import run_importer__dask
from wkz.tools import sse


log = logging.getLogger(__name__)


class Sport(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=24, unique=True, verbose_name="Sport Name")
    icon = models.CharField(max_length=24, verbose_name="Icon")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    color = ColorField(default="#42FF71", verbose_name="Color")
    evaluates_for_awards = models.BooleanField(verbose_name="Consider Sport for Awards", default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Sport, self).save(*args, **kwargs)


class Traces(models.Model):
    def __str__(self):
        return self.file_name

    path_to_file = models.CharField(max_length=200)
    file_name = models.CharField(max_length=100, editable=False)
    md5sum = models.CharField(max_length=32, unique=True)
    calories = models.IntegerField(null=True, blank=True)
    # coordinates
    latitude_list = models.CharField(max_length=10000000000, default="[]")
    longitude_list = models.CharField(max_length=10000000000, default="[]")
    # distance
    distance_list = models.CharField(max_length=10000000000, default="[]")
    # elevation
    altitude_list = models.CharField(max_length=10000000000, default="[]")
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
    avg_temperature = models.FloatField(null=True, blank=True)
    max_temperature = models.FloatField(null=True, blank=True)
    min_temperature = models.FloatField(null=True, blank=True)
    # training effect
    aerobic_training_effect = models.FloatField(blank=True, null=True)
    anaerobic_training_effect = models.FloatField(blank=True, null=True)
    # timestamps
    timestamps_list = models.CharField(max_length=10000000000, default="[]")
    # total ascent/descent
    total_ascent = models.IntegerField(null=True, blank=True)
    total_descent = models.IntegerField(null=True, blank=True)
    # other
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.file_name = self.path_to_file.split("/")[-1]
        super(Traces, self).save()


def default_sport(return_pk: bool = True):
    sport = Sport.objects.filter(slug="unknown").first()
    if not sport:
        sport = Sport(name="unknown", color="gray", icon="question-circle", slug="unknown")
        sport.save()
    if return_pk:
        return sport.pk
    else:
        return sport


class Activity(models.Model):
    def __str__(self):
        return f"{self.name} ({self.sport})"

    name = models.CharField(max_length=200, verbose_name="Activity Name", default="unknown")
    sport = models.ForeignKey(Sport, on_delete=models.SET_DEFAULT, default=default_sport, verbose_name="Sport")
    date = models.DateTimeField(blank=False, default=timezone.now, verbose_name="Date")
    duration = models.DurationField(verbose_name="Duration", default=datetime.timedelta(minutes=30))
    distance = models.FloatField(blank=True, null=True, verbose_name="Distance", default=0)
    description = models.CharField(max_length=600, blank=True, null=True, verbose_name="Description")
    trace_file = models.ForeignKey(Traces, on_delete=models.CASCADE, blank=True, null=True)
    is_demo_activity = models.BooleanField(verbose_name="Is this a Demo Activity", default=False)
    evaluates_for_awards = models.BooleanField(verbose_name="Consider Activity for Awards", default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        if self.trace_file:
            self.trace_file.delete()
            log.debug(f"deleted trace object {self.trace_file}")
            if os.path.isfile(self.trace_file.path_to_file):
                os.remove(self.trace_file.path_to_file)
                log.debug(f"deleted trace file also: {self.name}")
        super(Activity, self).delete(*args, **kwargs)
        log.debug(f"deleted activity: {self.name}")


class Lap(models.Model):
    start_time = models.DateTimeField(blank=False)
    end_time = models.DateTimeField(blank=False)
    elapsed_time = models.DurationField(blank=False)
    trigger = models.CharField(max_length=120, blank=False)
    start_lat = models.FloatField(blank=True, null=True)
    start_long = models.FloatField(blank=True, null=True)
    end_lat = models.FloatField(blank=True, null=True)
    end_long = models.FloatField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    trace = models.ForeignKey(Traces, on_delete=models.CASCADE, blank=False)
    label = models.CharField(max_length=100, blank=True, null=True, verbose_name="Label")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class BestSection(models.Model):
    """
    Contains all best sections of all activities. Best sections could be e.g. the fastest 5km of an activity. This model
    stores the start and end of each section, which is used to render the sections in the activity view.
    """

    def __str__(self):
        return f"{self.kind} {self.distance}m: {self.max_value}"

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, blank=False)
    kind = models.CharField(max_length=120, blank=False)
    distance = models.IntegerField(blank=False)
    start = models.IntegerField(blank=False)
    end = models.IntegerField(blank=False)
    max_value = models.FloatField(blank=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Settings(models.Model):
    days_choices = [
        (9999, "all"),
        (1095, "3 years"),
        (730, "2 years"),
        (365, "1 year"),
        (180, "180 days"),
        (90, "90 days"),
        (30, "30 days"),
        (10, "10 days"),
    ]

    path_to_trace_dir = models.CharField(
        max_length=120, default=django_settings.TRACKS_DIR, verbose_name="Path to Traces Directory"
    )
    path_to_garmin_device = models.CharField(
        max_length=120, default="/run/user/1000/gvfs/", verbose_name="Path to Garmin Device"
    )
    number_of_days = models.IntegerField(choices=days_choices, default=30)
    delete_files_after_import = models.BooleanField(verbose_name="Delete fit Files after Copying ", default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    __original_path_to_trace_dir = None

    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.__original_path_to_trace_dir = self.path_to_trace_dir
        self.__original_path_to_garmin_device = self.path_to_garmin_device

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        super(Settings, self).save(force_insert, force_update, *args, **kwargs)
        # whenever a path changes, check if it is a valid dir and retrigger watchdog
        if self.path_to_trace_dir != self.__original_path_to_trace_dir:
            from wkz import models

            if Path(self.path_to_trace_dir).is_dir():
                run_importer__dask(models)
            else:
                sse.send(f"<code>{self.path_to_trace_dir}</code> is not a valid path.", "red", "WARNING")
        self.__original_path_to_trace_dir = self.path_to_trace_dir

        if self.path_to_garmin_device != self.__original_path_to_garmin_device:
            from wkz import models

            if Path(self.path_to_garmin_device).is_dir():
                sse.send(f"<b>Device watchdog</b> now monitors <code>{self.path_to_garmin_device}</code>.", "green")
            else:
                sse.send(f"<code>{self.path_to_garmin_device}</code> is not a valid path.", "red", "WARNING")
        self.__original_path_to_garmin_device = self.path_to_garmin_device


def get_settings():
    return Settings.objects.get_or_create(pk=1)[0]
