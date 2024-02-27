from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from ticketsystem.models import User, Club, Event, Ticket, TransferRequest
import json

class TransferRequestViewSetTest(APITestCase):
    """ Testing: TransferRequestViewSet (Default router)
        Dependencies: TransferRequest, User, Ticket, Club, Event
        Url Name: transferrequest-list, transferrequest-detail """
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
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
        self.ticket = Ticket.objects.create(title='Test Ticket 1', code='1234567890', price=10.0, status='A', user=self.user1, event=self.event)
        self.transfer_request = TransferRequest.objects.create(sender=self.user1, receiver=self.user2, ticket=self.ticket)
        self.client.force_authenticate(user=self.user1)

    def test_get_transfer_requests(self):
        self.client.login(username='testuser1', password='testpass')
        response = self.client.get(reverse('transferrequest-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['sender'], 'testuser1')
        self.assertEqual(response.data[0]['receiver'], 'testuser2')

class AvailableToTransferTicketsViewTest(APITestCase):
    """ Testing: AvailableToTransferTicketsView
        Dependencies: TransferRequest, User, Ticket, Club, Event
        Url Name: available-to-transfer-tickets"""
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com')
        self.event1 = Event.objects.create(
            title='Test Event 1', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.event2 = Event.objects.create(
            title='Test Event 2', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-02',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.ticket1 = Ticket.objects.create(title='Test Ticket 1', code='1234567890', price=10.0, status='A', user=self.user1, event=self.event1)
        self.ticket2 = Ticket.objects.create(title='Test Ticket 2', code='1234567891', price=10.0, status='A', user=self.user1, event=self.event2)
        self.transfer_request = TransferRequest.objects.create(sender=self.user1, receiver=self.user2, ticket=self.ticket1)

    def test_get_available_to_transfer_tickets(self):
        response = self.client.get(reverse('available-to-transfer-tickets', kwargs={'user_id': self.user1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Ticket 2')

class CreateTransferRequestTest(APITestCase):
    """ Testing: CreateTransferRequest
        Dependencies: TransferRequest, User, Ticket, Club, Event
        Url Name: create-transfer-request """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
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
        self.ticket = Ticket.objects.create(title='Test Ticket 1', code='1234567890', price=10.0, status='A', user=self.user1, event=self.event)

    def test_create_transfer_request(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'receiver': 'testuser2',
            'ticket': {'id': self.ticket.id}
        }
        response = self.client.post(reverse('create-transfer-request'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['sender'], 'testuser1')
        self.assertEqual(response.data['receiver'], 'testuser2')

class UserSentTransferRequestsViewTest(APITestCase):
    """ Testing: UserSentTransferRequestsView
        Dependencies: TransferRequest, User, Ticket, Club, Event
        Url Name: sent-transfer-requests """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
        self.user3 = User.objects.create_user(username='testuser3', email='testuser3@example.com', password='testpass')

        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com')
        self.event1 = Event.objects.create(
            title='Test Event 1', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.event2 = Event.objects.create(
            title='Test Event 2', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.event3 = Event.objects.create(
            title='Test Event 3', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.ticket1 = Ticket.objects.create(title='Test Ticket 1', code='1234567890', price=10.0, status='A', user=self.user1, event=self.event1)
        self.ticket2 = Ticket.objects.create(title='Test Ticket 2', code='1234567891', price=10.0, status='A', user=self.user1, event=self.event2)
        self.ticket3 = Ticket.objects.create(title='Test Ticket 3', code='1234567892', price=10.0, status='A', user=self.user1, event=self.event3)
        self.transfer_request1 = TransferRequest.objects.create(sender=self.user1, receiver=self.user2, ticket=self.ticket1, status='pending')
        self.transfer_request2 = TransferRequest.objects.create(sender=self.user1, receiver=self.user2, ticket=self.ticket2, status='accepted')
        self.transfer_request3 = TransferRequest.objects.create(sender=self.user1, receiver=self.user2, ticket=self.ticket3, status='declined')

    def test_get_sent_transfer_requests(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('sent-transfer-requests', kwargs={'user_id': self.user1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['pending_transfer_requests']), 1)
        self.assertEqual(len(response.data['accepted_transfer_requests']), 1)
        self.assertEqual(len(response.data['declined_transfer_requests']), 1)

class UserTransferRequestViewTest(APITestCase):
    """ Testing: UserTransferRequestView
        Dependencies: TransferRequest, User, Ticket, Club, Event
        Url Name: transfer-request """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
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
        self.ticket = Ticket.objects.create(title='Test Ticket 1', code='1234567890', price=10.0, status='A', user=self.user1, event=self.event)
        self.transfer_request = TransferRequest.objects.create(sender=self.user1, receiver=self.user2, ticket=self.ticket, status='pending')

    def test_get_user_transfer_requests(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('transfer-request', kwargs={'user_id': self.user2.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['sender'], 'testuser1')

class UserReceivedTransferRequestViewTest(APITestCase):
    """ Testing: UserReceivedTransferRequestView
        Dependencies: TransferRequest, User, Ticket, Club, Event
        Url Name: received-transfer-request """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com')
        self.event1 = Event.objects.create(
            title='Test Event 1', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.event2 = Event.objects.create(
            title='Test Event 2', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.ticket1 = Ticket.objects.create(title='Test Ticket 1', code='1234567890', price=10.0, status='A', user=self.user1, event=self.event1)
        self.ticket2 = Ticket.objects.create(title='Test Ticket 2', code='1234567891', price=10.0, status='A', user=self.user1, event=self.event2)
        self.transfer_request1 = TransferRequest.objects.create(sender=self.user1, receiver=self.user2, ticket=self.ticket1, status='pending')
        self.transfer_request2 = TransferRequest.objects.create(sender=self.user1, receiver=self.user2, ticket=self.ticket2, status='pending')

    def test_get_received_transfer_requests(self):
        response = self.client.get(reverse('received-transfer-request', kwargs={'user_id': self.user2.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['num_of_transfers'], 2)

class CanAcceptTransferViewTest(APITestCase):
    """ Testing: CanAcceptTransferView
        Dependencies: TransferRequest, User, Ticket, Club, Event
        Url Name: can-accept-transfer """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
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
        self.ticket = Ticket.objects.create(title='Test Ticket 1', code='1234567890', price=10.0, status='A', user=self.user1, event=self.event)
        self.transfer_request = TransferRequest.objects.create(sender=self.user1, receiver=self.user2, ticket=self.ticket, status='pending')

    def test_can_accept_transfer(self):
        response = self.client.get(reverse('can-accept-transfer', kwargs={'user_id': self.user2.id, 'transfer_id': self.transfer_request.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['can_accept_transfer'], True)

class AcceptTransferRequestTest(APITestCase):
    """ Testing: AcceptTransferRequest
        Dependencies: TransferRequest, User, Ticket, Club, Event
        Url Name: accept-transfer-request """
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='testuser1', email='testuser1@example.com', password='testpass')
        self.user2 = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass')
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
        self.ticket = Ticket.objects.create(title='Test Ticket 1', code='1234567890', price=10.0, status='A', user=self.user1, event=self.event)
        self.transfer_request = TransferRequest.objects.create(sender=self.user1, receiver=self.user2, ticket=self.ticket, status='pending')

    def test_accept_transfer_request(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(reverse('accept-transfer-request', kwargs={'request_id': self.transfer_request.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Transfer request accepted')
        self.assertTrue(Ticket.objects.filter(user=self.user2, event=self.event).exists())
        self.assertFalse(Ticket.objects.filter(id=self.ticket.id).exists())
        self.assertFalse(TransferRequest.objects.filter(id=self.transfer_request.id).exists())