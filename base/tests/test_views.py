import json
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User, Group, AnonymousUser
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from base.models import School, Admin, Staff, Student
from base.forms import StaffRegistrationForm
from base.views import *


class LoginViewTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        
        self.admin_group = Group.objects.create(name='ADMIN')
        self.staff_group = Group.objects.create(name='STAFF')
        self.school = School.objects.create(name='Test School')
        self.admin_user = User.objects.create_user(
            first_name = 'Test',
            last_name = 'Admin',
            username='admin',  
            email='admin@test.com', 
            password='password123', 
        )
        self.admin_user.groups.add(self.admin_group)
        self.admin = Admin.objects.create(
            user=self.admin_user, 
            school=self.school
        )

        self.staff_user = User.objects.create_user(
            first_name = 'Test',
            last_name = 'Staff',
            username='staff', 
            email='staff@test.com', 
            password='password123'
        )
        self.staff = Staff.objects.create(
            user=self.staff_user, 
            school=self.school
        )
        self.staff_user.groups.add(self.staff_group)
        
    def test_login_available_by_name(self):
        client = Client()
        response = client.get(reverse('base:login'))
        self.assertEqual(response.status_code, 200)
    
    def test_staff_register_available_by_name(self):
        client = Client()
        response = client.get(reverse('base:register'))
        self.assertEqual(response.status_code, 200)

    def test_admin_login_view(self):
        client = Client()
        client.login(username='admin', password='password123')
        response = client.get(reverse('base:admin-home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin-home.html')
        client.logout()

    def test_admin_wrong_pass(self):
        client = Client()
        client.login(username='admin', password='word123')
        response = client.get(reverse('base:admin-home'))
        self.assertEqual(response.status_code, 302)
        client.logout()

    def test_staff_login_view(self):
        client = Client()
        client.login(username='staff', password='password123')
        response = client.get(reverse('base:staff-home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff-home.html')
        client.logout()

    def test_staff_registration(self):
        client = Client()
        form_data = {
            'first_name': 'Barry',
            'last_name': 'Doe',
            'username': 'staff3',
            'email': 'staff3@test.com',
            'password1': 'aMuchMoreComplicatedPassword',
            'password2': 'aMuchMoreComplicatedPassword',
            'school': self.school.pk
        }
        response = client.post(reverse('base:register'), data=form_data)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Staff.objects.count(), 2)
        client.login(username='staff3', password='aMuchMoreComplicatedPassword')
        response = client.get(reverse('base:staff-home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff-home.html')



class StaffHomeViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.staff_group = Group.objects.create(name='STAFF')
        self.school = School.objects.create(name="Presentation College")
        self.user = User.objects.create_user(
            email='presstaff@gmail.com',
            username = 'presstaff',
            first_name = 'Test',
            last_name = 'User',
            password = 'testpassword'
        )
        self.staff = Staff.objects.create(user=self.user, school=self.school)
        self.user.groups.add(self.staff_group)
        self.student = Student.objects.create(name="Jane Doe", school=self.school)
        self.review = Review.objects.create(staff=self.staff, student=self.student, text="This is a test review that is at least fifty characters.", rating=3, is_good=True)
        self.stats = Stats.objects.create(review=self.review)
        Endorsement.objects.create(leadership=True, respect=True, punctuality=True, participation=True, teamwork=True, student=self.student, staff=self.staff)
        self.activity = Activity.objects.create(user=self.user, message="Some message", parameter="NA")
        self.expected_activity = [self.activity]

    def test_staff_home(self):
        client = Client()
        client.login(username='presstaff', password='testpassword')
        response = client.get(reverse('base:staff-home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff-home.html')
        self.assertEqual(response.context['num_reviews'], 1)
        self.assertEqual(response.context['num_upvotes'], 0)
        self.assertEqual(response.context['num_downvotes'], 0)
        self.assertEqual(response.context['num_endorsements'], 5)
        #print(response.context)
        self.assertQuerysetEqual(response.context['activities'], self.expected_activity)


class StaffSearchViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.staff_group = Group.objects.create(name='STAFF')
        self.school = School.objects.create(name="Naparima College")
        self.school2 = School.objects.create(name="Presentation College")
        self.user = User.objects.create_user(
            email='napsstaff@gmail.com',
            username = 'napsstaff',
            first_name = 'Test',
            last_name = 'User',
            password = 'testpassword'
        )
        self.staff = Staff.objects.create(user=self.user, school=self.school)
        self.user.groups.add(self.staff_group)
        self.student1 = Student.objects.create(name="Harry Baksh", school=self.school)
        self.student2 = Student.objects.create(name="Jeff Dom", school=self.school)
        self.student3 = Student.objects.create(name="Larry Kompf", school=self.school)
        self.student4 = Student.objects.create(name="Kyle Ali", school=self.school2)
        self.review = Review.objects.create(staff=self.staff, student=self.student1, text="This is a test review that is at least fifty characters.", rating=3, is_good=True)
        self.stats = Stats.objects.create(review=self.review)
        Endorsement.objects.create(leadership=True, respect=True, punctuality=True, participation=True, teamwork=True, student=self.student1, staff=self.staff)
        self.activity = Activity.objects.create(user=self.user, message="Some message", parameter="NA")

    def test_student_search(self):
        client = Client()
        client.login(username='napsstaff', password='testpassword')
        response = client.get(reverse('base:staff-home'))
        response = client.get(reverse('base:search-results'), {'query': 'Harry'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.student1.name)
        self.assertNotContains(response, self.student2.name)
        self.assertNotContains(response, self.student3.name)

    def test_student_search_empty(self):
        client = Client()
        client.login(username='napsstaff', password='testpassword')
        response = client.get(reverse('base:staff-home'))
        response = client.get(reverse('base:search-results'), {'query': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.student1.name)
        self.assertContains(response, self.student2.name)
        self.assertContains(response, self.student3.name)

    def test_student_search_different_school(self):
        client = Client()
        client.login(username='napsstaff', password='testpassword')
        response = client.get(reverse('base:staff-home'))
        response = client.get(reverse('base:search-results'), {'query': 'Kyle'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.student1.name)
        self.assertNotContains(response, self.student2.name)
        self.assertNotContains(response, self.student3.name)
        self.assertNotContains(response, self.student4.name)



class StudentProfileViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.staff_group = Group.objects.create(name='STAFF')
        self.school = School.objects.create(name="Presentation College")
        self.user = User.objects.create_user(
            email='presstaff@gmail.com',
            username = 'presstaff',
            first_name = 'Test',
            last_name = 'User',
            password = 'testpassword'
        )
        self.staff = Staff.objects.create(user=self.user, school=self.school)
        self.user.groups.add(self.staff_group)
        self.student = Student.objects.create(name="Jane Doe", school=self.school)
        self.review = Review.objects.create(staff=self.staff, student=self.student, text="This is a test review that is at least fifty characters.", rating=3, is_good=True)
        self.stats = Stats.objects.create(review=self.review)
        Endorsement.objects.create(leadership=True, respect=True, punctuality=False, participation=True, teamwork=False, student=self.student, staff=self.staff)
        self.endorsement_stats = EndorsementStats.objects.create(student=self.student)
        self.vote = Vote.objects.create(staff=self.staff, review=self.review, value="UP")
        Karma.objects.create(student=self.student)

    
    def test_student_profile(self):
        client = Client()
        client.login(username='presstaff', password='testpassword')
        response = client.get(reverse('base:staff-home'))
        self.assertEqual(response.status_code, 200)
        response = client.get(reverse('base:student-profile', kwargs={'student_name': self.student.name}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['student'], self.student)        
        self.assertEqual(response.context['endorsement_stats'], self.endorsement_stats)
        self.assertEqual(response.context['reviews'][0][0], self.review)


class ReviewViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.staff_group = Group.objects.create(name='STAFF')
        self.school = School.objects.create(name="Presentation College")
        self.user = User.objects.create_user(
            email='presstaff@gmail.com',
            username = 'presstaff',
            first_name = 'Test',
            last_name = 'User',
            password = 'testpassword'
        )
        self.staff = Staff.objects.create(user=self.user, school=self.school)
        self.user.groups.add(self.staff_group)
        self.student = Student.objects.create(name="Jane Doe", school=self.school)
        Endorsement.objects.create(leadership=True, respect=True, punctuality=False, participation=True, teamwork=False, student=self.student, staff=self.staff)
        Karma.objects.create(student=self.student, score=100)
        self.endorsement_stats = EndorsementStats.objects.create(student=self.student)
        self.text = "This is a test review that is at least fifty characters."
        self.form_data = {
            'text' : self.text,
            'rating' : '3'
        }
    
    def test_create_review(self):
        client = Client()
        client.login(username='presstaff', password='testpassword')
        response = client.get(reverse('base:write-review', kwargs={'student_name':self.student.name}))
        self.assertTemplateUsed(response, 'create-review.html')
        response = client.post(reverse('base:write-review', kwargs={'student_name':self.student.name}), self.form_data)
        self.assertEqual(response.status_code, 302)
        response = client.get(reverse('base:student-profile', kwargs={'student_name': self.student.name}))
        review = Review.objects.get(student=self.student)
        self.assertEqual(response.context['reviews'][0][0], review)
    
    def test_edit_review(self):
        client = Client()
        client.login(username='presstaff', password='testpassword')

        #creating review
        response = client.get(reverse('base:write-review', kwargs={'student_name':self.student.name}))
        response = client.post(reverse('base:write-review', kwargs={'student_name':self.student.name}), self.form_data)
        response = client.get(reverse('base:student-profile', kwargs={'student_name': self.student.name}))

        #confirming review 
        self.assertEqual(response.context['reviews'][0][0].text, self.text)

        #editing review
        self.form_data['text'] = 'This is a different review text to show that the review is edited'
        review_id = response.context['reviews'][0][0].id
        response = client.get(reverse('base:edit-review', kwargs={'review_id' : review_id}), self.form_data)
        self.assertTemplateUsed(response, 'edit-review.html')
        response = client.post(reverse('base:edit-review', kwargs={'review_id' : review_id}), self.form_data)

        #confirming edit
        response = client.get(reverse('base:student-profile', kwargs={'student_name': self.student.name}))
        review = Review.objects.get(student=self.student)
        self.assertEqual(review.text, self.form_data['text'])
        self.assertEqual(response.context['reviews'][0][0], review)
    
    def test_delete_review(self):
        client = Client()
        client.login(username='presstaff', password='testpassword')

        #create review
        response = client.get(reverse('base:write-review', kwargs={'student_name':self.student.name}))
        response = client.post(reverse('base:write-review', kwargs={'student_name':self.student.name}), self.form_data)
        response = client.get(reverse('base:student-profile', kwargs={'student_name': self.student.name}))  

        #confirming review
        self.assertEqual(response.context['reviews'][0][0].text, self.text)
        review_id = response.context['reviews'][0][0].id
        review = Review.objects.get(id=review_id)

        #deleting review
        response = client.post(reverse('base:delete-review', kwargs={'review_id' : review_id}))

        #confirming review deleted
        self.assertFalse(Review.objects.filter(id=review.id).exists())
    
    def test_upvote_review(self):
        client = Client()
        client.login(username='presstaff', password='testpassword')
        response = client.get(reverse('base:write-review', kwargs={'student_name':self.student.name}))
        self.assertTemplateUsed(response, 'create-review.html')
        response = client.post(reverse('base:write-review', kwargs={'student_name':self.student.name}), self.form_data)
        self.assertEqual(response.status_code, 302)
        response = client.get(reverse('base:student-profile', kwargs={'student_name':self.student.name}))
        review_id = response.context['reviews'][0][0].id
        review = Review.objects.get(id=review_id)
        self.assertEqual(response.context['reviews'][0][0], review)  
        response = client.post(reverse('base:vote-review', kwargs={'review_id':review_id, 'vote_value':'UP'}))    
        response = client.get(reverse('base:student-profile', kwargs={'student_name':self.student.name}))
        review = Review.objects.filter(id=review.id).first()
        self.assertEqual(review.stats.upvotes, 1)
        self.assertEqual(review.stats.downvotes, 0)

    def test_downvote_review(self):
        client = Client()
        client.login(username='presstaff', password='testpassword')
        response = client.get(reverse('base:write-review', kwargs={'student_name':self.student.name}))
        self.assertTemplateUsed(response, 'create-review.html')
        response = client.post(reverse('base:write-review', kwargs={'student_name':self.student.name}), self.form_data)
        self.assertEqual(response.status_code, 302)
        response = client.get(reverse('base:student-profile', kwargs={'student_name':self.student.name}))
        review_id = response.context['reviews'][0][0].id
        review = Review.objects.get(id=review_id)
        self.assertEqual(response.context['reviews'][0][0], review)  
        response = client.post(reverse('base:vote-review', kwargs={'review_id':review_id, 'vote_value':'DOWN'}))    
        response = client.get(reverse('base:student-profile', kwargs={'student_name':self.student.name}))
        review = Review.objects.filter(id=review.id).first()
        self.assertEqual(review.stats.upvotes, 0)
        self.assertEqual(review.stats.downvotes, 1)

    def test_upvote_twice_review(self):
        client = Client()
        client.login(username='presstaff', password='testpassword')
        response = client.get(reverse('base:write-review', kwargs={'student_name':self.student.name}))
        self.assertTemplateUsed(response, 'create-review.html')
        response = client.post(reverse('base:write-review', kwargs={'student_name':self.student.name}), self.form_data)
        self.assertEqual(response.status_code, 302)
        response = client.get(reverse('base:student-profile', kwargs={'student_name':self.student.name}))
        review_id = response.context['reviews'][0][0].id
        review = Review.objects.get(id=review_id)
        self.assertEqual(response.context['reviews'][0][0], review)  
        response = client.post(reverse('base:vote-review', kwargs={'review_id':review_id, 'vote_value':'UP'}))   
        response = client.post(reverse('base:vote-review', kwargs={'review_id':review_id, 'vote_value':'UP'}))     
        response = client.get(reverse('base:student-profile', kwargs={'student_name':self.student.name}))
        review = Review.objects.filter(id=review.id).first()
        self.assertEqual(review.stats.upvotes, 0)
        self.assertEqual(review.stats.downvotes, 0)

    def test_downvote_twice_review(self):
        client = Client()
        client.login(username='presstaff', password='testpassword')
        response = client.get(reverse('base:write-review', kwargs={'student_name':self.student.name}))
        self.assertTemplateUsed(response, 'create-review.html')
        response = client.post(reverse('base:write-review', kwargs={'student_name':self.student.name}), self.form_data)
        self.assertEqual(response.status_code, 302)
        response = client.get(reverse('base:student-profile', kwargs={'student_name':self.student.name}))
        review_id = response.context['reviews'][0][0].id
        review = Review.objects.get(id=review_id)
        self.assertEqual(response.context['reviews'][0][0], review)  
        response = client.post(reverse('base:vote-review', kwargs={'review_id':review_id, 'vote_value':'DOWN'}))   
        response = client.post(reverse('base:vote-review', kwargs={'review_id':review_id, 'vote_value':'DOWN'}))     
        response = client.get(reverse('base:student-profile', kwargs={'student_name':self.student.name}))
        review = Review.objects.filter(id=review.id).first()
        self.assertEqual(review.stats.upvotes, 0)
        self.assertEqual(review.stats.downvotes, 0)

    def test_upvote_downvote_review(self):
        client = Client()
        client.login(username='presstaff', password='testpassword')
        response = client.get(reverse('base:write-review', kwargs={'student_name':self.student.name}))
        self.assertTemplateUsed(response, 'create-review.html')
        response = client.post(reverse('base:write-review', kwargs={'student_name':self.student.name}), self.form_data)
        self.assertEqual(response.status_code, 302)
        response = client.get(reverse('base:student-profile', kwargs={'student_name':self.student.name}))
        review_id = response.context['reviews'][0][0].id
        review = Review.objects.get(id=review_id)
        self.assertEqual(response.context['reviews'][0][0], review)  
        response = client.post(reverse('base:vote-review', kwargs={'review_id':review_id, 'vote_value':'UP'}))   
        response = client.post(reverse('base:vote-review', kwargs={'review_id':review_id, 'vote_value':'DOWN'}))     
        response = client.get(reverse('base:student-profile', kwargs={'student_name':self.student.name}))
        review = Review.objects.filter(id=review.id).first()
        self.assertEqual(review.stats.upvotes, 0)
        self.assertEqual(review.stats.downvotes, 1)


class GiveEndorsementTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff = Staff.objects.create(
            username='staff',
            password='password',
            school='Test School'
        )
        self.student = Student.objects.create(
            name='Test Student',
            school='Test School'
        )
        self.url = reverse('base:give-endorsement', args=[self.student.name, 'leadership'])
        self.login_url = reverse('login')
        self.credentials = {
            'username': 'staff',
            'password': 'password'
        }