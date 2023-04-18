from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.urls import reverse
from base.models import Admin, School, School, Staff, Admin
from base.forms import AdminRegistrationForm, StaffRegistrationForm, ReviewForm, UploadCsvForm, LetterForm
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
import io, csv





class AdminRegistrationFormTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name="Asja Boys College")
        self.form_data = {
            'school': self.school,
            'email': 'asjaadmin@gmail.com',
            'username' : 'asjaadmin',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }
    def test_valid_form_data(self):
        form = AdminRegistrationForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        admin = form.save()
        self.assertEqual(admin.user.first_name, 'John')
        self.assertEqual(admin.user.last_name, 'Doe')
        self.assertEqual(admin.user.username, 'asjaadmin')
        self.assertEqual(admin.user.email, 'asjaadmin@gmail.com')
        self.assertTrue(admin.user.check_password('testpassword'))
        self.assertEqual(admin.school, self.school)
        group = Group.objects.get(name='ADMIN')
        self.assertTrue(group in admin.user.groups.all())

    def test_password_mismatch(self):
        self.form_data['password2'] = 'differentpassword'
        form = AdminRegistrationForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertIn('password2', form.errors)

    def test_form_username_already_exists(self):
        user = User.objects.create_user(
            email='asjaadmin@gmail.com',
            username='asjaadmin',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        form = AdminRegistrationForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['A user with that username already exists.'])

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

    

class StaffRegistrationFormTest(TestCase):

    def setUp(self):
        self.school = School.objects.create(name="Test School")
        self.form_data = {'first_name': 'Test',
                     'last_name': 'User',
                     'username': 'testuser',
                     'email': 'testuser@example.com',
                     'password1': 'test_password',
                     'password2': 'test_password',
                     'school': self.school.id}        

    def test_form_valid_data(self):
        form = StaffRegistrationForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        staff = form.save()
        self.assertEqual(staff.user.first_name, 'Test')
        self.assertEqual(staff.user.last_name, 'User')
        self.assertEqual(staff.user.username, 'testuser')
        self.assertEqual(staff.user.email, 'testuser@example.com')
        self.assertTrue(staff.user.check_password('test_password'))
        self.assertEqual(staff.school, self.school)
        group = Group.objects.get(name='STAFF')
        self.assertTrue(group in staff.user.groups.all())


    def test_password_mismatch(self):
        self.form_data['password2'] = 'differentpassword'
        form = StaffRegistrationForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertIn('password2', form.errors)

    def test_form_email_already_exists(self):
        existing_user = User.objects.create_user(username='existing_user', email='testuser@example.com')
        form = StaffRegistrationForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Email already exists'])

    def test_form_missing_data(self):
        form_data = {
            'school': self.school.name,
            'email': 'asja@gmail.com'
        }
        form = StaffRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['first_name'], ['This field is required.'])
        self.assertEqual(form.errors['last_name'], ['This field is required.'])
        self.assertEqual(form.errors['password1'], ['This field is required.'])

class UploadCsvFormTest(TestCase):

    def test_upload_csv_form_valid(self):
        csv_file = SimpleUploadedFile("file.csv", b"file_content", content_type="text/csv")
        form_data = {'csv_file': csv_file}
        form = UploadCsvForm(data=form_data, files=form_data)
        self.assertTrue(form.is_valid())

    def test_upload_csv_form_missing_file(self):
        form_data = {}
        form = UploadCsvForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['csv_file'], ['This field is required.'])


class ReviewFormTests(TestCase):

    @classmethod
    def setUp(cls):
        cls.valid_form_data = {
            'text' : 'This is a test review that is at least fifty characters.',
            'rating' : '3'
        }

        cls.invalid_form_text = {
            'text' : 'Invalid.',
            'rating' : '3'
        }

        cls.invalid_form_rating = {
            'text' : 'This is a test review that is at least fifty characters.',
            'rating' : '10'
        }


    def test_valid_form(self):
        form = ReviewForm(data=self.valid_form_data)
        self.assertEqual({}, form.errors)
        self.assertTrue(form.is_valid())

    def test_invalid_form_text(self):
        form = ReviewForm(data=self.invalid_form_text)
        self.assertIn('text', form.errors)
        self.assertFalse(form.is_valid())

    def test_invalid_form_text(self):
        form = ReviewForm(data=self.invalid_form_rating)
        self.assertIn('rating', form.errors)
        self.assertFalse(form.is_valid())
        
    def test_blank_form(self):
        form = ReviewForm(data={})
        self.assertIn('rating', form.errors)
        self.assertIn('text',form.errors)
        self.assertFalse(form.is_valid())


class LetterFormTest(TestCase):
    def setUp(self):
        self.form_data = {'response': 'This is a test response.'}

    def test_form_valid(self):
        form = LetterForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        self.form_data['response'] = ''
        form = LetterForm(data=self.form_data)
        self.assertFalse(form.is_valid())