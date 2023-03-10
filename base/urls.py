from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.register, name='register'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
]