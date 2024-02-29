from ..models import *
from rest_framework import serializers
from django.utils.timezone import localdate
from .user_serializers import UserSerializer

class TicketScannerCreateSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'event_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        event_id = validated_data.pop('event_id')
        user = User.objects.create_user(**validated_data, user_type='ticket_scanner')
        # Set the event for the user
        user.event_id = event_id
        user.save()
        return user

class TicketScannerUserSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'event', 'created_by']

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None

class TicketScannerUserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        # Future validation
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

class TicketWithUserSerializer(serializers.ModelSerializer):
    """ Sending User data along with the ticket - used for the scanner """
    user = UserSerializer(read_only=True)
    scanned_at = serializers.SerializerMethodField()
    scanned_by = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'status', 'scanned_at', 'scanned_by', 'user']
    
    def get_scanned_at(self, obj):
        if obj.scanned_at is None:
            return None
        if obj.scanned_at.date() == localdate():
            # If the date is today, return just the time
            return obj.scanned_at.strftime("%H:%M")
        else:
            # Otherwise, return the time and date
            return obj.scanned_at.strftime("%H:%M, %d/%m")

    def get_scanned_by(self, obj):
        if obj.scanned_by is None:
            return None
        else:
            return obj.scanned_by.username