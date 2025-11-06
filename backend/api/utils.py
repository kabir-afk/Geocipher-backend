import math
from environ import Env
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

env = Env()
env.read_env()

def score_exponential(actual_location,user_location, max_score=5000, decay_rate=0.0005):
    """
    Score decreases exponentially with distance.
    Closer guesses are rewarded much more heavily.
    """
    
    lat1,lon1 = actual_location.values()
    lat2,lon2 = user_location.values()
    
    if lat2 == 0 and lon2 == 0:
        return {"score":0,"distance":0}

    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0

    # convert to radians
    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0

    # apply formulae
    a = (pow(math.sin(dLat / 2), 2) + 
         pow(math.sin(dLon / 2), 2) * 
             math.cos(lat1) * math.cos(lat2));
    rad = 6371
    c = 2 * math.asin(math.sqrt(a))
    distance = math.floor(rad * c)
    score=round(max_score * math.exp(-decay_rate * distance))
    return {"score":score,"distance":distance}

base = 150
def xp_and_level_mech(total_score):
    '''
        I'm going with a linear EXP mechanism , something like
        exp = base * level
    '''
    level = 1
    xp_required = base * level
    while(total_score >= xp_required):
        total_score -= xp_required
        level += 1
        xp_required = base * level
        
    return {"xp":total_score,"xp_required":xp_required,"level":level}

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