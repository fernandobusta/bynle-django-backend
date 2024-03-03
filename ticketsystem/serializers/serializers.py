from ..models import *
from rest_framework import serializers
from django.conf import settings
from django.utils.timezone import localdate


class StripeAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = StripeAccount
        fields = ('__all__')

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('__all__')