from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('refresh-token/', views.refresh_access_token, name='refresh_access_token'),  # Added path for refreshing access token
    path('login-history/', views.view_login_history, name='view_login_history'),  # Added path for login history
    path('change-password/', views.change_password, name='change_password'),  # Added path for changing password
    path('hello', views.hello, name='hello'),  # Added path for testing
]
