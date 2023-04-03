from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.http import urlencode
from base.models import Review
from base.views import staff_home, student_profile, create_review
import base.urls

class HomepageTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='ASJA')
        self.user = User.objects.create_user(
            email='asja@gmail.com',
            username='user',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        self.admin = Admin.objects.create(user=self.user, school=self.school)
        


    def test_login_available_by_name(self):
        response = self.client.get(reverse('base:login'))
        self.assertEqual(response.status_code, 200)
    
    def test_staff_register_available_by_name(self):
        response = self.client.get(reverse('base:register'))
        self.assertEqual(response.status_code, 200)
