
'''
The Role model is a many-to-many relationship with the Permission model.
This means that a role can have many permissions and a permission can be assigned to many roles.

A user can have one role (i.e waiter, admin), or none (if  customer).
yes, there can be more than 1 admin, but the admin role will have all permissions.

Here we will have 3 roles: Admin, Waiter, and User.
The Admin role will have all permissions(this could be the restaurant owner).
The Waiter role will have permissions to view the menu, take orders, and view orders.
The User role will have permissions to view the menu, order food, and view orders.


The User model is a one-to-many relationship with the LoginHistory model.
This means that a user can have many login histories but a login history can only belong to one user.
example:
    - A user can have many login histories
    - A login history can only belong to one user

On server start we should create the waiter and admin roles and assign the necessary permissions to them.
Along with a few default users of each role.

'''

from django.db import models
from django.contrib.auth.hashers import make_password, check_password 
from django.core.validators import EmailValidator 

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name

class User(models.Model):
    first_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    password_hash = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")

    def set_password(self, password):
        self.password_hash = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password_hash)

    def serialize(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'email': self.email,
            'role': self.role.name if self.role else None,
        }

    def __str__(self):
        return self.first_name

    



class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_histories')
    login_ip = models.GenericIPAddressField(null=True, default='0.0.0.0')
    login_time = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=255)

    def __str__(self):
        return f"LoginHistory of {self.user.email} at {self.login_time}"
    
class AuditLog(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='audit_logs')  # user.audit_logs.all()
    action = models.CharField(max_length=255) # example: User created, User updated, User deleted, Plate created, Plate updated, Plate deleted
    action_time = models.DateTimeField(auto_now_add=True)
    action_ip = models.GenericIPAddressField(null=True, default='0.0.0.0') 

    def __str__(self):
        return f"AuditLog: {self.action} by {self.user.email} at {self.action_time}"

class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.email} - {self.token_type} token"

'''from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role, Permission

@receiver(post_migrate)
def create_roles(sender, **kwargs):
    # Code to create roles and assign permissions
    admin_role, created = Role.objects.get_or_create(name='Admin')
    waiter_role, created = Role.objects.get_or_create(name='Waiter')
    user_role, created = Role.objects.get_or_create(name='User')
    
    # Example permissions
    view_menu, created = Permission.objects.get_or_create(name='View Menu')
    take_orders, created = Permission.objects.get_or_create(name='Take Orders')
    
    # Assign permissions
    admin_role.permissions.add(view_menu, take_orders)
    waiter_role.permissions.add(view_menu, take_orders)


    in case of migration errors: 
    python manage.py makemigrations user
    python3 manage.py migrate user/ or whatever the app name is
    python3 manage.py inspectdb <- will show the models in the database defined in python


'''

