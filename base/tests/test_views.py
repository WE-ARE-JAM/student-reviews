from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from base.models import Admin, Staff, School, Review


class BaseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_group = Group.objects.create(name='ADMIN')
        self.staff_group = Group.objects.create(name='STAFF')
        self.school = School.objects.create(name='Test School')
        self.admin_user = User.objects.create_user(username='admin', email='admin@test.com', password='password123')
        self.admin_user.groups.add(self.admin_group)
        self.admin = Admin.objects.create(user=self.admin_user, school=self.school)
        self.staff_user = User.objects.create_user(username='staff', email='staff@test.com', password='password123')
        self.staff_user.groups.add(self.staff_group)
        self.staff = Staff.objects.create(user=self.staff_user, school=self.school)


class LoginTest(BaseTest):
    def test_admin_login(self):
        response = self.client.post(reverse('base:login'), {'username': 'admin', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('base:admin-home'))
        self.client.logout()

    def test_admin_logout(self):
        response = self.client.post(reverse('base:logout'), {'username': 'admin', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('base:login'))
        self.client.logout()

    # def test_staff_login(self):
    #     self.client.logout()
    #     response = self.client.post(reverse('base:login'), {'username': 'staff', 'password': 'password123'})
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse('base:staff-home'))
    
    # def test_staff_logout(self):
    #     response = self.client.post(reverse('base:logout'), {'username': 'staff', 'password': 'password123'})
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse('base:login'))
    #     self.client.logout()
        

class AdminTest(TestCase):
    def test_admin_home(self):
        response = self.client.post(reverse('base:login'), {'username': 'admin', 'password': 'password123'})
        self.assertEqual(response.status_code, 200)
    # def test_admin_home(self):
    #     self.client.login(username='admin', password='password123')
    #     response = self.client.get(reverse('base:admin-home'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, 'Admin logged in')
    #     self.assertContains(response, 'Test School')


# class StaffTest(TestCase):
#     def test_staff_home(self):
#         response = self.client.get(reverse('base:staff-home'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, 'Staff logged in')
#         self.assertContains(response, 'Test School')       