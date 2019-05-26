from django.db import models


class Sport(models.Model):

    def __str__(self):
        return self.sports_name

    sports_name = models.CharField(max_length=24, unique=True)
    sports_name_slug = models.CharField(max_length=24, unique=True, editable=False)
    color = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=100)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.sports_name_slug = self.sports_name.lower().replace(" ", "_")
        super(Sport, self).save()


class Activity(models.Model):

    def __str__(self):
        return self.title

    title = models.CharField(max_length=400)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    date = models.DateTimeField()
    duration = models.IntegerField()
    distance = models.IntegerField()
