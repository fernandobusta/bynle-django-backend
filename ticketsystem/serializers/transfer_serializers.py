from ..models import *
from rest_framework import serializers
from django.conf import settings

class TransferTicketSerializer(serializers.ModelSerializer):
    """ To not send sensible ticket data (QR) when transferring a ticket """
    class Meta:
        model = Ticket
        fields = ['title', 'price']

class TransferRequestSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()
    ticket = TransferTicketSerializer()
    created_at = serializers.SerializerMethodField()
    sender_profile_picture = serializers.SerializerMethodField()
    club_name = serializers.SerializerMethodField()
    event_cover = serializers.SerializerMethodField()

    class Meta:
        model = TransferRequest
        fields = ['id', 'sender', 'receiver', 'ticket', 'status', 'created_at', 'sender_profile_picture', 'club_name', 'event_cover']

    def get_sender(self, obj):
        return obj.sender.username

    def get_receiver(self, obj):
        return obj.receiver.username

    def get_created_at(self, obj):
        return obj.created_at.strftime('%d/%m/%Y')

    def get_sender_profile_picture(self, obj):
        """ Return the sender's profile picture if it exists, otherwise return None """
        profile_picture = obj.sender.profile.profile_picture
        if profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(profile_picture.url)
            return profile_picture.url
        return None

    def get_club_name(self, obj):
        return obj.ticket.event.club.name

    def get_event_cover(self, obj):
        """ Return the event cover if it exists, otherwise return None """
        event_cover = obj.ticket.event.event_cover
        if event_cover:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(event_cover.url)
            return event_cover.url
        return None

class CreateTransferRequestSerializer(serializers.Serializer):
    receiver = serializers.CharField()
    ticket_id = serializers.IntegerField()

    def validate_ticket_id(self, value):
        # Check if the ticket exists
        if not Ticket.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid ticket id")
        return value

class AcceptTransferRequestSerializer(serializers.Serializer):
    transfer_request_id = serializers.IntegerField()

    def validate_transfer_request_id(self, value):
        # Check if the transfer request exists
        if not TransferRequest.objects.filter(id=value, status='pending').exists():
            raise serializers.ValidationError("Invalid transfer request id")
        return value