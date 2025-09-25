from django.db import models
import json
from pathlib import Path

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=10)
    email=models.EmailField(default="johdoe@exmaple.com")
    password = models.CharField(max_length=20)

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