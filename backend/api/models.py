from django.db import models
from django.contrib.auth.models import User
import json
from pathlib import Path

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    bio = models.TextField()

    def __str__(self):
        return self.username

class Coordinates(models.Model):
    name = models.CharField()
    coordinates = models.JSONField()

class Score(models.Model):
    round = models.IntegerField()
    user_location = models.JSONField()
    actual_location = models.JSONField()
    distance = models.IntegerField(default=0)
    score = models.IntegerField(default=0)