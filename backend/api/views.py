from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status , generics
from .models import Coordinates, Score
from .serializers import UserSerializer , CoordinatesSerializer , ScoreSerializer
from .utils import score_exponential , get_id_token# Create your views here.
class CoordinatesList(APIView):

    def get(self,req):
        coords = Coordinates.objects.first()
        serializer = CoordinatesSerializer(coords)
        return Response(serializer.data)

class ScoreList(APIView):
    def get(self,req):
        scores = Score.objects.all()
        serializer = ScoreSerializer(scores, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def post(self,req):
        data = req.data.copy()
        data['score'] = score_exponential(data['distance'])
        print(data)
        print(f"score : {data['score']}")

        serializer = ScoreSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class GoogleLogin(APIView):
    def post(self,req):
        if 'code' in req.data.keys():
            code = req.data['code']
            id_token = get_id_token(code)
        return Response("ok")

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class ProtectedView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,req):
        data={
            'status':"authenticated user's protected view" 
        }
        return Response(data)