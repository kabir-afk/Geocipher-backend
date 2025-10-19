from django.db import models
from django.contrib.auth.models import User
import json
from pathlib import Path

# Create your models here.
class Coordinates(models.Model):
    name = models.CharField()
    coordinates = models.JSONField()

class Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
class Score(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE , related_name='rounds',default=1)
    round = models.IntegerField()
    user_location = models.JSONField()
    actual_location = models.JSONField()
    distance = models.IntegerField(default=0)
    score = models.IntegerField(default=0)