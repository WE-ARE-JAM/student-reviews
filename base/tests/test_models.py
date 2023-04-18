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

    def test_admin_created(self):
        self.assertIsInstance(self.admin, Admin)

    def test_admin_user(self):
        self.assertEqual(self.admin.user, self.user)    

    def test_admin_school(self):
        self.assertEqual(self.admin.school, self.school)

    def test_admin_str(self):
        self.assertEqual(str(self.admin), 'Test User : ASJA')

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
    def test_staff_created(self):
        self.assertIsInstance(self.staff, Staff)
    
    def test_staff_user(self):
        self.assertEqual(self.staff.user, self.user)
    
    def test_staff_school(self):
        self.assertEqual(self.staff.school, self.school)

    def test_staff_model_str(self):
        self.assertEqual(str(self.staff), 'Test User : PRES')

    def test_staff_delete(self):
        staff_id = self.staff.id
        self.staff.delete()
        self.assertFalse(Staff.objects.filter(id=staff_id).exists())

#
#   STUDENT MODEL TESTS
#
class StudentModelTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.school = School.objects.create(name='Pres')
        cls.student = Student.objects.create(name='John Doe', school=cls.school)

    def test_student_created(self):
        self.assertIsInstance(self.student, Student)

    def test_student_name(self):
        self.assertEqual("John Doe", self.student.name)

    def test_student_school(self):
        self.assertTrue(self.school, self.student.school)

    def test_str_method(self):
        self.assertEquals(str(self.student), 'John Doe : Pres')


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

    def test_review_created(self):
        self.assertIsInstance(self.review, Review)

    def test_review_staff(self):
        self.assertEqual(self.staff, self.review.staff)
    
    def test_review_student(self):
        self.assertEqual(self.student, self.review.student)
    
    def test_review_rating(self):
        self.assertEqual(3, self.review.rating)

    def test_review_str(self):
        review_str = str(self.review)
        self.assertEqual(str(self.review), f'{timezone.localtime(self.review.created_at).strftime("%d/%m/%Y, %H:%M")} staff: {self.review.staff.user.get_full_name()} student: {self.review.student.name} text: {self.review.text} rating: {self.review.rating}')

    def test_review_text_max_length(self):
        max_length = self.review._meta.get_field('text').max_length
        self.assertEqual(max_length, 1000)

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
        self.endorsement = Endorsement.objects.create(leadership=True, respect=False, punctuality=True, participation=False, teamwork=True, student=self.student, staff=self.staff)

    def test_endorsement_staff(self):
        self.assertEquals(self.staff, self.endorsement.staff)

    def test_endorsement_student(self):
        self.assertEqual(self.student, self.endorsement.student)

    def test_endorsement_attributes(self):
        self.assertEqual(self.endorsement.leadership, True)
        self.assertEqual(self.endorsement.respect, False)
        self.assertEqual(self.endorsement.punctuality, True)
        self.assertEqual(self.endorsement.participation, False)
        self.assertEqual(self.endorsement.teamwork, True)


    def test_endorsement_str(self):
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
        Endorsement.objects.create(leadership=True, respect=False, punctuality=True,participation=False, teamwork=True, student=self.student,staff=self.staff)

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
        self.vote = Vote.objects.create(staff=self.staff, review=self.review, value="UP")

    def test_vote_staff(self):
        self.assertEqual(self.vote.staff, self.staff)

    def test_vote_review(self):
        self.assertEqual(self.vote.review, self.review)

    def test_vote_value(self):
        self.assertEqual(self.vote.value, "UP")

    def test_vote_str(self):
        self.assertEqual(str(self.vote), f'staff: {self.review.staff} review: {self.review} value: UP')
    
    def test_vote_down(self):
        vote = Vote.objects.create(staff=self.staff, review=self.review, value="DOWN")
        self.assertEqual(vote.value, "DOWN")
    
    

#
#   STATS MODEL TESTS
#
class StatsModelTest(TestCase):
    
    def setUp(self):
        self.school = School.objects.create(name='ASJA')
        self.user = User.objects.create_user(
            username='staff1',
            email='staff2@gmail.com',
            password='testpassword',
            first_name='Staff',
            last_name='User'
        )

        self.user2 = User.objects.create_user(
            username='staff2',
            email='staff2@gmail.com',
            password='testpassword',
            first_name='Test',
            last_name='Staff'
        )

        self.staff = Staff.objects.create(user=self.user, school=self.school)
        self.staff2 = Staff.objects.create(user=self.user2, school=self.school)

        #student with votes on review
        self.student = Student.objects.create(name = "John Doe",school=self.school)
        self.review = Review.objects.create(staff=self.staff, student=self.student, text='This is a test review that is at least fifty characters.', rating=3, is_good=True)
        self.stats = Stats.objects.create(review=self.review)
        self.vote1 = Vote.objects.create(staff=self.staff, review=self.review, value='UP')

        #student without votes on review
        self.student2 = Student.objects.create(name = "Jane Doe",school=self.school)
        self.review_empty = Review.objects.create(staff=self.staff, student=self.student2, text='This is a test review that is at least fifty characters.', rating=3, is_good=True)
        self.stats_empty = Stats.objects.create(review=self.review_empty)

    def test_stats_review(self):
        self.assertEqual(self.review, self.stats.review)
    
    def test_stats_empty_review(self):
        self.assertEqual(self.review_empty, self.stats_empty.review)

    def test_upvotes(self):
        self.assertEqual(self.stats.upvotes, 1)

    def test_downvotes(self):
        self.assertEqual(self.stats.upvotes, 1)
        
    def test_upvotes_no_votes(self):
        self.assertEqual(self.stats_empty.upvotes, 0)
        
    def test_downvotes_no_votes(self):
        self.assertEqual(self.stats_empty.downvotes, 0)
    
    def test_multiple_upvotes(self):
        vote2 = Vote.objects.create(staff=self.staff, review=self.review_empty, value='UP')
        vote3 = Vote.objects.create(staff=self.staff2, review=self.review_empty, value='UP')
        self.assertEqual(self.stats_empty.upvotes, 2)

    def test_multiple_upvotes(self):
        vote2 = Vote.objects.create(staff=self.staff, review=self.review_empty, value='DOWN')
        vote3 = Vote.objects.create(staff=self.staff2, review=self.review_empty, value='DOWN')
        self.assertEqual(self.stats_empty.downvotes, 2)

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

    def test_staff_inbox_staff(self):
        self.assertEqual(self.staff_inbox.staff, self.staff)

    def test_staff_inbox_message(self):
        self.assertEqual(self.staff_inbox.message, 'Test message')

    def test_staff_inbox_str(self):
        self.assertEqual(str(self.staff_inbox), 'staff: Test User : ASJA message: Test message')




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
        self.activity = Activity.objects.create(user=self.user, message='Some message', parameter='NA')

    def test_activity_user(self):
        self.assertEqual(self.user, self.activity.user)
    
    def test_activity_message(self):
        self.assertEqual("Some message", self.activity.message)
    
    def test_activity_parameter(self):
        self.assertEqual("NA", self.activity.parameter)

    def test_str_method(self):
        expected_output = '{} user: {} message: {} parameter: {}'.format(
            timezone.localtime(self.activity.created_at).strftime('%d/%m/%Y, %H:%M'),
            self.user,
            'Some message',
            'NA'
        )
        self.assertEqual(str(self.activity), expected_output)
        
    def test_created_at(self):
        self.assertTrue(self.activity.created_at)


