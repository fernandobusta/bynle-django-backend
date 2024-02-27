from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ticketsystem.models import User, Club, Event, Ticket

class EventViewSetTest(TestCase):
    """ Testing: EventViewSet (Default router)
        Dependencies: Event, Club, User
        Url Name: event-list, event-detail """
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
        self.client.force_authenticate(user=self.user)

    def test_get_events(self):
        response = self.client.get(reverse('event-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Event')

    def test_get_event_detail(self):
        response = self.client.get(reverse('event-detail', kwargs={'pk': self.event.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Event')

    def test_create_event(self):
        data = {
        'title': 'New Event',
        'description': 'This is a new event.',
        'price': 10.0,
        'date': '2021-01-01',
        'time': '12:00:00',
        'capacity': 100,
        'location': 'New Location',
        'club': self.club.id
        }
        response = self.client.post(reverse('event-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Event.objects.get(id=response.data['id']).title, 'New Event')

    def test_update_event(self):
        data = {
            'title': 'Updated Event',
            'description': 'This is an updated event.',
            'price': 10.0,
            'date': '2021-01-01',
            'time': '12:00:00',
            'capacity': 100,
            'location': 'Updated Location',
            'club': self.club.id
        }
        response = self.client.put(reverse('event-detail', kwargs={'pk': self.event.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Event.objects.get(id=self.event.id).title, 'Updated Event')
    
    def test_partial_update_event(self):
        data = {
            'title': 'Updated Event',
            'description': 'This is an updated event.',
        }
        response = self.client.patch(reverse('event-detail', kwargs={'pk': self.event.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Event.objects.get(id=self.event.id).title, 'Updated Event')

    def test_delete_event(self):
        response = self.client.delete(reverse('event-detail', kwargs={'pk': self.event.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), 0)

class ClubEventsViewTest(TestCase):
    """ Testing: ClubEventsView
        Dependencies: Event, Club, User
        Url Name: club-events """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com')
        self.event = Event.objects.create(title='Test Event', description='This is a test event.', price=10.0, date='2022-01-01', time='12:00:00', location='Test Location', club=self.club)
        self.client.force_authenticate(user=self.user)

    def test_club_events(self):
        response = self.client.get(reverse('club-events', kwargs={'club_id': self.club.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Event')

    def test_club_no_events(self):
        club2 = Club.objects.create(name='Test Club 2', description='This is a test club.', email='testclub2@example.com')
        response = self.client.get(reverse('club-events', kwargs={'club_id': club2.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

class UserEventsViewTest(TestCase):
    """ Testing: UserEventsView
        Dependencies: Event, Club, User, Ticket
        Url Name: user-events """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com')
        self.event1 = Event.objects.create(title='Test Event 1', description='This is a test event.', price=10.0, date='2022-01-01', time='12:00:00', location='Test Location', club=self.club)
        self.event2 = Event.objects.create(title='Test Event 2', description='This is a test event.', price=10.0, date='2022-01-01', time='12:00:00', location='Test Location', club=self.club)
        Ticket.objects.create(title='Test Ticket 1', code='1234567890', price=10.0, status='A', user=self.user, event=self.event1)  # Active ticket
        Ticket.objects.create(title='Test Ticket 2', code='0987654321', price=10.0, status='U', user=self.user, event=self.event2)  # Used ticket
        self.client.force_authenticate(user=self.user)

    def test_user_events(self):
        response = self.client.get(reverse('user-events', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['active']), 1)
        self.assertEqual(len(response.data['used']), 1)
        self.assertEqual(response.data['active'][0]['title'], 'Test Event 1')
        self.assertEqual(response.data['used'][0]['title'], 'Test Event 2')

class EventSoldOutViewTest(TestCase):
    """ Testing: EventSoldOutView
        Dependencies: Event, Club, User, Ticket
        Url Name: event-soldout """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com')
        self.event = Event.objects.create(title='Test Event', description='This is a test event.', price=10.0, date='2022-01-01', time='12:00:00', location='Test Location', club=self.club, capacity=1)
        Ticket.objects.create(title='Test Ticket', code='1234567890', price=10.0, status='A', user=self.user, event=self.event)  # Sold ticket

    def test_event_sold_out(self):
        response = self.client.get(reverse('event-soldout', kwargs={'event_id': self.event.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['sold_out'], True)

    def test_event_not_sold_out(self):
        event2 = Event.objects.create(title='Test Event 2', description='This is a test event.', price=10.0, date='2022-01-01', time='12:00:00', location='Test Location', club=self.club, capacity=2)
        response = self.client.get(reverse('event-soldout', kwargs={'event_id': event2.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['sold_out'], False)

    def test_event_does_not_exist(self):
        response = self.client.get(reverse('event-soldout', kwargs={'event_id': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)