from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from restaurant.user.models import User, Role

def waiter_only(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        if user.role.name.lower() == 'waiter':
            return view_func(request, *args, **kwargs)
        return JsonResponse({'error': 'Unauthorized access'}, status=403)
    return _wrapped_view

