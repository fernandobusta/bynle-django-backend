from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import Event, User, Ticket
from ..serializers.event_serializers import EventSerializer

# ====================================================================================================
# Events API
# ====================================================================================================
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    model = Event
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

class ClubEventsView(APIView):
    """ Optimised: True
    View for getting events for a specific club """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, club_id, format=None):
        """ Return a list of events that the club hosts """
        events = Event.objects.filter(club_id=club_id).select_related('club')
        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)

class UserEventsView(APIView):
    """ Optimised: True
    View for getting events for a specific user """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, username, format=None):
        """ Return a list of events that the user has tickets for (Active tickets), used in public profile page """
        user = get_object_or_404(User, username=username)

        # Get active and used events directly
        events_active = Event.objects.filter(ticket__user=user, ticket__status='A').select_related('club')
        events_used = Event.objects.filter(ticket__user=user, ticket__status='U').select_related('club')

        serializer_active = EventSerializer(events_active, many=True, context={'request': request})
        serializer_used = EventSerializer(events_used, many=True, context={'request': request})
        return Response({'active': serializer_active.data, 'used': serializer_used.data}, status=status.HTTP_200_OK)

class EventSoldOutView(APIView):
    def get(self, request, event_id, format=None):
        """ Return if the event is sold out """
        try:
            event = Event.objects.filter(id=event_id).annotate(tickets_sold=Count('ticket')).get()
        except Event.DoesNotExist:
            return Response({'detail': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)

        sold_out = event.tickets_sold >= event.capacity
        return Response({'sold_out': sold_out}, status=status.HTTP_200_OK)