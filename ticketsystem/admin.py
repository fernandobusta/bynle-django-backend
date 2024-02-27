from django.contrib import admin
from .models import *

# Register your models here.
class UserAdminPanel(admin.ModelAdmin):
    list_display = ('username', 'email', 'user_type', 'student_id')

class ProfileAdminPanel(admin.ModelAdmin):
    list_display = ('user', 'verified')

class FollowAdminPanel(admin.ModelAdmin):
    list_display = ('user', 'club')

class FriendAdminPanel(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status')

class TicketAdminPanel(admin.ModelAdmin):
    list_display = ('user', 'event')

class EventAdminPanel(admin.ModelAdmin):
    list_display = ('club', 'title')

class ClubAdminPanel(admin.ModelAdmin):
    list_display = ('name', 'stripe')

class TransferRequestAdminPanel(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'ticket', 'status')

admin.site.register(User, UserAdminPanel)
admin.site.register(Profile, ProfileAdminPanel)
admin.site.register(Friend, FriendAdminPanel)
admin.site.register(Ticket, TicketAdminPanel)
admin.site.register(Club, ClubAdminPanel)
admin.site.register(Event, EventAdminPanel)
admin.site.register(Follow, FollowAdminPanel)
admin.site.register(StripeAccount)
admin.site.register(TransferRequest, TransferRequestAdminPanel)
