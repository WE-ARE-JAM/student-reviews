from django.test import TestCase
from django.db import models
from django.contrib.auth.models import Group, User
from django.utils import timezone
from datetime import datetime
from django.urls import reverse
from base.models import Admin, School, Staff, Student, Review, Endorsement, EndorsementStats, Vote, Stats, Staff_Inbox, Activity
from base.forms import AdminRegistrationForm
from django.core.exceptions import ValidationError


#
#   ADMIN MODEL TESTS
#
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

#
#   STAFF MODEL TESTS
#
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
        self.assertEqual(str(self.staff), 'Test User : PRES')

    def test_staff_creation(self):
        self.assertEqual(self.staff.user.username, 'user')
        self.assertEqual(self.staff.school, self.school)
        self.assertEqual(str(self.staff), 'Test User : PRES')

#
#   STUDENT MODEL TESTS
#
class StudentModelTest(TestCase):
    @classmethod
    def setUp(cls):
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

#
#   REVIEW MODEL TESTS
#
class ReviewModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.school = School.objects.create(name='ASJA')
        cls.user = User.objects.create_user(
            username='asja',
            email='asja@gmail.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        cls.staff = Staff.objects.create(user=cls.user, school=cls.school)
        cls.student = Student.objects.create(name = "Jane Doe",school=cls.school)
        cls.review = Review.objects.create(staff=cls.staff, student=cls.student, text='This is a test review that is at least fifty characters.', rating=3, is_good=True)
        

    def test_review_string_representation(self):
        review_str = str(self.review)
        self.assertEqual(review_str, f'{timezone.localtime(self.review.created_at).strftime("%d/%m/%Y, %H:%M")} staff: {self.review.staff.user.get_full_name()} student: {self.review.student.name} text: {self.review.text} rating: {self.review.rating}')

    def test_review_text_max_length(self):
        max_length = self.review._meta.get_field('text').max_length
        self.assertEqual(max_length, 1000)

    def test_review_rating_default_value(self):
        default_rating = self.review._meta.get_field('rating').default
        self.assertEqual(default_rating, 3)

    def test_review_created_at_auto_now_add(self):
        created_at = self.review._meta.get_field('created_at')
        self.assertTrue(created_at.auto_now_add)

    def test_review_edited_default_value(self):
        default_edited = self.review._meta.get_field('edited').default
        self.assertFalse(default_edited)

    def test_review_deleted_default_value(self):
        default_deleted = self.review._meta.get_field('deleted').default
        self.assertFalse(default_deleted)

#
#   ENDORSEMENT MODEL TESTS
#
class EndorsementModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='ASJA')
        self.user = User.objects.create_user(
            username='asja',
            email='asja@gmail.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.staff = Staff.objects.create(user=self.user, school=self.school)
        self.student = Student.objects.create(name = "Jane Doe",school=self.school)
        self.endorsement = Endorsement.objects.create(leadership=True, respect=False, punctuality=True,
                                                       participation=False, teamwork=True, student=self.student,
                                                       staff=self.staff)

    def test_endorsement_attributes(self):
        self.assertEqual(self.endorsement.leadership, True)
        self.assertEqual(self.endorsement.respect, False)
        self.assertEqual(self.endorsement.punctuality, True)
        self.assertEqual(self.endorsement.participation, False)
        self.assertEqual(self.endorsement.teamwork, True)
        self.assertEqual(self.endorsement.student, self.student)
        self.assertEqual(self.endorsement.staff, self.staff)

    def test_endorsement_string_representation(self):
        self.assertEqual(str(self.endorsement), f"staff: {self.staff.user.get_full_name()} leadership: True respect: False punctuality: True participation: False teamwork: True")

    def test_endorsement_default_attributes(self):
        endorsement = Endorsement.objects.create(student=self.student, staff=self.staff)
        self.assertEqual(endorsement.leadership, False)
        self.assertEqual(endorsement.respect, False)
        self.assertEqual(endorsement.punctuality, False)
        self.assertEqual(endorsement.participation, False)
        self.assertEqual(endorsement.teamwork, False)

#
#   ENDORSEMENT STATS TESTS
#
class EndorsementStatsModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='ASJA')
        self.user = User.objects.create_user(
            username='asja',
            email='asja@gmail.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.staff = Staff.objects.create(user=self.user, school=self.school)
        self.student = Student.objects.create(name = "John Doe",school=self.school)
        Endorsement.objects.create(leadership=True, respect=False, punctuality=True,
                                    participation=False, teamwork=True, student=self.student,
                                    staff=self.staff)

    def test_endorsement_stats_attributes(self):
        endorsement_stats = EndorsementStats.objects.create(student=self.student)
        self.assertEqual(endorsement_stats.school, self.school)
        self.assertEqual(endorsement_stats.leadership, 1)
        self.assertEqual(endorsement_stats.respect, 0)
        self.assertEqual(endorsement_stats.punctuality, 1)
        self.assertEqual(endorsement_stats.participation, 0)
        self.assertEqual(endorsement_stats.teamwork, 1)

    def test_endorsement_stats_no_endorsements(self):
        student = Student.objects.create(name="Jane Doe", school=self.school)
        endorsement_stats = EndorsementStats.objects.create(student=student)
        self.assertEqual(endorsement_stats.leadership, 0)
        self.assertEqual(endorsement_stats.respect, 0)
        self.assertEqual(endorsement_stats.punctuality, 0)
        self.assertEqual(endorsement_stats.participation, 0)
        self.assertEqual(endorsement_stats.teamwork, 0)

#
#   VOTE MODEL TESTS
#
class VoteModelTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='ASJA')
        self.user = User.objects.create_user(
            username='asja',
            email='asja@gmail.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.staff = Staff.objects.create(user=self.user, school=self.school)
        self.student = Student.objects.create(name = "John Doe",school=self.school)
        self.review = Review.objects.create(staff=self.staff, student=self.student, text='This is a test review that is at least fifty characters.', rating=3, is_good=True)
    
    def test_vote_creation(self):
        vote = Vote.objects.create(staff=self.staff, review=self.review, value="UP")
        self.assertEqual(vote.staff, self.staff)
        self.assertEqual(vote.review, self.review)
        self.assertEqual(vote.value, "UP")
    
    def test_vote_string_representation(self):
        vote = Vote.objects.create(staff=self.staff, review=self.review, value="DOWN")
        self.assertEqual(str(vote), f'staff: {self.review.staff} review: {self.review} value: DOWN')

#
#   STATS MODEL TESTS
#
class StatsModelTest(TestCase):
    
    def setUp(self):
        self.school = School.objects.create(name='ASJA')
        self.user = User.objects.create_user(
            username='asja',
            email='asja@gmail.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.staff = Staff.objects.create(user=self.user, school=self.school)

        #student with votes on review
        self.student = Student.objects.create(name = "John Doe",school=self.school)
        self.review = Review.objects.create(staff=self.staff, student=self.student, text='This is a test review that is at least fifty characters.', rating=3, is_good=True)
        self.stats = Stats.objects.create(review=self.review)
        self.vote1 = Vote.objects.create(staff=self.staff, review=self.review, value='UP')
        self.vote2 = Vote.objects.create(staff=self.staff, review=self.review, value='DOWN')

        #student without votes on review
        self.student2 = Student.objects.create(name = "Jane Doe",school=self.school)
        self.review_empty = Review.objects.create(staff=self.staff, student=self.student2, text='This is a test review that is at least fifty characters.', rating=3, is_good=True)
        self.stats_empty = Stats.objects.create(review=self.review_empty)

    def test_upvotes(self):
        self.assertEqual(self.stats.upvotes, 1)
        
    def test_downvotes(self):
        self.assertEqual(self.stats.downvotes, 1)
        
    def test_upvotes_multiple_votes(self):
        Vote.objects.create(staff=self.staff, review=self.review, value='UP')
        self.assertEqual(self.stats.upvotes, 2)
        
    def test_downvotes_multiple_votes(self):
        Vote.objects.create(staff=self.staff, review=self.review, value='DOWN')
        self.assertEqual(self.stats.downvotes, 2)
        
    def test_upvotes_no_votes(self):
        self.assertEqual(self.stats_empty.upvotes, 0)
        
    def test_downvotes_no_votes(self):
        self.assertEqual(self.stats_empty.downvotes, 0)

#
#   STAFFINBOX MODEL TESTS
#
class StaffInboxTest(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='ASJA')
        self.user = User.objects.create_user(
            username='asja',
            email='asja@gmail.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.staff = Staff.objects.create(user=self.user, school=self.school)
        self.staff_inbox = Staff_Inbox.objects.create(staff=self.staff, message='Test message')

    def test_staff_inbox_str(self):
        self.assertEqual(str(self.staff_inbox), 'staff: Test User : ASJA message: Test message')

    def test_staff_inbox_staff(self):
        self.assertEqual(self.staff_inbox.staff, self.staff)

    def test_staff_inbox_message(self):
        self.assertEqual(self.staff_inbox.message, 'Test message')

#
#   ACTIVITY MODEL TESTS
#
class ActivityModelTestCase(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='ASJA')
        self.user = User.objects.create_user(
            username='asja',
            email='asja@gmail.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        self.staff = Staff.objects.create(user=self.user, school=self.school)

    def test_str_method(self):
        activity = Activity.objects.create(staff=self.staff, message='Some message', action='Some action')
        expected_output = '{} staff: {} message: {} action: {}'.format(
            timezone.localtime(activity.created_at).strftime('%d/%m/%Y, %H:%M'),
            self.staff,
            'Some message',
            'Some action'
        )
        self.assertEqual(str(activity), expected_output)
        
    def test_created_at(self):
        activity = Activity.objects.create(staff=self.staff, message='Some message', action='Some action')
        self.assertTrue(activity.created_at)
        
    def test_staff_foreign_key(self):
        activity = Activity.objects.create(staff=self.staff, message='Some message', action='Some action')
        self.assertEqual(activity.staff, self.staff)
        
    def test_message_field(self):
        activity = Activity.objects.create(staff=self.staff, message='Some message', action='Some action')
        self.assertEqual(activity.message, 'Some message')
        
    def test_action_field(self):
        activity = Activity.objects.create(staff=self.staff, message='Some message', action='Some action')
        self.assertEqual(activity.action, 'Some action')


