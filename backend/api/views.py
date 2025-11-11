from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min , Sum
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from .models import Coordinates, Score , Game
from .serializers import UserSerializer ,GoogleAuthSerializer, CoordinatesSerializer , ScoreSerializer , GameSerializer
from .utils import score_exponential , xp_and_level_mech ,id_token_data , get_token_pair_and_set_cookie
import math , random 

# Create your views here.
class CoordinatesList(APIView):

    def get(self,req):
        coords = Coordinates.objects.first()
        serializer = CoordinatesSerializer(coords)
        all_coords = serializer.data['coordinates']
        random_indices = random.sample(range(0, 299250), 5)        
        coordinates = [all_coords[i] for i in random_indices]
        return Response(coordinates)

class GameView(APIView):
    permission_classes = [AllowAny]
    def post(self,req):
        user = req.user if req.user.is_authenticated else None
        game = Game.objects.create(user=user)
        serializer = GameSerializer(game)
        return Response(serializer.data,status=status.HTTP_201_CREATED)

class ScoreList(APIView):
    permission_classes = [AllowAny]
    def get(self,req):
        scores = Score.objects.all()
        serializer = ScoreSerializer(scores, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def post(self,req):
        data = req.data.copy()
        actual_location = data['actual_location']
        user_location = data['user_location']
        score,distance = score_exponential(actual_location,user_location).values()
        response_payload = {
            "score": score,
            "distance": distance
        }
        if req.user.is_authenticated:
            data['score'] = score
            data['distance'] = distance
            serializer = ScoreSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(response_payload,status=status.HTTP_200_OK)
class GoogleLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, req):
        code = req.data.get('code')
        if not code:
            return Response({"detail": "code missing"}, status=400)
        try:
            data = id_token_data(code=code)
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        game_round_data = Game.objects.filter(user=user)
        if game_round_data.exists():
            serializer = GameSerializer(game_round_data, many=True)
            score_data = serializer.data

            stats = game_round_data.aggregate(
                total_score = Sum('rounds__score'),
                avg_score=Avg('rounds__score'),
                max_score=Max('rounds__score'),
                min_distance=Min('rounds__distance')
            )
            res = xp_and_level_mech(stats['total_score'])
            avg_score = stats['avg_score']
            avg_score = math.floor(avg_score) if avg_score is not None else 0

            data = {
                "username": user.username,
                "date_joined":user.date_joined.strftime("%B %d, %Y"),
                "score": score_data,
                "avg_score": avg_score,
                "max_score": stats['max_score'],
                "min_distance": stats['min_distance'],
                "xp": res['xp'],
                "xp_required": res['xp_required'],
                "level": res['level']
            }
        else:
            data = {
                "username": user.username,
                "date_joined":user.date_joined.strftime("%B %d, %Y"),
                "score": [],
                "avg_score": 0,
                "max_score": 0,
                "min_distance": None,
                "xp": 0,
                "xp_required": 150,
                "level": 1
            }

        return Response(data, status=status.HTTP_200_OK)

class Logout(APIView):
    authentication_classes = []
    permission_classes = []

    def post(sel, req):
        response = Response({"User logged out successfully"},status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token")
        return response