from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.Login.as_view(), name='api-v1-login'),
    path('register/', views.Register.as_view(), name='api-v1-register'),
]