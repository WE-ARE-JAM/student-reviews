from django.db import models
from django.contrib.auth.models import AbstractUser

# User Model

class User (AbstractUser):
    ACCESS_TYPE= (
        ('STAFF', 'Staff'),
        ('STUDENT', 'Student')
    )
    
    access=models.CharField(max_length=7, choices=ACCESS_TYPE, default="STAFF")
    email = models.EmailField(unique=True)
    avatar = models.ImageField(null=True, default="avatar.svg") #python -m pip install pillow
    #other fields e.g. firstname, lastname are included by default as part of AbstractUser
    USERNAME_FIELD = 'email'    #lets user log in with email instead of username
    REQUIRED_FIELDS = []


# Staff Model

class Staff (models.Model):
    id= models.IntegerField(primary_key=True, unique=True)
    faculty= models.CharField(max_length=100, null=True)
    department= models.CharField(max_length=100, null=True)
    users= models.OneToOneField(User, on_delete=models.CASCADE)


# Student Model

class Student (models.Model):
    id= models.IntegerField(primary_key=True, unique=True)
    faculty= models.CharField(max_length=100, null=False)
    department= models.CharField(max_length=100, null=False)
    bio= models.TextField(max_length=500, null=True)
    lectured_by= models.ManyToManyField(Staff)
    users= models.OneToOneField(User, on_delete=models.CASCADE)
    #STATS MISSING


# Review Model

class Review (models.Model):
    id= models.IntegerField(primary_key=True)
    staff= models.ForeignKey(Staff, on_delete= models.CASCADE) #could change to models.SET_NULL, null=True
    student= models.ForeignKey(Student, on_delete= models.CASCADE)
    text= models.TextField(max_length=1000, min_length=50, null=False)
    is_good= models.BooleanField(null=False)
    created= models.DateTimeField(auto_now_add=True)
    edited= models.BooleanField(default=False)
    deleted= models.BooleanField(default=False)
    #VOTES AND STATS MISSING

# Vote Model

class Vote (model.Model):
    VOTE_TYPE= (
        ("UP", "Upvote"),
        ("DOWN", "Downvote")
    )

    id=models.IntegerField(primary_key=True)
    staff= models.ForeignKey(Staff, on_delete= models.CASCADE)
    review= models.ForeignKey(Review, on_delete= models.CASCADE)
    time= models.DateTimeField(auto_now_add=True)
    value= models.CharField(choices=VOTE_TYPE, max_length=4)

# Staff Inbox




