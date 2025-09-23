from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import User , Coordinates
from .serializers import UserSerializer , CoordinatesSerializer
# Create your views here.
class CoordinatesList(APIView):

    def get(self,req):
        coords = Coordinates.objects.first()
        serializer = CoordinatesSerializer(coords)
        return Response(serializer.data)