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
    path('student/<str:student_name>/', views.student_profile, name='student-profile'),
    path('student/<str:student_name>/write-review', views.create_review, name='write-review'),
    path('<int:review_id>/vote/<str:vote_value>', views.vote_review, name='vote-review'),
    path('dashboard', views.admin_home, name='admin-home'),
    path('unauthorized', views.unauthorized, name='unauthorized'),
]

# call url using path name, eg. url 'base:student-search'