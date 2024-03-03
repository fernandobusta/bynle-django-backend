from ..models import *
from rest_framework import serializers
from django.conf import settings
from django.utils.timezone import localdate

class ClubSerializer(serializers.ModelSerializer):
    """ Serializer for the Club model """
    club_logo = serializers.SerializerMethodField()
    club_cover = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = '__all__'

    def get_club_logo(self, obj):
        """ Return the club logo if it exists, otherwise return None """
        club_logo = obj.club_logo
        if club_logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(club_logo.url)
            return club_logo.url
        return None

    def get_club_cover(self, obj):
        """ Return the club cover if it exists, otherwise return None """
        club_cover = obj.club_cover
        if club_cover:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(club_cover.url)
            return club_cover.url
        return None


class ClubUpdateSerializer(serializers.ModelSerializer):
    """ Serializer for updating the Club model """
    class Meta:
        model = Club
        fields = ('name', 'description', 'email', 'website', 'content', 'club_logo', 'club_cover')
        extra_kwargs = {field: {'required': False} for field in fields}

class FollowSerializer(serializers.ModelSerializer):
    """ Serializer for the Follow model """
    class Meta:
        model = Follow
        fields = ('__all__')

class ClubsFollowedSerializer(serializers.ModelSerializer):
    club_logo = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = ('id', 'name', 'email', 'club_logo')

    def get_club_logo(self, obj):
        """ Return the club logo if it exists, otherwise return None """
        club_logo = obj.club_logo
        if club_logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(club_logo.url)
            return club_logo.url
        return None