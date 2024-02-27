from django.test import TestCase
from ticketsystem.models import User, Event, Club, Profile, Ticket, TransferRequest, StripeAccount, Friend, Follow

class UserModelTest(TestCase):
    """ Testing: User Model
        Dependencies: Event, Club """
    def setUp(self):
        self.club = Club.objects.create(name='Test Club')
        self.event = Event.objects.create(
            title='Test Event',
            description='This is a test event.',
            price=10.0,
            date='2022-01-01',
            time='10:00:00',
            capacity=100,
            location='Test Location',
            event_type='M',
            club=self.club
        )
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.ticket_scanner = User.objects.create_user(username='testscanner', email='testscanner@example.com', password='testpass', user_type='ticket_scanner', event=self.event, created_by=self.user)

    def test_user_creation(self):
        self.assertIsInstance(self.user, User)
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertEqual(self.user.user_type, 'user')
        self.assertIsNone(self.user.event)
        self.assertIsNone(self.user.created_by)

    def test_ticket_scanner_creation(self):
        self.assertIsInstance(self.ticket_scanner, User)
        self.assertEqual(self.ticket_scanner.username, 'testscanner')
        self.assertEqual(self.ticket_scanner.email, 'testscanner@example.com')
        self.assertEqual(self.ticket_scanner.user_type, 'ticket_scanner')
        self.assertEqual(self.ticket_scanner.event, self.event)
        self.assertEqual(self.ticket_scanner.created_by, self.user)

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser')
        self.assertEqual(str(self.ticket_scanner), 'testscanner')

    def test_required_fields(self):
        self.assertEqual(User.REQUIRED_FIELDS, ['username'])

    def test_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, 'email')

    def test_user_type_choices(self):
        self.assertEqual(User.USER_TYPE_CHOICES, (('user', 'user'), ('ticket_scanner', 'ticket_scanner')))

class ProfileModelTest(TestCase):
    """ Testing: Profile Model
        Dependencies: User """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')

    def test_profile_creation(self):
        self.assertIsInstance(self.user.profile, Profile)
        self.assertEqual(self.user.profile.course, 'none')
        self.assertEqual(self.user.profile.year, 0)
        self.assertIsNone(self.user.profile.birthday)
        self.assertIsNone(self.user.profile.description)
        self.assertIsNone(self.user.profile.stripe)
        self.assertFalse(self.user.profile.verified)

    def test_profile_auto_created_for_new_user(self):
        new_user = User.objects.create_user(username='newuser', email='newuser@example.com', password='testpass', user_type='user')
        self.assertIsInstance(new_user.profile, Profile)

class TicketModelTest(TestCase):
    """ Testing: Ticket Model
        Dependencies: User, Event, Club """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.club = Club.objects.create(name='Test Club')  # Replace with actual Club creation
        self.event = Event.objects.create(
            title='Test Event',
            description='This is a test event.',
            price=10.0,
            date='2022-01-01',
            time='10:00:00',
            capacity=100,
            location='Test Location',
            event_type='M',
            club=self.club
        )
        self.ticket = Ticket.objects.create(
            title='Test Ticket',
            code='testcode',
            price=10.0,
            user=self.user,
            event=self.event
        )

    def test_ticket_creation(self):
        self.assertIsInstance(self.ticket, Ticket)
        self.assertEqual(self.ticket.title, 'Test Ticket')
        self.assertEqual(self.ticket.code, 'testcode')
        self.assertEqual(self.ticket.price, 10.0)
        self.assertEqual(self.ticket.status, 'A')
        self.assertIsNotNone(self.ticket.order_date)
        self.assertEqual(self.ticket.user, self.user)
        self.assertEqual(self.ticket.event, self.event)
        self.assertIsNone(self.ticket.scanned_at)
        self.assertIsNone(self.ticket.scanned_by)

    def test_status_choices(self):
        self.assertEqual(Ticket.STATUS_CHOICES, (('A', 'Active'), ('C', 'Cancelled'), ('R', 'Refunded'), ('U', 'Used')))

    def test_unique_together(self):
        with self.assertRaises(Exception):
            Ticket.objects.create(
                title='Test Ticket 2',
                code='testcode2',
                price=10.0,
                user=self.user,
                event=self.event
            )

class TransferRequestModelTest(TestCase):
    """ Testing: TransferRequest Model
        Dependencies: User, Ticket, Event, Club """
    def setUp(self):
        self.sender = User.objects.create_user(username='testsender', email='testsender@example.com', password='testpass', user_type='user')
        self.receiver = User.objects.create_user(username='testreceiver', email='testreceiver@example.com', password='testpass', user_type='user')
        self.club = Club.objects.create(name='Test Club')
        self.event = Event.objects.create(
            title='Test Event',
            description='This is a test event.',
            price=10.0,
            date='2022-01-01',
            time='10:00:00',
            capacity=100,
            location='Test Location',
            event_type='M',
            club=self.club
        )
        self.ticket = Ticket.objects.create(
            title='Test Ticket',
            code='testcode',
            price=10.0,
            user=self.sender,
            event=self.event
        )
        self.transfer_request = TransferRequest.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            ticket=self.ticket
        )

    def test_transfer_request_creation(self):
        self.assertIsInstance(self.transfer_request, TransferRequest)
        self.assertEqual(self.transfer_request.sender, self.sender)
        self.assertEqual(self.transfer_request.receiver, self.receiver)
        self.assertEqual(self.transfer_request.ticket, self.ticket)
        self.assertEqual(self.transfer_request.status, 'pending')
        self.assertIsNotNone(self.transfer_request.created_at)

    def test_unique_together(self):
        with self.assertRaises(Exception):
            TransferRequest.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                ticket=self.ticket
            )

class StripeAccountModelTest(TestCase):
    def setUp(self):
        self.stripe_account = StripeAccount.objects.create()

    def test_stripe_account_creation(self):
        self.assertIsInstance(self.stripe_account, StripeAccount)
        self.assertIsNone(self.stripe_account.stripe_id)
        self.assertFalse(self.stripe_account.stripe_connected)
        self.assertFalse(self.stripe_account.stripe_complete)
    
class ClubModelTest(TestCase):
    """ Testing: Club Model
        Dependencies: User, StripeAccount"""
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.stripe_account = StripeAccount.objects.create()
        self.club = Club.objects.create(
            name='Test Club',
            description='This is a test club.',
            email='testclub@example.com',
            website='http://www.testclub.com',
            content='Test content.'
        )
        self.club.club_admins.add(self.user)

    def test_club_creation(self):
        self.assertIsInstance(self.club, Club)
        self.assertEqual(self.club.name, 'Test Club')
        self.assertEqual(self.club.description, 'This is a test club.')
        self.assertEqual(self.club.email, 'testclub@example.com')
        self.assertEqual(self.club.website, 'http://www.testclub.com')
        self.assertEqual(self.club.content, 'Test content.')
        self.assertIsNone(self.club.stripe)
        self.assertEqual(self.club.club_admins.first(), self.user)

class FriendModelTest(TestCase):
    """ Testing: Friend Model
        Dependencies: User """
    def setUp(self):
        self.sender = User.objects.create_user(username='testsender', email='testsender@example.com', password='testpass', user_type='user')
        self.receiver = User.objects.create_user(username='testreceiver', email='testreceiver@example.com', password='testpass', user_type='user')
        self.friend_request = Friend.objects.create(
            sender=self.sender,
            receiver=self.receiver
        )

    def test_friend_request_creation(self):
        self.assertIsInstance(self.friend_request, Friend)
        self.assertEqual(self.friend_request.sender, self.sender)
        self.assertEqual(self.friend_request.receiver, self.receiver)
        self.assertFalse(self.friend_request.status)
        self.assertIsNotNone(self.friend_request.created_at)

    def test_unique_together(self):
        with self.assertRaises(Exception):
            Friend.objects.create(
                sender=self.sender,
                receiver=self.receiver
            )
    
    def test_update_friend_status(self):
        self.friend_request.status = True
        self.friend_request.save()
        self.assertTrue(self.friend_request.status)

class FollowModelTest(TestCase):
    """ Testing: Follow Model
        Dependencies: User, Club """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass', user_type='user')
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com', content='Test content.')
        self.follow = Follow.objects.create(user=self.user, club=self.club)

    def test_follow_creation(self):
        self.assertIsInstance(self.follow, Follow)
        self.assertEqual(self.follow.user, self.user)
        self.assertEqual(self.follow.club, self.club)

    def test_unique_together(self):
        with self.assertRaises(Exception):
            Follow.objects.create(user=self.user, club=self.club)

class EventModelTest(TestCase):
    """ Testing: Event Model
        Dependencies: Club """
    def setUp(self):
        self.club = Club.objects.create(name='Test Club', description='This is a test club.', email='testclub@example.com', content='Test content.')
        self.event = Event.objects.create(
            title='Test Event',
            description='This is a test event.',
            price=10.0,
            date='2022-01-01',
            time='10:00:00',
            capacity=100,
            location='Test Location',
            event_type='M',
            club=self.club
        )

    def test_event_creation(self):
        self.assertIsInstance(self.event, Event)
        self.assertEqual(self.event.title, 'Test Event')
        self.assertEqual(self.event.description, 'This is a test event.')
        self.assertEqual(self.event.price, 10.0)
        self.assertEqual(self.event.date, '2022-01-01')
        self.assertEqual(self.event.time, '10:00:00')
        self.assertEqual(self.event.capacity, 100)
        self.assertEqual(self.event.soldout, False)
        self.assertEqual(self.event.location, 'Test Location')
        self.assertEqual(self.event.event_type, 'M')
        self.assertEqual(self.event.club, self.club)

    def test_event_choices(self):
        self.assertEqual(Event.EVENT_CHOICES, (
            ('A', 'Anniversary'),
            ('B', 'Birthday'),
            ('C', 'Charity'),
            ('D', 'Dinner'),
            ('E', 'Exhibition'),
            ('F', 'Festival'),
            ('G', 'Gathering'),
            ('H', 'Hackathon'),
            ('I', 'Interview'),
            ('J', 'Job Fair'),
            ('L', 'Lecture'),
            ('M', 'Meeting'),
            ('N', 'Networking'),
            ('O', 'Other'),
            ('P', 'Party'),
            ('R', 'Rally'),
            ('S', 'Seminar'),
            ('T', 'Tournament'),
            ('V', 'Visit'),
            ('W', 'Workshop'),
            ('X', 'Expo'),
        ))