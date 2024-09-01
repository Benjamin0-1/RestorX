import jwt
from django.conf import settings
from django.http import JsonResponse
from functools import wraps
from restaurant.user.models import User

SECRET_KEY = settings.SECRET_KEY

def jwt_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return JsonResponse({'error': 'Token required'}, status=401)
        
        parts = auth_header.split()
        if parts[0].lower() != 'bearer':
            return JsonResponse({'error': 'Invalid authorization header format'}, status=401)
        elif len(parts) != 2:
            return JsonResponse({'error': 'Token not found'}, status=401)
        
        token = parts[1]
        
        try:
            # Decode the access token
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            if decoded.get('token_type') != 'access':  # Ensure it's an access token
                return JsonResponse({'error': 'Invalid token type'}, status=401)
            request.user = User.objects.get(id=decoded.get('user_id'))
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
