from django.contrib.auth.models import User
from django.db import models


class MoodUpload(models.Model):
    class Mood(models.IntegerChoices):
        SAD = 0
        NEUTRAL = 1
        HAPPY = 2

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.IntegerField(choices=Mood.choices)
    lat = models.FloatField()
    lng = models.FloatField()
