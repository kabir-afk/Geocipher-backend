import math
from environ import Env
import urllib.parse
import requests
import jwt
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

env = Env()
env.read_env()

def score_exponential(distance, max_score=5000, decay_rate=0.0005):
    """
    Score decreases exponentially with distance.
    Closer guesses are rewarded much more heavily.
    """
    return round(max_score * math.exp(-decay_rate * distance))

def id_token_data(code):
    id_info = id_token.verify_oauth2_token(
        code,
        google_requests.Request(),
        env('CLIENT_ID')
    )
    email = id_info['email']
    first_name = id_info.get('given_name', '')
    last_name = id_info.get('family_name', '')
    username = (first_name + last_name) or email.split('@')[0]
    return {'username': username, 'email': email}

def get_token_pair_and_set_cookie(user,data,status):
    refresh = RefreshToken.for_user(user)
    response_data = {
        "access_token": str(refresh.access_token),
        "data":data
    }
    response = Response(response_data, status=status)
    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        httponly=True,
        secure=True,        # Use True in production (HTTPS)
        samesite='None',    # Required for cross-site requests (e.g., if frontend on localhost:5173)
        max_age=7 * 24 * 60 * 60,  # 7 days
    )
    return response