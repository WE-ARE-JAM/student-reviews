from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.login_request, name='login'),
    path('register', views.staff_register, name='register'),
    path('login', views.login_request, name='login'),
    path('logout', views.logout_request, name='logout'),
    path('jam-admin', views.superuser_home, name='superuser-home'),
    path('school-register', views.school_register, name='school-register'),
    path('admin-register', views.admin_register, name='admin-register'),
    path('profile', views.staff_home, name='staff-home'),
    path('search-results', views.student_search, name='student-search'),
    path('student/<str:student_name>/', views.student_profile, name='student-profile'),
    path('student/<str:student_name>/write-review', views.create_review, name='write-review'),
    path('student/<int:review_id>/edit-review', views.edit_review, name='edit-review'),
    path('student/<int:review_id>/delete-review', views.delete_review, name='delete-review'),
    path('student/<str:student_name>/endorsement/<str:skill>', views.give_endorsement, name='endorse'),
    path('<int:review_id>/vote/<str:vote_value>', views.vote_review, name='vote-review'),
    path('leaderboard', views.student_ranking, name='leaderboard'),
    path('dashboard', views.admin_home, name='admin-home'),
    path('unauthorized', views.unauthorized, name='unauthorized'),
    path('student/<str:student_name>/recommendation-letter', views.generate_recommendation, name='recommendation-letter'),
    path('student/recommendation-letter/<str:response>', views.download_recommendation, name='download-recommendation'),
    path('leaderboard/download/<int:query>', views.download_leaderboard, name='download-leaderboard'),
    path('student/reviews/<str:student_name>', views.student_reviews, name='student-reviews')
]

# call url using path name, eg. url 'base:student-search'