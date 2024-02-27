from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from ticketsystem.models import User, Club, Event, Ticket

from unittest.mock import patch

class TicketViewSetTest(APITestCase):
    """ Testing: TicketViewSet (Default router)
        Dependencies: Ticket, User, Event
        Url Name: ticket-list, ticket-detail """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
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
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ticket(self):
        response = self.client.get(reverse('ticket-detail', kwargs={'pk': self.ticket.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.ticket.id)

    def test_retrieve_ticket_not_owner(self):
        other_user = User.objects.create_user(username='otheruser', email='otheruser@example.com', password='testpass')
        self.client.force_authenticate(user=other_user)
        response = self.client.get(reverse('ticket-detail', kwargs={'pk': self.ticket.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_ticket_existing(self):
        response = self.client.post(reverse('ticket-list'), {'user': 'testuser', 'event': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'A ticket already exists for this user')

class UserTicketsViewTest(APITestCase):
    """ Testing: UserTicketsView
        Dependencies: Ticket, User
        Url Name: user-tickets """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
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
        self.ticket1 = Ticket.objects.create(title='Test Ticket 1', code='1234567890', price=10.0, status='A', user=self.user, event=self.event1)
        self.ticket2 = Ticket.objects.create(title='Test Ticket 2', code='1234567540', price=10.0, status='A', user=self.user, event=self.event2)
        self.client.force_authenticate(user=self.user)


    def test_get_user_tickets(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('user-tickets', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'Test Ticket 1')
        self.assertEqual(response.data[1]['title'], 'Test Ticket 2')

class UserHasTicketViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
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
        self.ticket = Ticket.objects.create(title='Test Ticket', code='1234567890', price=10.0, status='A', user=self.user, event=self.event)
        self.client.force_authenticate(user=self.user)

    def test_user_has_ticket(self):
        response = self.client.get(reverse('user-has-ticket-for-event', kwargs={'user_id': self.user.id, 'event_id': self.event.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_ticket'], True)