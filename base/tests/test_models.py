from django.test import TestCase
from django.db import models
from django.contrib.auth.models import Group, User
from django.urls import reverse
from base.models import Admin, School, Staff, Student
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


class StudentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.school = School.objects.create(name='Test School')
        cls.student = Student.objects.create(name='John Doe', school=cls.school)

    def test_name_label(self):
        student = StudentModelTest.student
        field_label = student._meta.get_field('name').verbose_name
        self.assertEquals(field_label, 'name')

    def test_active_default(self):
        student = StudentModelTest.student
        self.assertTrue(student.active)

    def test_profile_pic_null(self):
        student = StudentModelTest.student
        self.assertTrue(student._meta.get_field('profile_pic').null)

    def test_str_method(self):
        student = StudentModelTest.student
        expected_string = f"{student.name} : {student.school.name}"
        self.assertEquals(str(student), expected_string)

    def test_school_foreign_key(self):
        student = StudentModelTest.student
        self.assertIsInstance(student._meta.get_field('school'), models.ForeignKey)
        self.assertEquals(student.school, StudentModelTest.school)
    



