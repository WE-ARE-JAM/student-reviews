from django.contrib import admin
from .models import User, Student, Staff, Review, Vote, Staff_Inbox, Endorsement
# Register your models here.

admin.site.unregister(User)
admin.site.register(User)
admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(Review)
admin.site.register(Vote)
admin.site.register(Staff_Inbox)
admin.site.register(Endorsement)