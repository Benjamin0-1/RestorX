# restaurant/user/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role, User

@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    # Ensure this signal is processed only for the 'user' app
    if sender.name != 'restaurant.user':
        return

  
    roles = {
        'admin': 'Admin users have all permissions',
        'waiter': 'Waiters can view and manage orders',
        'user': 'Regular user or customer role, default one, does not require any extra configuration'
    }


    for role_name, role_description in roles.items():
        Role.objects.get_or_create(name=role_name, defaults={'description': role_description})


    admin_role = Role.objects.get(name='admin')
    admin_user, created = User.objects.get_or_create(
        email='admin@gmail.com',
        defaults={
            'first_name': 'Admin',
            'role': admin_role
        }
    )
    if created:
        admin_user.set_password('12345')
        admin_user.save()


    waiter_role = Role.objects.get(name='waiter')
    waiter_user, created = User.objects.get_or_create(
        email='waiter@gmail.com',
        defaults={
            'first_name': 'Waiter',
            'role': waiter_role
        }
    )
    if created:
        waiter_user.set_password('12345')
        waiter_user.save()
