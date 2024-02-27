from ..models import *
from rest_framework import serializers
from django.conf import settings
from django.utils.timezone import localdate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'student_id', 'first_name', 'last_name')

class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('__all__')
    
    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        else:
            return settings.MEDIA_URL + 'default_profile_picture.jpg'  # replace 'default.jpg' with your default image file name

class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

class UserFriendSerializer(serializers.ModelSerializer):
    """ Serializer for the User model with the profile picture """
    profile_picture = serializers.SerializerMethodField()
    course = serializers.CharField(source='profile.course')
    year = serializers.IntegerField(source='profile.year')
    verified = serializers.BooleanField(source='profile.verified')
    description = serializers.CharField(source='profile.description')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'profile_picture', 'course', 'year', 'verified', 'description')

    def get_profile_picture(self, obj):
        profile_picture = obj.profile.profile_picture if obj.profile and obj.profile.profile_picture else None
        return profile_picture.url if profile_picture else settings.MEDIA_URL + 'default_profile_picture.jpg' 

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
            return settings.MEDIA_URL + 'default_club_logo.jpg'  # replace 'default_logo.jpg' with your default logo image file name

    def get_club_cover(self, obj):
        if obj.club_cover:
            return obj.club_cover.url
        else:
            return settings.MEDIA_URL + 'default_club_cover.jpg'  # replace 'default_cover.jpg' with your default cover image file name

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
            return settings.MEDIA_URL + 'default_event_cover.jpg'  # replace 'default_event_cover.jpg' with your default event cover image file name

    def get_club_name(self, obj):
        return obj.club.name
    
    def get_club_logo(self, obj):
        if obj.club.club_logo:
            return obj.club.club_logo.url
        else:
            return settings.MEDIA_URL + 'default_club_logo.jpg'