from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status , generics
from .models import Coordinates, Score
from .serializers import UserSerializer ,GoogleAuthSerializer, CoordinatesSerializer , ScoreSerializer
from .utils import score_exponential , id_token_data , get_token_pair_and_set_cookie
import math

# Create your views here.
class CoordinatesList(APIView):

    def get(self,req):
        coords = Coordinates.objects.first()
        serializer = CoordinatesSerializer(coords)
        return Response(serializer.data)

class ScoreList(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,req):
        scores = Score.objects.all()
        serializer = ScoreSerializer(scores, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def post(self,req):
        data = req.data.copy()
        data['score'] = score_exponential(data['distance'])
        serializer = ScoreSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=req.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, req):
        data = req.data
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return get_token_pair_and_set_cookie(user=user, data=serializer.data, status=status.HTTP_201_CREATED)

class ProtectedView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request):
        user = request.user
        score = Score.objects.filter(user=user)
        if score.exists():
            serializer = ScoreSerializer(score,many=True)
            score_data = serializer.data
            all_scores = list(map(lambda item:item['score'] , score_data))
            avg_score = math.floor(sum(all_scores)/len(all_scores))
            max_score = max(all_scores)
        else :
            score_data = 0
        data = {
            "username": user.username,
            "score": score_data,
            "avg_score": avg_score,
            "max_score": max_score
        }
        return Response(data,status=status.HTTP_200_OK)
class Logout(APIView):
    authentication_classes = []
    permission_classes = []

    def post(sel, req):
        response = Response({"User logged out successfully"},status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token")
        return response