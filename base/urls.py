from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.staff_login, name='login'),
    path('register', views.register, name='register'),
    path('login', views.staff_login, name='login'),
    path('home', views.staff_home, name='home')
]