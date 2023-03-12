from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

# School Model

class School (models.Model):
    name= models.CharField(max_length=200, null=False)

    def __str__(self):
        return '%s' % (self.name)


# class User(AbstractUser):
#     pass


# Staff Model

class Staff (models.Model):
    profile_pic = models.ImageField(null=True, default="avatar.svg")
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    school= models.ForeignKey(School,on_delete=models.CASCADE)

    def __str__(self):
        return '%s : %s' % (self.user.get_full_name(), self.school.name)

    @property
    def name(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)
    
    @property
    def get_id(self):
        return self.user.id
    
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)


# Student Model

class Student (models.Model):
    name= models.CharField(max_length=100, null=False)
    active= models.BooleanField(default=True)
    profile_pic = models.ImageField(null=True, default="avatar.svg")
    karma = models.IntegerField(default=100)
    school= models.ForeignKey(School,on_delete=models.CASCADE)
    
    @property
    def name(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)
    
    def __str__(self):
        return '%s : %s : %s' % (self.name, self.school.name, self.karma)
    
    @property 
    def karma(self):
        reviews= Review.objects.filter(student=self.id)
        karma=100   #initial karma value is 100
        for review in reviews:
            karma += review.karma
        return karma


# Subject Model

class Subject(models.Model):

  name= models.CharField(max_length=100, null=False)
  staff= models.ForeignKey(Staff, on_delete=models.CASCADE) 

  def __str__(self):
        return '%s : %s' % (self.name, self.staff.name)


# Studset Model

class Studset (models.Model):
    subject= models.ForeignKey(Staff, on_delete=models.CASCADE) 
    student= models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return '%s : %s' % (self.subject.name, self.staff.student.name)


# Endorsement Model

class Endorsement (models.Model):
    leadership= models.IntegerField(default=0)
    respect= models.IntegerField(default=0)
    punctuality= models.IntegerField(default=0)
    participation= models.IntegerField(default=0)
    teamwork= models.IntegerField(default=0)
    student= models.ForeignKey(Student, on_delete=models.CASCADE)

    def get_stats(self):
        return 'leadership: %s respect: %s punctuality: %s participation: %s teamwork: %s' % (self.leadership, self.respect, self.punctuality, self.participation, self.teamwork)
    
    @property
    def total_stats(self):
        return (self.leadership + self.respect + self.punctuality + self.participation + self.teamwork)


# Review Model

class Review (models.Model):
    staff= models.ForeignKey(Staff, on_delete= models.CASCADE) #could change to models.SET_NULL, null=True
    student= models.ForeignKey(Student, on_delete= models.CASCADE)
    text= models.TextField(max_length=1000, validators=[MinLengthValidator(50)], null=False)
    is_good= models.BooleanField(null=False)
    created= models.DateTimeField(auto_now_add=True)
    edited= models.BooleanField(default=False)
    deleted= models.BooleanField(default=False)

    #stats
    #leadership= models.IntegerField(default=0)  # Remove these to make writing a review faster??
    #respect= models.IntegerField(default=0)
    #punctuality= models.IntegerField(default=0)
    #participation= models.IntegerField(default=0)
    #teamwork= models.IntegerField(default=0)

    def __str__(self):
        return 'staff: %s student: %s text: %s' % (self.staff.name, self.student.name, self.text)    
 
    @property
    def num_upvotes(self):
        return Vote.objects.filter(review=self, value="UP").count()
    
    @property
    def num_downvotes(self):
        return Vote.objects.filter(review=self.id, value="DOWN").count()
    
    @property
    def karma(self):
        if (self.is_good==True):
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

    staff= models.ForeignKey(Staff, on_delete= models.CASCADE)
    review= models.ForeignKey(Review, on_delete= models.CASCADE)
    time= models.DateTimeField(auto_now_add=True)
    value= models.CharField(choices=VOTE_TYPE, max_length=4)

    def __str__(self):
        return 'staff: %s review: %s value: %s' % (self.staff, self.review, self.value)
        

# Staff Inbox

class Staff_Inbox (models.Model):
    staff= models.ForeignKey(Staff, on_delete=models.CASCADE)
    message= models.TextField(max_length=50, null=False)

    def __str__(self):
        return 'staff: %s message: %s' % (self.staff, self.message)


