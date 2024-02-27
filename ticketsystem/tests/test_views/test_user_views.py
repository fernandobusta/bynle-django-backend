from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ticketsystem.models import User, Profile
from rest_framework.authtoken.models import Token

class UserViewSetTest(TestCase):
    """ Testing: UserViewSet (Default router)
        Dependencies: User
        Url Name: user-list, user-detail """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_list(self):
        response = self.client.get(reverse('user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'testuser')

    def test_retrieve_single_user(self):
        response = self.client.get(reverse('user-detail', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

class ProfileViewSetTest(TestCase):
    """ Testing: ProfileViewSet (Default router)
        Dependencies: User
        Url Name: profile-list, profile-detail """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.profile = Profile.objects.get(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_list(self):
        response = self.client.get(reverse('profile-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.user.id)

    def test_retrieve_single_profile(self):
        response = self.client.get(reverse('profile-detail', kwargs={'pk': self.profile.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)

class UserNameViewTest(TestCase):
    """ Testing: UserNameView
        Dependencies: User
        Url Name: public-usernames """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.client.force_authenticate(user=self.user)

    def test_retrieve_usernames(self):
        response = self.client.get(reverse('public-usernames'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'testuser')

    def test_retrieve_usernames_with_query_param(self):
        response = self.client.get(reverse('public-usernames'), {'username': 'testuser'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'testuser')

class UserPersonalProfileViewTest(TestCase):
    """ Testing: UserPersonalProfileView
        Dependencies: User, Profile
        Url Name: user-profile """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.profile = Profile.objects.get(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_retrieve_personal_profile(self):
        response = self.client.get(reverse('user-profile', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)

class UserPublicProfileViewTest(TestCase):
    """ Testing: UserPublicProfileView
        Dependencies: User, Profile
        Url Name: public-users """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.profile = Profile.objects.get(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_retrieve_public_profile(self):
        response = self.client.get(reverse('public-users', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_retrieve_nonexistent_public_profile(self):
        response = self.client.get(reverse('public-users', kwargs={'username': 'nonexistentuser'}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)