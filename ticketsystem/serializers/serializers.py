from ..models import *
from rest_framework import serializers
from django.conf import settings
from django.utils.timezone import localdate


class StripeAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeAccount
        fields = ('__all__')


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = ('__all__')

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('__all__')

class ClubSerializer(serializers.ModelSerializer):
    club_logo = serializers.SerializerMethodField()
    club_cover = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = ('__all__')

    def get_club_logo(self, obj):
        if obj.club_logo:
            return obj.club_logo.url
        else:
            return settings.MEDIA_URL + 'default_club_logo.jpg'

    def get_club_cover(self, obj):
        if obj.club_cover:
            return obj.club_cover.url
        else:
            return settings.MEDIA_URL + 'default_club_cover.jpg'

class ClubUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ('name', 'description', 'email', 'website', 'content', 'club_logo', 'club_cover')
        extra_kwargs = {field: {'required': False} for field in fields}

class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('__all__')

class EventSerializer(serializers.ModelSerializer):
    event_cover = serializers.SerializerMethodField()
    club_name = serializers.SerializerMethodField()
    club_logo = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('__all__')
    
    def get_event_cover(self, obj):
        if obj.event_cover:
            return obj.event_cover.url
        else:
            return settings.MEDIA_URL + 'default_event_cover.jpg'

    def get_club_name(self, obj):
        return obj.club.name
    
    def get_club_logo(self, obj):
        if obj.club.club_logo:
            return obj.club.club_logo.url
        else:
            return settings.MEDIA_URL + 'default_club_logo.jpg'