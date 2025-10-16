from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status , generics
from .models import Coordinates, Score
from .serializers import UserSerializer ,GoogleAuthSerializer, CoordinatesSerializer , ScoreSerializer
from .utils import score_exponential , id_token_data , get_token_pair_and_set_cookie# Create your views here.
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
    permission_classes = [AllowAny]

    def post(self, req):
        credential = req.data.get('credential')
        if not credential:
            return Response({'detail': 'credential required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = id_token_data(credential)
        except ValueError:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=data['email'])
            serializer = GoogleAuthSerializer(user)
            response = get_token_pair_and_set_cookie(user=user,data=serializer.data,status=status.HTTP_200_OK)
            return response
        except User.DoesNotExist:
            serializer = GoogleAuthSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                response = get_token_pair_and_set_cookie(user=user,data=serializer.data,status=status.HTTP_201_CREATED)
                return response
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class ProtectedView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)