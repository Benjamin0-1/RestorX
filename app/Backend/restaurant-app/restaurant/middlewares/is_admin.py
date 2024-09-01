from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from restaurant.user.models import User, Role

def admin_only(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = get_object_or_404(User, id=request.user.id) # gets from jwt, so such route needs jwt_required first.
        if user.role.name.lower() == 'admin':
            return view_func(request, *args, **kwargs)
        return JsonResponse({'error': 'Unauthorized access'}, status=403)
    return _wrapped_view
