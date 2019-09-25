import logging
import datetime

from django.db import models
from django.utils import timezone

from wizer.tools.utils import sanitize

log = logging.getLogger("wizer.models")


class Sport(models.Model):

    def __str__(self):
        return self.name

    name = models.CharField(max_length=24, unique=True, verbose_name="Sport Name:")
    slug = models.CharField(max_length=24, unique=True, editable=False)
    color = models.CharField(max_length=24, verbose_name="Color:")
    icon = models.CharField(max_length=24, verbose_name="Icon:")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = sanitize(self.name)
        log.debug(f"converting name {self.name} to slug {self.slug}")
        super(Sport, self).save()


class Traces(models.Model):

    def __str__(self):
        return self.file_name

    path_to_file = models.CharField(max_length=200)
    file_name = models.CharField(max_length=100, editable=False)
    md5sum = models.CharField(max_length=32, unique=True)
    coordinates = models.CharField(max_length=10000000000)
    altitude = models.CharField(max_length=10000000000, null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.file_name = self.path_to_file.split("/")[-1]
        log.debug(f"creating file name from path {self.path_to_file} -> {self.file_name}")
        super(Traces, self).save()


class Activity(models.Model):

    def __str__(self):
        return f"{self.name} ({self.sport})"

    name = models.CharField(max_length=50, verbose_name="Activity Name:")
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, verbose_name="Sport:")
    date = models.DateField(blank=False, default=timezone.now, verbose_name="Date:")
    duration = models.DurationField(verbose_name="Duration:", default=datetime.timedelta(minutes=30))
    distance = models.FloatField(blank=True, null=True, verbose_name="Distance:")
    description = models.CharField(max_length=300, blank=True, null=True, verbose_name="Description:")
    trace_file = models.ForeignKey(Traces, on_delete=models.CASCADE, blank=True, null=True)


class Settings(models.Model):
    days_choices = [(9999, 'all'), (365, 365), (180, 180), (90, 90), (30, 30), (10, 10), (5, 5)]
    plotting_choices = [('bar', 'stacked bar chart'), ('line', 'multiline')]

    path_to_trace_dir = models.CharField(max_length=120, default="/path/to/your/traces/",
                                         verbose_name="Path to Traces Directory:")
    path_to_garmin_device = models.CharField(max_length=120, default="/path/to/your/garmin-device/",
                                             verbose_name="Path to Garmin Device:")
    file_checker_interval = models.IntegerField(default=60, verbose_name="File Checker Time Interval:")
    number_of_days = models.IntegerField(choices=days_choices, default=30)
    trace_width = models.FloatField(max_length=20, default=3.0, verbose_name="Width of Traces:")
    trace_opacity = models.FloatField(max_length=20, default=0.7, verbose_name="Opacity of Traces:")
    plotting_style = models.CharField(choices=plotting_choices, default='line', max_length=120,
                                      verbose_name="Plotting Style:")
