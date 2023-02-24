from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User (AbstractUser):
    ACCESS_TYPE= [
        ('STAFF', 'Staff'),
        ('STUDENT', 'Student')
    ]
    
    access=models.CharField(max_length=7, choices=ACCESS_TYPE)
    email = models.EmailField(unique=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []