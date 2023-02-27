from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator

# User Model

class User (AbstractUser):
    ACCESS_TYPE= (
        ('STAFF', 'Staff'),
        ('STUDENT', 'Student')
    )

    access=models.CharField(max_length=7, choices=ACCESS_TYPE, default="STAFF")
    email = models.EmailField(unique=True, null=False)
    avatar = models.ImageField(null=True, default="avatar.svg") #python -m pip install pillow
    first_name=models.CharField(null=False, max_length=50)
    last_name=models.CharField(null=False, max_length=100)

    #other fields e.g. firstname, lastname are included by default as part of AbstractUser

    USERNAME_FIELD = 'email'    #lets user log in with email instead of username
    REQUIRED_FIELDS = []


# Staff Model

class Staff (models.Model):

    PREFIX= (
        ('Prof.', 'Prof.'),
        ('Dr.', 'Dr.'),
        ('Mrs.', 'Mrs.'),
        ('Ms.', 'Mrs.'),
        ('Mr.', 'Mr.'),
        ('Mx.', 'Mx.')  #gender neutral prefix
    )

    id= models.IntegerField(primary_key=True, unique=True)
    faculty= models.CharField(max_length=100, null=True)
    department= models.CharField(max_length=100, null=True)
    prefix= models.CharField(max_length=5, choices=PREFIX, default="Mx.")
    user= models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return '%s : %s : %s' % (self.faculty, self.department, self.get_name())

    @property
    def name(self):
        return '%s %s %s' % (self.prefix, self.user.first_name, self.user.last_name)


# Student Model

class Student (models.Model):
    id= models.IntegerField(primary_key=True, unique=True)
    faculty= models.CharField(max_length=100, null=False)
    department= models.CharField(max_length=100, null=False)
    bio= models.TextField(max_length=500, null=True)
    #stats
    leardership= models.IntegerField(default=0)
    respect= models.IntegerField(default=0)
    punctuality= models.IntegerField(default=0)
    participation= models.IntegerField(default=0)
    teamwork= models.IntegerField(default=0)

    lectured_by= models.ManyToManyField(Staff)
    user= models.OneToOneField(User, on_delete=models.CASCADE)

    @property
    def name(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)
    
    def __str__(self):
        return '%s : %s : %s : %s' % (self.get_name(), self.faculty, self.department, self.bio)
    
    def get_stats(self):
        return 'leadership: %s respect: %s punctuality: %s participation: %s teamwork: %s' % (self.leadership, self.respect, self.punctuality, self.participation, self.teamwork)

    def get_lecturers(self):
        return self.staff_set.all()

# Review Model

class Review (models.Model):
    id= models.IntegerField(primary_key=True)
    staff= models.ForeignKey(Staff, on_delete= models.CASCADE) #could change to models.SET_NULL, null=True
    student= models.ForeignKey(Student, on_delete= models.CASCADE)
    text= models.TextField(max_length=1000, validators=[MinLengthValidator(50)], null=False)
    is_good= models.BooleanField(null=False)
    created= models.DateTimeField(auto_now_add=True)
    edited= models.BooleanField(default=False)
    deleted= models.BooleanField(default=False)

    #stats
    leardership= models.IntegerField(default=0)
    respect= models.IntegerField(default=0)
    punctuality= models.IntegerField(default=0)
    participation= models.IntegerField(default=0)
    teamwork= models.IntegerField(default=0)




# Vote Model

class Vote (models.Model):
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

class Staff_Inbox (models.Model):
    id= models.IntegerField(primary_key=True)
    staff= models.ForeignKey(Staff, on_delete=models.CASCADE)
    message= models.TextField(max_length=50, null=False)

class Student_Inbox (models.Model):
    id= models.IntegerField(primary_key=True)
    student= models.ForeignKey(Student, on_delete=models.CASCADE)
    message= models.TextField(max_length=50, null=False)



