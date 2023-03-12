from django.contrib import admin
from .models import School, Admin, Student, Staff, Review, Vote, Staff_Inbox, Endorsement, Karma, Stats

# Register your models here.

admin.site.register(School)
admin.site.register(Admin)
admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(Review)
admin.site.register(Vote)
admin.site.register(Staff_Inbox)
admin.site.register(Endorsement)
admin.site.register(Karma)
admin.site.register(Stats)