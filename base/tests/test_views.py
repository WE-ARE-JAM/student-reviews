from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from base.models import School, Admin, Staff, Student


class TestViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.admin_group = Group.objects.create(name='ADMIN')
        cls.staff_group = Group.objects.create(name='STAFF')
        cls.school = School.objects.create(name='Test School')

        cls.admin_user = User.objects.create_user(
            first_name = 'Test',
            last_name = 'Admin',
            username='admin',  
            email='admin@test.com', 
            password='password123'
        )

        cls.admin_user.groups.add(cls.admin_group)

        cls.admin = Admin.objects.create(
            user=cls.admin_user, 
            school=cls.school
        )

        cls.staff_user = User.objects.create_user(
            first_name = 'Test',
            last_name = 'Staff',
            username='staff', 
            email='staff@test.com', 
            password='password123'
        )
        cls.staff_user.groups.add(cls.staff_group)

        cls.staff = Staff.objects.create(
            user=cls.staff_user, 
            school=cls.school
        )
        print('User count', User.objects.count())
        print('Admin count', Admin.objects.count())
        print('Staff count', Staff.objects.count())

    def test_admin_login_view(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('base:admin-home'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_staff_login_view(self):
        self.client.login(username='staff', password='password123')
        response = self.client.get(reverse('base:staff-home'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_staff_registration_view(self):
        self.client.get(reverse('base:register'))
        response = self.client.post(reverse('base:register'), {
            'first_name' : 'Test',
            'last_name' : 'Stafftwo',
            'username' :'staff2',  
            'email' : 'staff2@test.com', 
            'password' : 'password123',
            'school' : self.school
            }
        )
        print(response)
        self.assertRedirects(response, reverse('base:login'))
        self.client.post(reverse('base:login'), 
            {
                'username': 'staff2', 
                'password': 'password123'
            }
        )
        response = self.client.get(reverse('base:staff-home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Staff.objects.count(), 2)


# def test_staff_registration_view(self):
    #     response = self.client.post(reverse('base:register'), {
    #         'username' :'staff2',  
    #         'email' : 'staff2@test.com', 
    #         'password' : 'password123'
    #         }
    #     )
    #     self.assertRedirects(response, reverse('base:login'))
    #     self.assertEqual(User.objects.count(), 3)
    #     self.assertEqual(Staff.objects.count(), 2)

    # def test_admin_login_view(self):
    #     # admin login, redirect to admin-home
    #     response = self.client.post(reverse('base:login'), 
    #         {
    #             'username': 'admin', 
    #             'password': 'password123'
    #         }
    #     )
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse('base:admin-home'))

    # def test_staff_login_view(self):
    #     # staff login, redirect to staff-home
    #     response = self.client.post(reverse('base:login'), 
    #         {
    #             'username': 'staff', 
    #             'password': 'password123'
    #         }
    #     )
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse('base:staff-home'))

    # def test_staff_registration_view(self):
    #     response = self.client.post(reverse('base:register'), {
    #         'username' :'staff2',  
    #         'email' : 'staff2@test.com', 
    #         'password' : 'password123'
    #         }
    #     )
    #     self.assertRedirects(response, reverse('base:login'))
    #     self.assertEqual(User.objects.count(), 3)
    #     self.assertEqual(Staff.objects.count(), 2)




   