from django.urls import path
from . import views

urlpatterns = [
   path('create-product/', views.create_product, name='create_product'),
]
