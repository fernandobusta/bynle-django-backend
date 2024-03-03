from ..models import *
from rest_framework import serializers
from django.conf import settings


class EventSerializer(serializers.ModelSerializer):
    """ Serializer for the Event model """
    event_cover = serializers.SerializerMethodField()
    club_name = serializers.SerializerMethodField()
    club_logo = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_club_name(self, obj):
        return obj.club.name

    def get_event_cover(self, obj):
        """ Return the event cover if it exists, otherwise return None """
        event_cover = obj.event_cover
        if event_cover:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(event_cover.url)
            return event_cover.url
        return None

    def get_club_logo(self, obj):
        """ Return the club logo if it exists, otherwise return None """
        club_logo = obj.club.club_logo
        if club_logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(club_logo.url)
            return club_logo.url
        return None