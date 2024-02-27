from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ticketsystem.models import User, Profile, Friend

class FriendViewSetTest(TestCase):
    """ Testing: FriendViewSet (Default router)
        Dependencies: User, Profile, Friend
        Url Name: friend-list, friend-detail """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
        self.user1.profile.course = 'Test Course'
        self.user1.profile.year = 1
        self.user1.profile.verified = True
        self.user1.profile.description = 'Test Description'
        self.user1.profile.save()
        self.user2.profile.course = 'Test Course'
        self.user2.profile.year = 1
        self.user2.profile.verified = True
        self.user2.profile.description = 'Test Description'
        self.user2.profile.save()
        Friend.objects.create(sender=self.user1, receiver=self.user2, status=True)
        self.client.force_authenticate(user=self.user1)

    def test_get_friend_requests(self):
        response = self.client.get(reverse('friend-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['receiver'], self.user2.id)

    def test_get_friend_request_detail(self):
        friend_request = Friend.objects.get(sender=self.user1, receiver=self.user2)
        response = self.client.get(reverse('friend-detail', kwargs={'pk': friend_request.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['receiver'], self.user2.id)

    def test_create_friend_request(self):
        user3 = User.objects.create_user(username='testuser3', email='testuser3@example.com', password='testpass')
        user3.profile.course = 'Test Course'
        user3.profile.year = 1
        user3.profile.verified = True
        user3.profile.description = 'Test Description'
        user3.profile.save()
        data = {
            'sender': self.user1.id,
            'receiver': user3.id,
            'status': False  # Pending friend request
        }
        response = self.client.post(reverse('friend-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Friend.objects.count(), 2)
        self.assertEqual(Friend.objects.get(id=response.data['id']).receiver.username, 'testuser3')

    def test_delete_friend_request(self):
        friend_request = Friend.objects.get(sender=self.user1, receiver=self.user2)
        response = self.client.delete(reverse('friend-detail', kwargs={'pk': friend_request.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Friend.objects.count(), 0)

class UserFriendsTest(TestCase):
    """ Testing: UserFriendsView
        Dependencies: User, Profile, Friend
        Url Name: user-friends """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
        self.user3 = User.objects.create_user(username='testuser3', email='testuser3@example.com', password='testpass')
        self.user1.profile.course = 'Test Course'
        self.user1.profile.year = 1
        self.user1.profile.verified = True
        self.user1.profile.description = 'Test Description'
        self.user1.profile.save()
        self.user2.profile.course = 'Test Course'
        self.user2.profile.year = 1
        self.user2.profile.verified = True
        self.user2.profile.description = 'Test Description'
        self.user2.profile.save()
        self.user3.profile.course = 'Test Course'
        self.user3.profile.year = 1
        self.user3.profile.verified = True
        self.user3.profile.description = 'Test Description'
        self.user3.profile.save()
        Friend.objects.create(sender=self.user1, receiver=self.user2, status=True)  # Accepted friend request
        Friend.objects.create(sender=self.user3, receiver=self.user1, status=False)  # Pending friend request
        self.client.force_authenticate(user=self.user1)

    def test_get_accepted_friends(self):
        response = self.client.get(reverse('user-friends', kwargs={'user_id': self.user1.id, 'friendship_status': 'accepted'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'testuser2')

    def test_get_pending_friends(self):
        response = self.client.get(reverse('user-friends', kwargs={'user_id': self.user1.id, 'friendship_status': 'pending'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'testuser3')

    def test_get_invalid_friendship_status(self):
        response = self.client.get(reverse('user-friends', kwargs={'user_id': self.user1.id, 'friendship_status': 'invalid'}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CommonFriendsViewTest(TestCase):
    """ Testing: CommonFriendsView
        Dependencies: User, Profile, Friend
        Url Name: common-friends """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
        self.user3 = User.objects.create_user(username='testuser3', email='testuser3@example.com', password='testpass')
        self.user4 = User.objects.create_user(username='testuser4', email='testuser4@example.com', password='testpass')
        self.user1.profile.course = 'Test Course'
        self.user1.profile.year = 1
        self.user1.profile.verified = True
        self.user1.profile.description = 'Test Description'
        self.user1.profile.save()
        self.user2.profile.course = 'Test Course'
        self.user2.profile.year = 1
        self.user2.profile.verified = True
        self.user2.profile.description = 'Test Description'
        self.user2.profile.save()
        self.user3.profile.course = 'Test Course'
        self.user3.profile.year = 1
        self.user3.profile.verified = True
        self.user3.profile.description = 'Test Description'
        self.user3.profile.save()
        self.user4.profile.course = 'Test Course'
        self.user4.profile.year = 1
        self.user4.profile.verified = True
        self.user4.profile.description = 'Test Description'
        self.user4.profile.save()
        Friend.objects.create(sender=self.user1, receiver=self.user2, status=True)  # Accepted friend request
        Friend.objects.create(sender=self.user1, receiver=self.user3, status=True)  # Accepted friend request
        Friend.objects.create(sender=self.user2, receiver=self.user3, status=True)  # Accepted friend request
        Friend.objects.create(sender=self.user2, receiver=self.user4, status=True)  # Accepted friend request
        self.client.force_authenticate(user=self.user1)

    def test_get_common_friends(self):
        response = self.client.get(reverse('common-friends', kwargs={'user_id1': self.user1.id, 'username2': 'testuser2'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'testuser3')

class CreateFriendRequestTest(TestCase):
    """ Testing: CreateFriendRequest
        Dependencies: User, Profile, Friend
        Url Name: create-friend-request """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
        self.user1.profile.course = 'Test Course'
        self.user1.profile.year = 1
        self.user1.profile.verified = True
        self.user1.profile.description = 'Test Description'
        self.user1.profile.save()
        self.user2.profile.course = 'Test Course'
        self.user2.profile.year = 1
        self.user2.profile.verified = True
        self.user2.profile.description = 'Test Description'
        self.user2.profile.save()
        self.client.force_authenticate(user=self.user1)

    def test_create_friend_request(self):
        data = {
            'sender': self.user1.id,
            'receiver': 'testuser2'
        }
        response = self.client.post(reverse('create-friend-request'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Friend.objects.count(), 1)
        self.assertEqual(Friend.objects.get().receiver.username, 'testuser2')

    def test_create_friend_request_same_user(self):
        data = {
            'sender': self.user1.id,
            'receiver': 'testuser1'
        }
        response = self.client.post(reverse('create-friend-request'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_friend_request_already_exists(self):
        Friend.objects.create(sender=self.user1, receiver=self.user2, status=False)  # Pending friend request
        data = {
            'sender': self.user1.id,
            'receiver': 'testuser2'
        }
        response = self.client.post(reverse('create-friend-request'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_friend_request(self):
        Friend.objects.create(sender=self.user2, receiver=self.user1, status=False)  # Pending friend request
        data = {
            'sender': self.user1.id,
            'receiver': 'testuser2'
        }
        response = self.client.post(reverse('create-friend-request'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Friend.objects.count(), 1)
        self.assertEqual(Friend.objects.get().status, True)

class ManageFriendshipTest(TestCase):
    """ Testing: ManageFriendship
        Dependencies: User, Profile, Friend
        Url Name: manage-friendship """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
        self.client.force_authenticate(user=self.user1)

    def test_get_friendship_status(self):
        Friend.objects.create(sender=self.user1, receiver=self.user2, status=True)  # Accepted friend request
        response = self.client.get(reverse('manage-friendship', kwargs={'user1': self.user1.id, 'username2': 'testuser2'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Friends')
        self.assertEqual(response.data['status'], 'True')
        self.assertEqual(response.data['sender'], 'current')

    def test_accept_friend_request(self):
        Friend.objects.create(sender=self.user2, receiver=self.user1, status=False)  # Pending friend request
        response = self.client.post(reverse('manage-friendship', kwargs={'user1': self.user1.id, 'username2': 'testuser2'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Friend.objects.get().status, True)

    def test_delete_friendship(self):
        Friend.objects.create(sender=self.user1, receiver=self.user2, status=True)  # Accepted friend request
        response = self.client.delete(reverse('manage-friendship', kwargs={'user1': self.user1.id, 'username2': 'testuser2'}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Friend.objects.count(), 0)