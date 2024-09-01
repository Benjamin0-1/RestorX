from rest_framework.decorators import api_view #, permission_classes
from rest_framework.response import Response
#from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import make_password
from .models import User, LoginHistory, Role
from django.utils import timezone
#from rest_framework.exceptions import NotFound, AuthenticationFailed
from restaurant.utils.jwt_utils import create_access_token, create_refresh_token, get_user_from_jwt, verify_refresh_token, verify_access_token, decode_access_token, decode_refresh_token
from restaurant.middlewares.is_authenticated import jwt_required 
from datetime import timedelta

'''
    Here we only have user routes which are general user routes.
    Such as login, signup, change password, view login history, and refresh access token.
'''

@api_view(['POST'])
def signup(request):
    data = request.data
    first_name = data.get('first_name')
    email = data.get('email')
    password = data.get('password')

    if not all([first_name, email, password]):
        return Response({'error': 'Missing required fields'}, status=400)

   
    if User.objects.filter(email=email).exists():
        return Response({'error': 'User already exists'}, status=400)

    try:
        new_user = User(first_name=first_name, email=email)
        new_user.set_password(password)  
        new_user.save()
        return Response({'message': 'User created successfully'}, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def login(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return Response({'error': 'Missing required fields'}, status=400)
    
    user = User.objects.filter(email=email).first()
    if not user:
        return Response({'error': 'User not found'}, status=404)    
    
    if not user.check_password(password):
        return Response({'error': 'Invalid password'}, status=401)
    
    try:
      
        login_history = LoginHistory(
            user=user, 
            user_agent=request.META.get('HTTP_USER_AGENT'), 
            login_time=timezone.now()  
        )
        login_history.save()
    except Exception as e:
        return Response({'error': str(e)}, status=500)

    access_token = create_access_token(user.id, user.email)  
    refresh_token = create_refresh_token(user.id, user.email)  
    
    return Response({
        'refresh': refresh_token,
        'access': access_token,
    })

@api_view(['GET'])
def view_login_history(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id, _ = get_user_from_jwt(token)
    user = User.objects.filter(id=user_id).first()

    if not user:
        return Response({'error': 'User not found'}, status=404)

    try:
        login_history = LoginHistory.objects.filter(user=user)
        history_data = [{
            'timestamp': lh.timestamp,
            'user_agent': lh.user_agent,
        } for lh in login_history]
        return Response({'login_history': history_data}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['PUT'])
def change_password(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id, _ = get_user_from_jwt(token)
    user = User.objects.filter(id=user_id).first()

    if not user:
        return Response({'error': 'User not found'}, status=404)
    
    data = request.data
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not all([old_password, new_password]):
        return Response({'error': 'Missing required fields'}, status=400)
    
    if not user.check_password(old_password):
        return Response({'error': 'Invalid old password'}, status=401)
    
    try:
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    

@api_view(['POST'])
def refresh_access_token(request):
    data = request.data
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return Response({'error': 'Refresh token required'}, status=400)
    
    # Verify the refresh token
    user_id, email = verify_refresh_token(refresh_token)
    if not user_id or not email:
        return Response({'error': 'Invalid refresh token'}, status=401)
    
    # Create a new access token
    access_token = create_access_token(user_id, email)
    access_token_expiration = timezone.now() + timedelta(minutes=120)
    
    return Response({
        'access_token': access_token,
        'access_token_expiration': access_token_expiration.isoformat()
    }, status=200)


    


@api_view(['GET'])
@jwt_required
def hello(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id, email = get_user_from_jwt(token)  # Access the email from the tuple
    return Response({'message': f'Hello user {email}'}, status=200)
