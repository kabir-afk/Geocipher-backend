import math
from environ import Env
import urllib.parse
import requests
import jwt

env = Env()
env.read_env()

def score_exponential(distance, max_score=5000, decay_rate=0.0005):
    """
    Score decreases exponentially with distance.
    Closer guesses are rewarded much more heavily.
    """
    return round(max_score * math.exp(-decay_rate * distance))

def get_id_token(code):
    token_endpoint = 'https://oauth2.googleapis.com/token'
    payload={
        'code':code,
        'client_id':env('CLIENT_ID'),
        'secret':env('CLIENT_SECRET'),
        'grant_type':'authorization',
        'redirect_uri':'postmessage'
    }

    body=urllib.parse.urlencode(payload)
    headers={
        'content-type':'application/x-www-form-urlendcoded'
    }

    response = requests.post(token_endpoint,body=body,headers=headers)
    if response.ok:
        id_token = response.json()['id_token']
        return jwt.decode(id_token,options={
            "verify_signature":False
        })
    else:
        print(response.json())