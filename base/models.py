from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.utils import timezone
# from zoneinfo import ZoneInfo
from datetime import datetime
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE



# School Model

class School (models.Model):
    name = models.CharField(max_length=200, null=False, unique=True)

    def __str__(self):
        return '%s' % (self.name)



# Admin Model

class Admin (models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    school= models.ForeignKey(School,on_delete=models.CASCADE)

    def __str__(self):
        return '%s : %s' % (self.user.get_full_name(), self.school.name)



# Staff Model

class Staff (models.Model):
    profile_pic = models.ImageField(null=True, default="avatar.svg")
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    school= models.ForeignKey(School,on_delete=models.CASCADE)

    def __str__(self):
        return '%s : %s' % (self.user.get_full_name(), self.school.name)



# Student Model
#A Karma object must be created each time a student is created
#can access the karma score by: [student object].karma.score

class Student (models.Model):
    name= models.CharField(max_length=100, null=False)
    active= models.BooleanField(default=True)
    school= models.ForeignKey(School,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'school',)
    
    def __str__(self):
        return '%s : %s' % (self.name, self.school.name)



# Review Model
# A Stats object must be created each time a review is created
#access total upvotes/downvotes by  [review object].stats.upvotes or [review object].stats.downvotes

class Review(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    staff= models.ForeignKey(Staff, on_delete= models.CASCADE) #could change to models.SET_NULL, null=True
    student= models.ForeignKey(Student, on_delete= models.CASCADE)
    text= models.TextField(max_length=1000, validators=[MinLengthValidator(50)], null=False)
    rating = models.IntegerField(null=False, default=3)
    is_good= models.BooleanField(null=False)
    created_at= models.DateTimeField(auto_now_add=True)
    edited= models.BooleanField(default=False)

    def __str__(self):
        return '%s staff: %s student: %s text: %s rating: %d' % (timezone.localtime(self.created_at).strftime("%d/%m/%Y, %H:%M"), self.staff.user.get_full_name(), self.student.name, self.text, self.rating)

    @property
    def timestamp(self):
        return '%s' % (timezone.localtime(self.created_at).strftime("%b %-d, %Y"))



# Endorsement Model

class Endorsement (models.Model):   #change to boolean
    leadership= models.BooleanField(default=False)
    respect= models.BooleanField(default=False)
    punctuality= models.BooleanField(default=False)
    participation= models.BooleanField(default=False)
    teamwork= models.BooleanField(default=False)
    student= models.ForeignKey(Student, on_delete=models.CASCADE)
    staff= models.ForeignKey(Staff, on_delete=models.CASCADE)

    def __str__(self):
        return 'staff: %s leadership: %s respect: %s punctuality: %s participation: %s teamwork: %s' % (self.staff.user.get_full_name(), self.leadership, self.respect, self.punctuality, self.participation, self.teamwork)



# Endorsement Stats Model

class EndorsementStats (models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)

    @property
    def school(self):
        return self.student.school

    @property
    def leadership(self):
        return Endorsement.objects.filter(student=self.student, leadership=True).count()

    @property
    def respect(self):
        return Endorsement.objects.filter(student=self.student, respect=True).count()

    @property
    def punctuality(self):
        return Endorsement.objects.filter(student=self.student, punctuality=True).count()

    @property
    def participation(self):
        return Endorsement.objects.filter(student=self.student, participation=True).count()

    @property
    def teamwork(self):
        return Endorsement.objects.filter(student=self.student, teamwork=True).count()



# Vote Model

class Vote (models.Model):
    VOTE_TYPE= (
        ("UP", "Upvote"),
        ("DOWN", "Downvote")
    )

    staff= models.ForeignKey(Staff, on_delete= models.CASCADE)
    review= models.ForeignKey(Review, on_delete= models.CASCADE)
    time= models.DateTimeField(auto_now_add=True)
    value= models.CharField(choices=VOTE_TYPE, max_length=4)

    def __str__(self):
        return 'staff: %s review: %s value: %s' % (self.staff, self.review, self.value)



# Karma

class Karma (models.Model):
    student= models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    score = models.IntegerField(default=100)

    def update_score(self):
        karma=100 #default karma score is 100
        reviews=Review.objects.filter(student=self.student)
        for review in reviews:
            num_upvotes= Vote.objects.filter(review=review, value="UP").count()
            num_downvotes= Vote.objects.filter(review=review, value="DOWN").count()
            if review.is_good==True:
                karma= karma + 50 + (num_upvotes*5) - (num_downvotes*5)
            else:
                karma= karma - 50 - (num_upvotes*5) + (num_downvotes*5)
        
        lead= Endorsement.objects.filter(student=self.student, leadership=True).count()
        respect= Endorsement.objects.filter(student=self.student, respect=True).count()
        punc= Endorsement.objects.filter(student=self.student, punctuality=True).count()
        part= Endorsement.objects.filter(student=self.student, participation=True).count()
        team= Endorsement.objects.filter(student=self.student, teamwork=True).count()
        karma= karma + (lead*10) + (respect*10) + (punc*10) + (part*10) + (team*10)

        self.score = karma
        self.save()
    
    def __str__(self):
        return 'student: %s score: %s' % (self.student.name, self.score)



# Stats : for displaying number of upvotes and downvotes per review
# must be created each time a review is created
# call by [review object].stats.upvotes or [review object].stats.downvotes

class Stats (models.Model):
    review= models.OneToOneField(Review, on_delete=models.CASCADE, primary_key=True)

    @property
    def upvotes(self):
        num_upvotes= Vote.objects.filter(review=self.review, value="UP").count()
        return num_upvotes

    @property
    def downvotes(self):
        num_downvotes= Vote.objects.filter(review=self.review, value="DOWN").count()
        return num_downvotes

    def __str__(self):
        return 'upvotes: %s  downvotes: %s' % (self.upvotes, self.downvotes)



# Staff Inbox

class Staff_Inbox (models.Model):
    staff= models.ForeignKey(Staff, on_delete=models.CASCADE)
    message= models.TextField(max_length=50, null=False)

    def __str__(self):
        return 'staff: %s message: %s' % (self.staff, self.message)



class Activity (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # change default when in production
    message = models.TextField()
    created_at= models.DateTimeField(auto_now_add=True)
    parameter = models.TextField()

    def __str__(self):
        return '%s user: %s message: %s parameter: %s' % (timezone.localtime(self.created_at).strftime("%d/%m/%Y, %H:%M"), self.user, self.message, self.parameter)
    
    @property
    def timestamp(self):
        return '%s' % (timezone.localtime(self.created_at).strftime("%d/%m/%Y, %-I:%M%p"))