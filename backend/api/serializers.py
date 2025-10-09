from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Coordinates, Score

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=8,style={"input_type":"password"})
    class Meta :
        model = User
        fields = ["username","email","password"]
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = "__all__"
class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = "__all__"