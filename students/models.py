from django.db import models
from users_app.models import User

# Create your models here.

class Student (models.Model):
    student_ID= models.IntegerField(primark_key=True, unique=True)
    faculty= models.CharField(max_length=100)
    department= models.CharField(max_length=100)
    courses= models.JSONField()
    bio= models.TextField()
    users= models.ForeignKey(User, on_delete=models.CASCADE)