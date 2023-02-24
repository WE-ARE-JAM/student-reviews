from django.db import models
from users_app.models import User
# Create your models here.

class Staff (models.Model):
    staff_ID= models.IntegerField(primark_key=True, unique=True)
    faculty= models.CharField(max_length=100)
    department= models.CharField(max_length=100)
    courses= models.JSONField()
    users= models.ForeignKey(User, on_delete=models.CASCADE)

