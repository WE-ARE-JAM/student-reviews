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

# Stats Model

class Stats (models.Model):
    id= models.IntegerField(primary_key=True)
    leadership= models.IntegerField(default=0)
    respect= models.IntegerField(default=0)
    punctuality= models.IntegerField(default=0)
    participation= models.IntegerField(default=0)
    teamwork= models.IntegerField(default=0)

    #karma= models.IntegerField(default=100)

    def get_stats(self):
        return 'leadership: %s respect: %s punctuality: %s participation: %s teamwork: %s' % (self.leadership, self.respect, self.punctuality, self.participation, self.teamwork)
    
    @property
    def total_stats(self):
        return (self.leadership + self.respect + self.punctuality + self.participation + self.teamwork)

# Student Model

class Student (models.Model):
    id= models.IntegerField(primary_key=True, unique=True)
    faculty= models.CharField(max_length=100, null=False)
    department= models.CharField(max_length=100, null=False)
    bio= models.TextField(max_length=500, null=True)
    lectured_by= models.ManyToManyField(Staff)
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    stats= models.OneToOneField(Stats, on_delete=models.CASCADE, null=True)

    @property
    def name(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)
    
    def __str__(self):
        return '%s : %s : %s : %s' % (self.get_name(), self.faculty, self.department, self.bio)

    def get_lecturers(self):
        return self.lectured_by.all()
    
    @property 
    def karma(self):
        reviews= Review.objects.filter(student=self.id)
        karma=100   #initial karma value is 100
        for review in reviews:
            karma += review.karma
        return karma


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
    leadership= models.IntegerField(default=0)
    respect= models.IntegerField(default=0)
    punctuality= models.IntegerField(default=0)
    participation= models.IntegerField(default=0)
    teamwork= models.IntegerField(default=0)

    def __str__(self):
        return 'staff: %s student: %s text: %s' % (self.staff.name, self.student.name, self.text)

    def get_review_stats(self):
        return 'leadership: %s respect: %s punctuality: %s participation: %s teamwork: %s' % (self.leadership, self.respect, self.punctuality, self.participation, self.teamwork)

    def update_stats(self):
        student= Student.objects.get(id=self.student.id)
        stats= Stats.objects.get(id=student.stats.id)
        stats.leadership = F('leadership') + self.leadership    #add new stats values to stats model
        stats.respect = F('respect') + self.respect
        stats.punctuality= F('punctuality') + self.punctuality
        stats.participation = F('participation') + self.participation
        stats.teamwork = F('teamwork') + self.teamwork
        stats.save()

    def save (self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method
        self.update_stats() #immediately update student's stats when a review is saved

    @property
    def num_upvotes(self):
        return Vote.objects.filter(review=self.id, value="UP").count()
    
    @property
    def num_downvotes(self):
        return Vote.objects.filter(review=self.id, value="DOWN").count()
    
    @property
    def karma(self):
        if (is_good):
            karma= (self.num_upvotes*10) - (self.num_downvotes*10)
            return karma
        else:
            karma= (self.num_downvotes*10) - (self.num_upvotes*10)
            return karma


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



