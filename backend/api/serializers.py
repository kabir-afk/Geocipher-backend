from rest_framework import serializers
from .models import User
from .models import Coordinates

class UserSerializer(serializers.ModelSerializer):
    class Meta :
        model = User
        fields = "__all__"

class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = "__all__"