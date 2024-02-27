from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from ticketsystem.models import StripeAccount, Club, User, Profile, Ticket, TransferRequest, Event

from unittest.mock import patch, MagicMock

class StripeAccountClubViewTest(TestCase):
    """ Testing: StripeAccountClubView
        Dependencies: Club, User, StripeAccount
        Url Name: club-stripe-account """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club')
        self.stripe_account = StripeAccount.objects.create(stripe_id='stripe_123', stripe_connected=True, stripe_complete=True)
        self.club.stripe = self.stripe_account
        self.club.save()
        self.client.force_authenticate(user=self.user)

    def test_get_stripe_account(self):
        response = self.client.get(reverse('club-stripe-account', kwargs={'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stripe_id'], self.stripe_account.stripe_id)

    def test_get_stripe_account_no_stripe_account(self):
        self.club.stripe = None
        self.club.save()
        response = self.client.get(reverse('club-stripe-account', kwargs={'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'No Stripe account found for the club')

    def test_get_stripe_account_club_not_found(self):
        response = self.client.get(reverse('club-stripe-account', kwargs={'club_id': 999}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Club not found')

class StripeAccountUserViewTest(TestCase):
    """ Testing: StripeAccountUserView
        Dependencies: User, StripeAccount
        Url Name: user-stripe-account """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.stripe_account = StripeAccount.objects.create(stripe_id='stripe_123', stripe_connected=True, stripe_complete=True)
        self.user.profile.stripe = self.stripe_account
        self.user.profile.save()
        self.client.force_authenticate(user=self.user)

    def test_get_stripe_account(self):
        response = self.client.get(reverse('user-stripe-account', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stripe_id'], self.stripe_account.stripe_id)

    def test_get_stripe_account_no_stripe_account(self):
        self.user.profile.stripe = None
        self.user.profile.save()
        response = self.client.get(reverse('user-stripe-account', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'No Stripe account found for the user')

    def test_get_stripe_account_user_not_found(self):
        response = self.client.get(reverse('user-stripe-account', kwargs={'user_id': 999}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'User not found')

class StripeStatusViewTest(APITestCase):
    """ Testing: StripeStatusView
        Dependencies: Club, User, StripeAccount
        Url Name: stripe-status-club """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club')
        self.stripe_account = StripeAccount.objects.create(stripe_id='stripe_123', stripe_connected=True, stripe_complete=True)
        self.club.stripe = self.stripe_account
        self.club.save()
        self.client.force_authenticate(user=self.user)

    @patch('stripe.Account.retrieve')
    @patch('ticketsystem.utils.get_stripe_account_completion')  # Replace 'your_app' with your actual app name
    @patch('ticketsystem.utils.account_create_link')  # Replace 'your_app' with your actual app name
    def test_get_stripe_status_complete(self, mock_retrieve, mock_account_create_link, mock_get_stripe_account_completion):
        # Set up the mock objects
        mock_get_stripe_account_completion.return_value = {"payouts_enabled": True}
        mock_retrieve.return_value = MagicMock(stripe_id='stripe_123', stripe_connected=True, stripe_complete=True)

        # Run the test
        response = self.client.get(reverse('stripe-status-club', kwargs={'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Stripe account is complete')

    def test_get_stripe_status_no_stripe_account(self):
        self.club.stripe = None
        self.club.save()
        response = self.client.get(reverse('stripe-status-club', kwargs={'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'No Stripe account found for the club')

    def test_get_stripe_status_club_not_found(self):
        response = self.client.get(reverse('stripe-status-club', kwargs={'club_id': 999}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Club not found')


class StripeStatusUserViewTest(APITestCase):
    """ Testing: StripeStatusUserView
        Dependencies: Club, User, StripeAccount
        Url Name: stripe-status-user """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club')
        self.stripe_account = StripeAccount.objects.create(stripe_id='stripe_123', stripe_connected=True, stripe_complete=True)
        self.club.stripe = self.stripe_account
        self.club.save()
        self.client.force_authenticate(user=self.user)

    def test_get_stripe_status_no_stripe_account(self):
        self.user.profile.stripe = None
        self.user.profile.save()
        response = self.client.get(reverse('stripe-status-user', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'No Stripe account found for the user')

    def test_get_stripe_status_profile_not_found(self):
        response = self.client.get(reverse('stripe-status-user', kwargs={'user_id': 999}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Profile not found')

class CreateStripeUserCheckoutSessionTest(APITestCase):
    """ Testing: CreateStripeUserCheckoutSession
        Dependencies: User, StripeAccount, Club, Event, Ticket, TransferRequest
        Url Name: checkout-session-user """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.receiver = User.objects.create_user(username='receiver', email='receiver@example.com', password='testpass')
        self.stripe_account = StripeAccount.objects.create(stripe_id='stripe_123', stripe_connected=True, stripe_complete=True)
        self.user.profile.stripe = self.stripe_account
        self.user.profile.save()
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com')
        self.event = Event.objects.create(
            title='Test Event', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        
        self.ticket = Ticket.objects.create(title='Test Ticket 1', code='1234567890', price=10.0, status='A', user=self.user, event=self.event)
        self.transfer_request = TransferRequest.objects.create(id=1, ticket=self.ticket, sender=self.user, receiver=self.receiver)
        self.client.force_authenticate(user=self.user)

    @patch('stripe.PaymentIntent.create')
    def test_create_checkout_session(self, mock_create):
        mock_create.return_value = {'client_secret': 'secret123'}
        response = self.client.post(reverse('checkout-session-user'), {'transferRequestId': self.transfer_request.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['clientSecret'], 'secret123')

    @patch('stripe.PaymentIntent.create')
    def test_create_checkout_session_error(self, mock_create):
        mock_create.side_effect = Exception('Test error')
        response = self.client.post(reverse('checkout-session-user'), {'transferRequestId': self.transfer_request.id})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['detail'], 'Something went wrong')
        self.assertEqual(response.data['error'], 'Test error')

class CreateStripeCheckoutSessionTest(APITestCase):
    """ Testing: CreateStripeCheckoutSession
        Dependencies: User, StripeAccount, Club, Event, Ticket, TransferRequest
        Url Name: checkout-session """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.stripe_account = StripeAccount.objects.create(stripe_id='stripe_123', stripe_connected=True, stripe_complete=True)
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com', stripe=self.stripe_account)
        self.event = Event.objects.create(
            title='Test Event', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.client.force_authenticate(user=self.user)

    @patch('stripe.PaymentIntent.create')
    def test_create_checkout_session(self, mock_create):
        mock_create.return_value = {'client_secret': 'secret123'}
        response = self.client.post(reverse('checkout-session'), {'eventId': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['clientSecret'], 'secret123')

    @patch('stripe.PaymentIntent.create')
    def test_create_checkout_session_error(self, mock_create):
        mock_create.side_effect = Exception('Test error')
        response = self.client.post(reverse('checkout-session'), {'eventId': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['detail'], 'Something went wrong')
        self.assertEqual(response.data['error'], 'Test error')

class StripeSuccessViewTest(APITestCase):
    """ Testing: StripeSuccessView
        Dependencies: User, StripeAccount, Club
        Url Name: stripe-successful """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.stripe_account = StripeAccount.objects.create(stripe_id='stripe_123', stripe_connected=True, stripe_complete=True)
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com', stripe=self.stripe_account)
        self.client.force_authenticate(user=self.user)

    def test_stripe_success_club_not_found(self):
        response = self.client.get(reverse('stripe-successful', kwargs={'club_id': 999}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Club not found')

class StripeSuccessUserViewTest(APITestCase):
    """ Testing: StripeSuccessUserView
        Dependencies: User, StripeAccount, Club
        Url Name: stripe-successful-user """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.stripe_account = StripeAccount.objects.create(stripe_id='stripe_123', stripe_connected=True, stripe_complete=False)
        self.user.profile.stripe = self.stripe_account
        self.user.profile.save()
        self.client.force_authenticate(user=self.user)

    def test_stripe_success_user(self):
        response = self.client.get(reverse('stripe-successful-user', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Stripe account is complete')
        self.user.profile.refresh_from_db()
        self.assertTrue(self.user.profile.stripe.stripe_complete)

    def test_stripe_success_user_not_found(self):
        response = self.client.get(reverse('stripe-successful-user', kwargs={'user_id': 999}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Profile not found')

class CreateStripeAccountCustomTest(APITestCase):
    """ Testing: CreateStripeAccountCustom
        Dependencies: User, Club, StripeAccount
        Url Name: create_account_custom """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com')
        self.client.force_authenticate(user=self.user)
    def test_create_stripe_account_club_not_found(self):
        response = self.client.get(reverse('create_account_custom', kwargs={'club_id': 999}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Club not found')

class CreateStripeAccountExpressTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.client.force_authenticate(user=self.user)

    @patch('ticketsystem.utils.get_stripe_accountid')
    def test_create_stripe_account_existing(self, mock_get_stripe_accountid):
        mock_get_stripe_accountid.return_value = True
        response = self.client.get(reverse('create_account_express', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Email is already associated with a Stripe account.')