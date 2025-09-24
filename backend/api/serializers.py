from rest_framework import serializers
from .models import User
from .models import Coordinates, Score

class UserSerializer(serializers.ModelSerializer):
    class Meta :
        model = User
        fields = "__all__"

class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = "__all__"
class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = "__all__"