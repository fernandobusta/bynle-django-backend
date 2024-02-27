from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from ticketsystem.models import User, Club, Event, Ticket

from datetime import timedelta

class CreateTicketScannerViewTest(TestCase):
    """ Testing: CreateTicketScannerView
        Dependencies: User, Club, Event
        Url Name: create-ticket-scanner """
    def setUp(self):
        self.client = APIClient()
        self.club_admin = User.objects.create_user(username='clubadmin', email='clubadmin@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club')
        self.club.club_admins.add(self.club_admin)
        self.event = Event.objects.create(
            title='Test Event', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.client.force_authenticate(user=self.club_admin)

    def test_create_ticket_scanner(self):
        data = {
            'username': 'ticketscanner',
            'password': 'testpass',
            'email': 'ticketscanner@example.com',
            'event_id': self.event.id
        }
        response = self.client.post(reverse('create-ticket-scanner'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(username='ticketscanner').user_type, 'ticket_scanner')
        self.assertEqual(User.objects.get(username='ticketscanner').event_id, self.event.id)

    def test_create_ticket_scanner_not_club_admin(self):
        user = User.objects.create_user(username='user', email='user@example.com', password='testpass')
        self.client.force_authenticate(user=user)
        data = {
            'username': 'ticketscanner',
            'password': 'testpass',
            'email': 'ticketscanner@example.com',
            'event_id': self.event.id
        }
        response = self.client.post(reverse('create-ticket-scanner'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TicketScannerUserPasswordResetViewTest(TestCase):
    """ Testing: TicketScannerUserPasswordResetView
        Dependencies: User, Club, Event
        Url Name: ticket-scanner-user-reset-password """
    def setUp(self):
        self.client = APIClient()
        self.club_admin = User.objects.create_user(username='clubadmin', email='clubadmin@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club')
        self.club.club_admins.add(self.club_admin)
        self.event = Event.objects.create(
            title='Test Event', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.ticket_scanner = User.objects.create_user(username='ticketscanner', email='ticketscanner@example.com', password='testpass', user_type='ticket_scanner', event=self.event)
        self.client.force_authenticate(user=self.club_admin)

    def test_reset_password(self):
        data = {
            'password': 'newpass'
        }
        response = self.client.put(reverse('ticket-scanner-user-reset-password', kwargs={'id': self.ticket_scanner.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket_scanner.refresh_from_db()
        self.assertTrue(self.ticket_scanner.check_password('newpass'))

    def test_reset_password_not_club_admin(self):
        user = User.objects.create_user(username='user', email='user@example.com', password='testpass')
        self.client.force_authenticate(user=user)
        data = {
            'password': 'newpass'
        }
        response = self.client.put(reverse('ticket-scanner-user-reset-password', kwargs={'id': self.ticket_scanner.id}), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TicketScannerUserListViewTest(TestCase):
    """ Testing: TicketScannerUserListView
        Dependencies: User, Club, Event
        Url Name: ticket-scanner-user-list """
    def setUp(self):
        self.client = APIClient()
        self.club_admin = User.objects.create_user(username='clubadmin', email='clubadmin@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club')
        self.club.club_admins.add(self.club_admin)
        self.event = Event.objects.create(
            title='Test Event', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.ticket_scanner = User.objects.create_user(username='ticketscanner', email='ticketscanner@example.com', password='testpass', user_type='ticket_scanner', event=self.event, created_by=self.club_admin)
        self.client.force_authenticate(user=self.club_admin)

    def test_list_ticket_scanner_users(self):
        response = self.client.get(reverse('ticket-scanner-user-list'), {'event_id': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'ticketscanner')

    def test_list_ticket_scanner_users_not_club_admin(self):
        user = User.objects.create_user(username='user', email='user@example.com', password='testpass')
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('ticket-scanner-user-list'), {'event_id': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TicketScannerUserDeleteViewTest(TestCase):
    """ Testing: TicketScannerUserDeleteView
        Dependencies: User, Club, Event
        Url Name: ticket-scanner-user-delete """
    def setUp(self):
        self.client = APIClient()
        self.club_admin = User.objects.create_user(username='clubadmin', email='clubadmin@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club')
        self.club.club_admins.add(self.club_admin)
        self.event = Event.objects.create(
            title='Test Event', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.ticket_scanner = User.objects.create_user(username='ticketscanner', email='ticketscanner@example.com', password='testpass', user_type='ticket_scanner', event=self.event, created_by=self.club_admin)
        self.client.force_authenticate(user=self.club_admin)

    def test_delete_ticket_scanner_user(self):
        response = self.client.delete(reverse('ticket-scanner-user-delete', kwargs={'id': self.ticket_scanner.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)

    def test_delete_ticket_scanner_user_not_club_admin(self):
        user = User.objects.create_user(username='user', email='user@example.com', password='testpass')
        self.client.force_authenticate(user=user)
        response = self.client.delete(reverse('ticket-scanner-user-delete', kwargs={'id': self.ticket_scanner.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class ValidateTicketViewTest(TestCase):
    """ Testing: ValidateTicketView
        Dependencies: User, Club, Event, Ticket
        Url Name: validate-ticket """
    def setUp(self):
        self.client = APIClient()
        self.club_admin = User.objects.create_user(username='clubadmin', email='clubadmin@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club')
        self.club.club_admins.add(self.club_admin)
        self.event = Event.objects.create(
            title='Test Event', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.ticket_scanner = User.objects.create_user(username='ticketscanner', email='ticketscanner@example.com', password='testpass', user_type='ticket_scanner', event=self.event, created_by=self.club_admin)
        self.ticket_user1 = User.objects.create_user(username='ticketuser1', email='ticketuser1@example.com', password='testpass', first_name='Ticket', last_name='User', student_id='123456')
        self.ticket = Ticket.objects.create(title='Test Ticket 1', code='1234567890', price=10.0, status='A', user=self.ticket_user1, event=self.event)
        self.client.force_authenticate(user=self.ticket_scanner)

    def test_validate_ticket(self):
        response = self.client.post(reverse('validate-ticket', kwargs={'ticket_id': self.ticket.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'U')
        self.assertEqual(self.ticket.scanned_by, self.ticket_scanner)

    def test_validate_ticket_not_ticket_scanner(self):
        self.client.force_authenticate(user=self.club_admin)
        response = self.client.post(reverse('validate-ticket', kwargs={'ticket_id': self.ticket.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_validate_ticket_from_another_event(self):
        another_event = Event.objects.create(
            title='Another Test Event', 
            description='This is another test event.', 
            price=10.0,
            date='2021-01-02',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.ticket_user2 = User.objects.create_user(username='ticketuser2', email='ticketuser2@example.com', password='testpass', first_name='Ticket', last_name='User', student_id='234567')
        another_ticket = Ticket.objects.create(title='Test Ticket 2', code='2345678901', price=10.0, status='A', user=self.ticket_user2, event=another_event)
        response = self.client.post(reverse('validate-ticket', kwargs={'ticket_id': another_ticket.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # This is removed because for the demo we will be testing with a 10 second time difference, tests have been ran and passed for 2 minutes

    # def test_validate_used_ticket_scanned_more_than_two_minutes_ago(self):
    #     self.ticket_user3 = User.objects.create_user(username='ticketuser3', email='ticketuser3@example.com', password='testpass', first_name='Ticket', last_name='User', student_id='345678')
    #     used_ticket = Ticket.objects.create(title='Test Ticket 3', code='3456789012', price=10.0, status='U', user=self.ticket_user3, event=self.event, scanned_at=timezone.now() - timedelta(minutes=3))
    #     response = self.client.post(reverse('validate-ticket', kwargs={'ticket_id': used_ticket.id}))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('Ticket already scanned', response.data['detail'])

    # def test_validate_used_ticket_scanned_less_than_two_minutes_ago(self):
    #     self.ticket_user4 = User.objects.create_user(username='ticketuser4', email='ticketuser4@example.com', password='testpass', first_name='Ticket', last_name='User', student_id='456789')
    #     used_ticket = Ticket.objects.create(title='Test Ticket 4', code='4567890123', price=10.0, status='U', user=self.ticket_user4, event=self.event, scanned_at=timezone.now() - timedelta(minutes=1))
    #     response = self.client.post(reverse('validate-ticket', kwargs={'ticket_id': used_ticket.id}))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('Ticket validated successfully', response.data['detail'])

    def test_validate_cancelled_ticket(self):
        self.ticket_user4 = User.objects.create_user(username='ticketuser4', email='ticketuser4@example.com', password='testpass', first_name='Ticket', last_name='User', student_id='456789')
        cancelled_ticket = Ticket.objects.create(title='Test Ticket 4', code='4567890123', price=10.0, status='C', user=self.ticket_user4, event=self.event)
        response = self.client.post(reverse('validate-ticket', kwargs={'ticket_id': cancelled_ticket.id}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Ticket is not active', response.data['detail'])

class RetrieveEventTicketsViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.club_admin = User.objects.create_user(username='clubadmin', email='clubadmin@example.com', password='testpass')
        self.club = Club.objects.create(name='Test Club')
        self.club.club_admins.add(self.club_admin)
        self.event = Event.objects.create(
            title='Test Event', 
            description='This is a test event.', 
            price=10.0,
            date='2021-01-01',
            time='12:00:00',
            capacity=100,
            location='Test Location',
            club=self.club)
        self.ticket_scanner = User.objects.create_user(username='ticketscanner', email='ticketscanner@example.com', password='testpass', user_type='ticket_scanner', event=self.event, created_by=self.club_admin)
        self.ticket_user = User.objects.create_user(username='ticketuser', email='ticketuser@example.com', password='testpass', first_name='Ticket', last_name='User', student_id='123456')
        self.ticket = Ticket.objects.create(title='Test Ticket 1', code='1234567890', price=10.0, status='A', user=self.ticket_user, event=self.event)
        self.client.force_authenticate(user=self.ticket_scanner)

    def test_retrieve_event_tickets(self):
        response = self.client.get(reverse('scanner-event-tickets'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['active_tickets']), 1)
        self.assertEqual(response.data['active_tickets'][0]['id'], self.ticket.id)

    def test_retrieve_event_tickets_not_ticket_scanner(self):
        self.client.force_authenticate(user=self.club_admin)
        response = self.client.get(reverse('scanner-event-tickets'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_event_tickets_no_event_associated(self):
        self.ticket_scanner.event = None
        self.ticket_scanner.save()
        response = self.client.get(reverse('scanner-event-tickets'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_event_tickets_no_tickets_found(self):
        self.ticket.delete()
        response = self.client.get(reverse('scanner-event-tickets'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)