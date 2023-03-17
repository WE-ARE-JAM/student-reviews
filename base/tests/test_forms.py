from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.urls import reverse
from base.models import Admin, School
from base.forms import AdminRegistrationForm


class AdminRegistrationFormTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='ASJA Boys')
        self.form_data = {
            'school': self.school,
            'email': 'asja@gmail.com',
            'username' : 'test',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }

    def test_valid_form(self):
        form = AdminRegistrationForm(data=self.form_data)
        print(form.errors)
        self.assertTrue(form.is_valid())
        user = form.save()
        admin = Admin.objects.get(user=user)
        self.assertEqual(admin.school, self.school)
        self.assertTrue(user.groups.filter(name='ADMIN').exists())

    def test_missing_fields(self):
        form_data = {
            'school': self.school.name,
            'email': 'asja@gmail.com'
        }
        form = AdminRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)

    def test_passwords_not_matching(self):
        form_data = self.form_data.copy()
        form_data['password2'] = 'wrongpassword'
        form = AdminRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

