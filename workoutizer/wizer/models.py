from django.db import models


class Sport(models.Model):

    def __str__(self):
        return self.sport

    sport = models.CharField(max_length=200)
    color = models.CharField(max_length=200)


class Activity(models.Model):

    def __str__(self):
        return self.activity

    title = models.CharField(max_length=400)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    date = models.DateTimeField('date published')
    duration = models.IntegerField()
    distance = models.IntegerField()
