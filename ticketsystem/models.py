from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models import Q

from backend.storage_backends import PrivateMediaStorage

class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    student_id = models.CharField(max_length=50, unique=True, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    USER_TYPE_CHOICES = (
        ('user', 'user'),
        ('ticket_scanner', 'ticket_scanner'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='user')
    PUBLIC = 'PUB'
    PRIVATE = 'PRI'
    CLOSED = 'CLO'
    ACCOUNT_TYPES = [
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
        (CLOSED, 'Closed'),
    ]
    account_type = models.CharField(
        max_length=3,
        choices=ACCOUNT_TYPES,
        default=PUBLIC,
    )
    event = models.ForeignKey('Event', on_delete=models.SET_NULL, null=True, blank=True, default=None)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, default=None)

    def is_friends_with(self, user):
        status_friends = Friend.objects.filter(
            Q(sender=self, receiver=user) | Q(sender=user, receiver=self),
            status=True
        ).exists()
        print("The status: ", status_friends)
        return status_friends

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_picture/', blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    course = models.CharField(max_length=100, default="none")
    year = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    stripe = models.OneToOneField('StripeAccount', blank=True, null=True, on_delete=models.CASCADE)

    verified = models.BooleanField(default=False)

def create_user_profile(sender, instance, created, **kwargs):
    """ Create a user profile when a new user is created. Only for users. """
    if created and instance.user_type == 'user':
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    """ Save the user profile when the user is saved. Only for users. """
    if hasattr(instance, 'profile'):
        instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)


class TransferRequest(models.Model):
    id =  models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, related_name='sent_transfer_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_transfer_requests', on_delete=models.CASCADE)
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'ticket')
    
class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    code = models.CharField(max_length=100, unique=True)
    price = models.FloatField()
    order_date = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = (
        ('A', 'Active'),
        ('C', 'Cancelled'),
        ('R', 'Refunded'),
        ('U', 'Used'),
    )
    status = models.CharField(max_length=10, 
                                choices=STATUS_CHOICES,
                                default='A')
    qr_code = models.ImageField(upload_to='ticket_qr_code/', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    scanned_at = models.DateTimeField(blank=True, null=True)
    scanned_by = models.ForeignKey(User, related_name='scanned_by', on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'event')

class StripeAccount(models.Model):
    stripe_id = models.CharField(max_length=1000, blank=True, null=True)
    stripe_connected = models.BooleanField(default=False)
    stripe_complete = models.BooleanField(default=False)

class Club(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    club_logo = models.ImageField(upload_to='club_logo/', blank=True, null=True)
    club_cover = models.ImageField(upload_to='club_cover/', blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    content = models.TextField()
    stripe = models.OneToOneField(StripeAccount, blank=True, null=True, on_delete=models.SET_NULL)
    club_admins = models.ManyToManyField(User, related_name='club_admins')

class Friend(models.Model):
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User,related_name='sender', on_delete=models.CASCADE) # Sender is the one who sends the request
    receiver = models.ForeignKey(User,related_name='receiver',  on_delete=models.CASCADE) # Receiver is the one who receives the request
    status = models.BooleanField(default=False) # False means pending, True means accepted
    # Date when the request was sent
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')
    
    def clean(self):
        if self.sender == self.receiver:
            raise ValidationError("A user cannot be friends with themselves.")

class Follow(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'club')

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=1000)
    price = models.FloatField()
    date = models.DateField()
    time = models.TimeField()
    capacity = models.IntegerField(blank=True, null=True)
    soldout = models.IntegerField(default=False)
    event_cover = models.ImageField(upload_to='event_cover/', blank=True, null=True)
    location = models.CharField(max_length=50)
    EVENT_CHOICES = (
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
    )
    event_type = models.CharField(max_length=10,
                                  choices=EVENT_CHOICES,    
                                  default='M')
    club = models.ForeignKey(Club, on_delete=models.CASCADE)