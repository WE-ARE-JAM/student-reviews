from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.urls import reverse
from base.models import Admin, School, School, Staff
from base.forms import AdminRegistrationForm, StaffRegistrationForm


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




class StaffRegistrationFormTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='ASJA')
    


class StaffRegistrationFormTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="PRES")
        self.valid_form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'pres@gmail.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'school': self.school.id
        }

    def test_valid_form(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'pres@gmail.com',
            'username': 'testuser',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'school': self.school.id,
        }
        form = StaffRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'pres@gmail.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.groups.count(), 1)
        self.assertEqual(user.groups.first().name, 'STAFF')
        staff = Staff.objects.get(user=user)
        self.assertEqual(staff.school, self.school)
    
    def test_invalid_form(self):
        form_data = {
            'first_name': '',
            'last_name': '',
            'email': 'invalidemail',
            'username': '',
            'password1': '',
            'password2': 'testpassword123',
            'school': '',
        }
        form = StaffRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())



    def test_blank_form(self):
        form = StaffRegistrationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 7)

    def test_password_mismatch(self):
        form_data = self.valid_form_data.copy()
        form_data['password2'] = 'differentpassword'
        form = StaffRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertIn('password2', form.errors)

    def test_existing_email(self):
        user = User.objects.create_user(
            username='existinguser',
            password='existingpassword',
            email=self.valid_form_data['email'],
        )
        form = StaffRegistrationForm(data=self.valid_form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(len(form.errors['email']), 1)
        self.assertEqual(form.errors['email'][0], 'Email already exists')

    def test_group_added(self):
        form = StaffRegistrationForm(data=self.valid_form_data)
        user = form.save()
        staff_group = Group.objects.get(name='STAFF')
        self.assertTrue(user.groups.filter(name=staff_group.name).exists())

    def test_staff_created(self):
        form = StaffRegistrationForm(data=self.valid_form_data)
        user = form.save()
        staff = Staff.objects.get(user=user)
        self.assertEqual(staff.school, self.school)


