from django.db import models
from django.contrib.auth.models import AbstractUser

# User Model

class User (AbstractUser):
    ACCESS_TYPE= (
        ('STAFF', 'Staff'),
        ('STUDENT', 'Student')
    )
    
    access=models.CharField(max_length=7, choices=ACCESS_TYPE)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(null=True, default="avatar.svg") #python -m pip install pillow
    #other fields e.g. firstname, lastname are included by default as part of AbstractUser
    USERNAME_FIELD = 'email'    #lets user log in with email instead of username
    REQUIRED_FIELDS = []


# Staff Model

class Staff (models.Model):
    staff_ID= models.IntegerField(primary_key=True, unique=True)
    faculty= models.CharField(max_length=100)
    department= models.CharField(max_length=100)
    users= models.OneToOneField(User, on_delete=models.CASCADE)


# Student Model

class Student (models.Model):
    student_ID= models.IntegerField(primary_key=True, unique=True)
    faculty= models.CharField(max_length=100)
    department= models.CharField(max_length=100)
    bio= models.TextField()
    lectured_by= models.ManyToManyField(Staff)
    users= models.OneToOneField(User, on_delete=models.CASCADE)

