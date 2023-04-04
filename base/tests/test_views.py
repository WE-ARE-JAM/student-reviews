import json
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User, Group, AnonymousUser
from django.contrib import messages
from base.models import School, Admin, Staff, Student
from base.forms import StaffRegistrationForm
from base.views import *


class ViewTests(TestCase):

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
        client.logout()

    def test_admin_wrong_pass(self):
        client = Client()
        client.login(username='admin', password='word123')
        response = client.get(reverse('base:admin-home'), follow=True)

        # message = list(response.context.get('messages'))[0]
        # self.assertEqual(message.tags, "success")
        # self.assertTrue("success text" in message.message)

        self.assertEqual(response.status_code, 302)
        client.logout()

    def test_staff_login_view(self):
        client = Client()
        client.login(username='staff', password='password123')
        response = client.get(reverse('base:staff-home'))
        self.assertEqual(response.status_code, 200)
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

