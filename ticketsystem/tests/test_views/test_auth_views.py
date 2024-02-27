from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ticketsystem.models import User, Profile
from rest_framework_simplejwt.tokens import AccessToken



class UserTokenObtainPairViewTest(APITestCase):
    """ Testing: UserTokenObtainPairView
        Url Name: token_obtain_pair """
    def setUp(self):
        # Create a user and a profile
        self.user = User.objects.create_user(username='testuser', password='testpass', email='testuser@example.com', user_type='user', student_id='123456')
        # Update the user's profile
        self.user.profile.birthday = '2000-01-01'
        self.user.profile.course = 'Test Course'
        self.user.profile.year = 1
        self.user.profile.description = 'Test Description'
        self.user.profile.verified = True
        self.user.profile.save()

    def test_token_obtain_pair(self):
        data = {
            'username': 'testuser',
            'password': 'testpass',
            'email': 'testuser@example.com'
        }
        response = self.client.post(reverse('token_obtain_pair'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        access_token = AccessToken(response.data['access'])
        self.assertTrue('student_id' in access_token)
        self.assertTrue('first_name' in access_token)
        self.assertTrue('last_name' in access_token)
        self.assertTrue('profile_picture' in access_token)
        self.assertTrue('birthday' in access_token)
        self.assertTrue('course' in access_token)
        self.assertTrue('year' in access_token)
        self.assertTrue('description' in access_token)
        self.assertTrue('verified' in access_token)

class TicketScannerTokenObtainPairViewTest(APITestCase):
    """ Testing: TicketScannerTokenObtainPairView
        Url Name: token_ticket_scanner_obtain_pair """
    def setUp(self):
        # Create a ticket scanner user
        self.user = User.objects.create_user(username='testscanner', password='testpass', email='testuser@example.com', user_type='ticket_scanner')

    def test_token_obtain_pair(self):
        data = {
            'username': 'testscanner',
            'password': 'testpass',
            'email': 'testuser@example.com'
        }
        response = self.client.post(reverse('token_ticket_scanner_obtain_pair'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        access_token = AccessToken(response.data['access'])
        self.assertTrue('username' in access_token)
        self.assertTrue('email' in access_token)
        self.assertTrue('user_type' in access_token)

class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('auth_register')

    def test_register_passwords_dont_match(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'student_id': '123456',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword123',
            'password2': 'differentpassword',
            'profile': {
                'course': 'Test Course',
                'year': '1',
                'description': 'Test description',
            }
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 400)