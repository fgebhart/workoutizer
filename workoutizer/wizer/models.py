import logging

from django.db import models

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
        self.slug = self.name.lower().replace(" ", "-")
        log.debug(f"converting name {self.name} to slug {self.slug}")
        super(Sport, self).save()


class Activity(models.Model):

    def __str__(self):
        return self.title

    title = models.CharField(max_length=50)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    date = models.DateField(blank=False)
    duration = models.FloatField()
    distance = models.FloatField()
    trace_file = models.FileField(null=True, blank=True)


class Settings(models.Model):

    path_to_trace_dir = models.CharField(max_length=120)


class TraceFiles(models.Model):

    def __str__(self):
        return self.file_name

    path_to_file = models.CharField(max_length=200)
    file_name = models.CharField(max_length=100, editable=False)
    md5sum = models.CharField(max_length=32, unique=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.file_name = self.path_to_file.split("/")[-1]
        log.debug(f"creating file name from path {self.path_to_file} -> {self.file_name}")
        super(TraceFiles, self).save()
