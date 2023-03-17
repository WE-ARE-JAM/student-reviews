from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.urls import reverse
from base.models import Admin, School
from base.forms import AdminRegistrationForm

class AdminModelTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='Test School')
        self.user = User.objects.create_user(
            email='asja@gmail.com',
            username='user',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        self.admin = Admin.objects.create(user=self.user, school=self.school)

    def test_str(self):
        self.assertEqual(str(self.admin), 'Test User : Test School')

    def test_user_deletion_cascades(self):
        self.user.delete()
        self.assertFalse(Admin.objects.filter(pk=self.admin.pk).exists())