from django.shortcuts import render

# Create your views here.

user1= User(access='STAFF', username='dillon@email.com', first_name='Dillon', last_name='Laing')
user1.save()
users=User.objects.all()
users

staff1= Staff(faculty='Science and Technology', department='Department of Computing and Information Technology', prefix='Dr.' ,user=user1)
staff1.save()
staff= Staff.objects.all()
staff

user2=User(access='STUDENT', username='jane@email.com', first_name='Jane', last_name='Doe')
user2.save()
stud1=Student(faculty='Science and Technology', department='Department of Computing and Information Technology', user=user2)
stud1.save()
students= Student.objects.all()
students

