from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.urls import reverse
from base.models import Admin, School, Staff
from base.forms import AdminRegistrationForm

class AdminModelTests(TestCase):
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

    def test_str(self):
        self.assertEqual(str(self.admin), 'Test User : ASJA')

    def test_user_deletion_cascades(self):
        self.user.delete()
        self.assertFalse(Admin.objects.filter(pk=self.admin.pk).exists())


class StaffModelTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='ASJA')
        self.user = User.objects.create_user(
            username='johndoe',
            email='johndoe@gmail.com',
            password='testpassword123',
            first_name='John',
            last_name='Doe'
        )
        self.staff = Staff.objects.create(user=self.user, school=self.school)
    
    def test_staff_model_str(self):
        self.assertEqual(str(self.staff), 'John Doe : ASJA')
