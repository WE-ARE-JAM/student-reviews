from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.login_request, name='login'),
    path('register', views.staff_register, name='register'),
    path('login', views.login_request, name='login'),
    path('logout', views.logout_request, name='logout'),
    path('admin-register', views.admin_register, name='superuser-home'),
    path('profile', views.staff_home, name='staff-home'),
    path('search-results', views.student_search, name='student-search'),
    path('dashboard', views.admin_home, name='admin-home'),
    path('unauthorized', views.unauthorized, name='unauthorized'),
]

# call url using path name, eg. url 'base:student-search'