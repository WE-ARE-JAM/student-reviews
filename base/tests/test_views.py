from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from base.models import School, Admin, Staff, Student


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_group = Group.objects.create(name='ADMIN')
        self.staff_group = Group.objects.create(name='STAFF')
        self.school = School.objects.create(name='Test School')

        self.admin_user = User.objects.create_user(
            username='admin',  
            email='admin@test.com', 
            password='password123'
        )

        self.admin_user.groups.add(self.admin_group)

        self.admin = Admin.objects.create(
            user=self.admin_user, 
            school=self.school
        )

        self.staff_user = User.objects.create_user(
            username='staff', 
            email='staff@test.com', 
            password='password123'
        )
        self.staff_user.groups.add(self.staff_group)

        self.staff = Staff.objects.create(
            user=self.staff_user, 
            school=self.school
        )

    def test_admin_login_view(self):
        # admin login, redirect to admin-home
        response = self.client.post(reverse('base:login'), 
            {
                'username': 'admin', 
                'password': 'password123'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('base:admin-home'))

    def test_staff_login_view(self):
        # staff login, redirect to staff-home
        response = self.client.post(reverse('base:login'), 
            {
                'username': 'staff', 
                'password': 'password123'
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('base:staff-home'))


     

   