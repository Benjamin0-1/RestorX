import jwt 
from datetime import datetime, timedelta
from django.conf import settings 

ACCESS_SECRET_KEY = settings.SECRET_KEY # or environment variable
REFRESH_SECRET_KEY = settings.REFRESH_SECRET_KEY
ALGORITHM = 'HS256'

def create_access_token(user_id, email):
    payload = {
        'user_id': user_id,
        'email': email,
        'token_type': 'access',
        'exp': datetime.utcnow() + timedelta(minutes=120),
    }
    return jwt.encode(payload, ACCESS_SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id, email):
    payload = {
        'user_id': user_id,
        'email': email,
        'token_type': 'refresh',
        'exp': datetime.utcnow() + timedelta(days=30),
    }
    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)



def decode_access_token(token):
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Signature has expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'

def decode_refresh_token(token):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Signature has expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'
    
def get_user_from_jwt(token): # ACCESS TOKEN
    payload = decode_access_token(token)
    if isinstance(payload, dict) and payload.get('token_type') == 'access':  
        return payload.get('user_id'), payload.get('email') 
    return None, None

# Verifying refresh token
def verify_refresh_token(token):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('token_type') == 'refresh':
            return payload.get('user_id'), payload.get('email')
        else:
            return None, 'Access token provided, INVALID'
    except jwt.ExpiredSignatureError:
        return None, 'Signature has expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'


# Verifying access token
def verify_access_token(token):
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('token_type') == 'access':
            return payload.get('user_id'), payload.get('email')
        else:
            return 'Refresh token provided, INVALID'
    except jwt.ExpiredSignatureError:
        return 'Signature has expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'



'''
def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Signature has expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'
    
def get_user_from_jwt(token):
    payload = decode_token(token)
    if isinstance(payload, dict):  # Ensure it's a dictionary and not an error message
        return payload.get('user_id'), payload.get('email')
    return None, None
'''