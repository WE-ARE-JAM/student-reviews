from django.test import TestCase
from django.db import models
from django.contrib.auth.models import Group, User
from django.urls import reverse
from base.models import Admin, School, Staff, Student, Review
from base.forms import AdminRegistrationForm
from django.core.exceptions import ValidationError

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

    def test_admin_user(self):
        self.assertEqual(self.admin.user, self.user)

    def test_admin_school(self):
        self.assertEqual(self.admin.school, self.school)

    def test_admin_delete(self):
        admin_id = self.admin.id
        self.admin.delete()
        self.assertFalse(Admin.objects.filter(id=admin_id).exists())


class StaffModelTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='PRES')
        self.user = User.objects.create_user(
            username='user',
            email='pres@gmail.com',
            password='testpass',
            first_name='Test',
            last_name='User'
        )
        self.staff = Staff.objects.create(user=self.user, school=self.school)
    
    def test_staff_model_str(self):
        self.assertEqual(str(self.staff), 'Test User : Pres')

    def test_staff_creation(self):
        self.assertEqual(self.staff.user.username, 'user')
        self.assertEqual(self.staff.school, self.school)
        self.assertEqual(str(self.staff), 'Test User : PRES')

class StudentModelTest(TestCase):
    @classmethod
    def setUp(self):
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


# class ReviewModelTest(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         cls.school = School.objects.create(name='ASJA')
#         cls.user = User.objects.create_user(
#             username='johndoe',
#             email='johndoe@gmail.com',
#             password='testpassword123',
#             first_name='John',
#             last_name='Doe'
#         )
#         cls.staff = Staff.objects.create(user=cls.user, school=cls.school)
#         cls.student = Student.objects.create(name = "Jane Doe",school=cls.school)
#         cls.review = Review.objects.create(staff=cls.staff, student=cls.student, text='This is a test review.', rating=3, is_good=True)
#         # school = School.objects.create(name='Test School')
#         # user = User.objects.create_user(username='testuser', password='12345')
#         # staff = Staff.objects.create(user=user, school=school)
#         # student = Student.objects.create(name='Test Student', school=school)
#         # cls.review = Review.objects.create(staff=cls.review.staff, student=cls.review.student, text='This is a test review.', rating=3, is_good=True)

#     def test_review_string_representation(self):
#         review_str = str(self.review)
#         self.assertEqual(review_str, f'staff: {self.review.staff.user.get_full_name()} student: {self.review.student.name} text: {self.review.text} rating: {self.review.rating}')

#     def test_review_text_max_length(self):
#         max_length = self.review._meta.get_field('text').max_length
#         self.assertEqual(max_length, 1000)

#     def test_review_text_min_length_validator(self):
#         with self.assertRaises(ValidationError):
#             Review.objects.create(staff=self.review.staff, student=self.review.student, text='This is a test.', rating=3, is_good=True)

#     def test_review_rating_default_value(self):
#         default_rating = self.review._meta.get_field('rating').default
#         self.assertEqual(default_rating, 3)

#     def test_review_is_good_null(self):
#         with self.assertRaises(TypeError):
#             Review.objects.create(staff=self.review.staff, student=self.review.student, text='This is a test review.', rating=3)

#     def test_review_created_at_auto_now_add(self):
#         created_at = self.review._meta.get_field('created_at')
#         self.assertTrue(created_at.auto_now_add)

#     def test_review_edited_default_value(self):
#         default_edited = self.review._meta.get_field('edited').default
#         self.assertFalse(default_edited)

#     def test_review_deleted_default_value(self):
#         default_deleted = self.review._meta.get_field('deleted').default
#         self.assertFalse(default_deleted)

