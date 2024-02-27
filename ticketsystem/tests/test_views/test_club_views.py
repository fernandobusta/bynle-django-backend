from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ticketsystem.models import User, Club, Follow

# CLUBS ==============================================================================================
class ClubViewSetTest(TestCase):
    """ Testing: ClubViewSet (Default router)
        Dependencies: User, Club
        Url Name: club-list, club-detail """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com', content='Test content.')
        self.client.force_authenticate(user=self.user)

    def test_retrieve_club_list(self):
        response = self.client.get(reverse('club-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Club')

    def test_retrieve_single_club(self):
        response = self.client.get(reverse('club-detail', kwargs={'pk': self.club.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Club')

class CreateClubViewTest(TestCase):
    """ Testing: CreateClubView
        Dependencies: User, Club
        Url Name: create-club """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.client.force_authenticate(user=self.user)

    def test_create_club(self):
        data = {
            'name': 'Test Club',
            'description': 'This is a test club.',
            'email': 'testclub@example.com',
            'content': 'Test content.',
            'club_admins': [self.user.id]
        }
        response = self.client.post(reverse('create-club'), data) 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Club')

    def test_create_club_with_existing_email(self):
        Club.objects.create(name='Existing Club', description='This is an existing club.', email='existingclub@example.com', content='Existing content.')
        data = {
            'name': 'Test Club',
            'description': 'This is a test club.',
            'email': 'existingclub@example.com',
            'content': 'Test content.'
        }
        response = self.client.post(reverse('create-club'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ClubUpdateViewTest(TestCase):
    """ Testing: ClubUpdateView
        Dependencies: User, Club
        Url Name: update-club """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com', content='Test content.')
        self.client.force_authenticate(user=self.user)

    def test_update_club(self):
        data = {
            'name': 'Updated Club',
            'description': 'This is an updated club.',
            'email': 'updatedclub@example.com',
            'content': 'Updated content.'
        }
        response = self.client.patch(reverse('update-club', kwargs={'club_id': self.club.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Club')
        self.assertEqual(response.data['description'], 'This is an updated club.')
        self.assertEqual(response.data['email'], 'updatedclub@example.com')
        self.assertEqual(response.data['content'], 'Updated content.')

    def test_update_nonexistent_club(self):
        data = {
            'name': 'Updated Club',
            'description': 'This is an updated club.',
            'email': 'updatedclub@example.com',
            'content': 'Updated content.'
        }
        response = self.client.patch(reverse('update-club', kwargs={'club_id': 999}), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# CLUB ADMINS ========================================================================================
class ClubAdminViewTest(TestCase):
    """ Testing: ClubAdminView
        Dependencies: User, Club
        Url Name: user-admins-club """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com', content='Test content.')
        self.club.club_admins.add(self.user)
        self.client.force_authenticate(user=self.user)

    def test_user_is_club_admin(self):
        response = self.client.get(reverse('user-admins-club', kwargs={'user_id': self.user.id, 'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, True)

    def test_user_is_not_club_admin(self):
        other_user = User.objects.create_user(username='otheruser', email='otheruser@example.com', password='testpass', user_type='user')
        response = self.client.get(reverse('user-admins-club', kwargs={'user_id': other_user.id, 'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, False)

class ClubsAdminedByUserViewTest(TestCase):
    """ Testing: ClubsAdminedByUserView
        Dependencies: User, Club
        Url Name: user-admins """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com', content='Test content.')
        self.club.club_admins.add(self.user)
        self.client.force_authenticate(user=self.user)

    def test_retrieve_clubs_admined_by_user(self):
        response = self.client.get(reverse('user-admins', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Club')

class AdminsInClubViewTest(TestCase):
    """ Testing: AdminsInClubView
        Dependencies: User, Club
        Url Name: club-admins """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com', content='Test content.')
        self.club.club_admins.add(self.user)
        self.client.force_authenticate(user=self.user)

    def test_retrieve_admins_in_club(self):
        response = self.client.get(reverse('club-admins', kwargs={'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'testuser')

class RemoveClubAdminViewTest(TestCase):
    """ Testing: RemoveClubAdminView
        Dependencies: User, Club
        Url Name: remove-club-admin """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com')
        self.club.club_admins.add(self.user)
        self.client.force_authenticate(user=self.user)

    def test_remove_club_admin(self):
        response = self.client.delete(reverse('remove-club-admin', kwargs={'username': self.user.username, 'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn(self.user, self.club.club_admins.all())

    def test_remove_nonexistent_club_admin(self):
        other_user = User.objects.create_user(username='otheruser', email='otheruser@example.com', password='testpass')
        response = self.client.delete(reverse('remove-club-admin', kwargs={'username': other_user.username, 'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

# 
class AddClubAdminViewTest(TestCase):
    """ Testing: AddClubAdminView
        Dependencies: User, Club
        Url Name: add-club-admin """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.other_user = User.objects.create_user(username='otheruser', email='otheruser@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com')
        self.client.force_authenticate(user=self.user)

    def test_add_club_admin(self):
        data = {
            'usernames': ('otheruser',)
        }
        response = self.client.post(reverse('add-club-admin', kwargs={'club_id': self.club.id}), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(self.other_user, self.club.club_admins.all())

    def test_add_nonexistent_club_admin(self):
        data = {
            'usernames': ['nonexistentuser']
        }
        response = self.client.post(reverse('add-club-admin', kwargs={'club_id': self.club.id}), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# FOLLOWS ============================================================================================
class FollowViewSetTest(TestCase):
    """ Testing: FollowViewSet (Default router)
        Dependencies: User, Club, Follow
        Url Name: follow-list, follow-detail """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com')
        self.client.force_authenticate(user=self.user)

    def test_follow_club(self):
        data = {
            'user': self.user.id,
            'club': self.club.id
        }
        response = self.client.post(reverse('follow-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Follow.objects.filter(user=self.user, club=self.club).exists())

    def test_follow_club_already_followed(self):
        Follow.objects.create(user=self.user, club=self.club)
        data = {
            'user': self.user.id,
            'club': self.club.id
        }
        response = self.client.post(reverse('follow-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserFollowsClubViewTest(TestCase):
    """ Testing: UserFollowsClubView
        Dependencies: User, Club, Follow
        Url Name: user-follows-club """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com')
        self.client.force_authenticate(user=self.user)

    def test_user_follows_club(self):
        Follow.objects.create(user=self.user, club=self.club)
        response = self.client.get(reverse('user-follows-club', kwargs={'user_id': self.user.id, 'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, True)

    def test_user_does_not_follow_club(self):
        response = self.client.get(reverse('user-follows-club', kwargs={'user_id': self.user.id, 'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, False)

    def test_delete_follow(self):
        Follow.objects.create(user=self.user, club=self.club)
        response = self.client.delete(reverse('user-follows-club', kwargs={'user_id': self.user.id, 'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Follow.objects.filter(user=self.user, club=self.club).exists())

    def test_delete_nonexistent_follow(self):
        response = self.client.delete(reverse('user-follows-club', kwargs={'user_id': self.user.id, 'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserFollowsViewTest(TestCase):
    """ Testing: UserFollowsView
        Dependencies: User, Club, Follow
        Url Name: user-follows """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com')
        self.client.force_authenticate(user=self.user)

    def test_user_follows(self):
        Follow.objects.create(user=self.user, club=self.club)
        response = self.client.get(reverse('user-follows', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Club')

    def test_user_does_not_follow_any_clubs(self):
        response = self.client.get(reverse('user-follows', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

class CommonClubsViewTest(TestCase):
    """ Testing: CommonClubsView
        Dependencies: User, Club, Follow
        Url Name: common-followed-clubs """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
        self.club1 = Club.objects.create(name='Test Club 1', description='This is a test club.', email='testclub1@example.com')
        self.club2 = Club.objects.create(name='Test Club 2', description='This is a test club.', email='testclub2@example.com')
        Follow.objects.create(user=self.user1, club=self.club1)
        Follow.objects.create(user=self.user2, club=self.club1)
        Follow.objects.create(user=self.user2, club=self.club2)

    def test_common_clubs(self):
        response = self.client.get(reverse('common-followed-clubs', kwargs={'user_id1': self.user1.id, 'username2': self.user2.username}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Club 1')

    def test_no_common_clubs(self):
        user3 = User.objects.create_user(username='testuser3', email='testuser3@example.com', password='testpass')
        response = self.client.get(reverse('common-followed-clubs', kwargs={'user_id1': self.user1.id, 'username2': user3.username}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)