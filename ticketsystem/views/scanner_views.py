from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from datetime import timedelta
from collections import defaultdict

from ..models import User, Event, Ticket
from ..permissions import IsTicketScannerUser
from ..serializers.scanner_serializers import TicketScannerCreateSerializer, TicketScannerUserPasswordResetSerializer, TicketScannerUserSerializer, TicketWithUserSerializer

# ====================================================================================================
# Ticket Scanner API
# ====================================================================================================

class CreateTicketScannerView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TicketScannerCreateSerializer

    def post(self, request, *args, **kwargs):
        """ Create a ticket scanner user given an event and club admin """
        # Check if the authenticated user is active
        if not request.user.is_active:
            return Response({'detail': 'Inactive user'}, status=status.HTTP_400_BAD_REQUEST)
        # Check if the authenticated user is an admin of the event
        event_id = request.data.get('event_id')
        if not event_id:
            return Response({'detail': 'Event ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        # Get the event
        event = get_object_or_404(Event, id=event_id)
        # Check if the event is associated with a club
        if not event.club:
            return Response({'detail': 'Event is not associated with a club'}, status=status.HTTP_400_BAD_REQUEST)
         # Check if the authenticated user is a club admin for the club that is hosting the event
        if not event.club.club_admins.filter(id=request.user.id).exists():
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        # Set the created_by field to the authenticated user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TicketScannerUserPasswordResetView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TicketScannerUserPasswordResetSerializer

    def get_object(self):
        """ Reset the password of a ticket scanner user """
        user_id = self.kwargs.get('id')
        user = get_object_or_404(User, id=user_id)
        if not user.event.club.club_admins.filter(id=self.request.user.id).exists():
            raise PermissionDenied('You do not have permission to reset this user\'s password')
        return user
    
class TicketScannerUserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TicketScannerUserSerializer

    def list(self, request, *args, **kwargs):
        """ Return a list of ticket scanner users for an event """
        event_id = request.query_params.get('event_id')
        if not event_id:
            return Response({'detail': 'Event ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        event = get_object_or_404(Event, id=event_id)
        if not event.club.club_admins.filter(id=request.user.id).exists():
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        queryset = User.objects.filter(event=event)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class TicketScannerUserDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    # Should probably merge this with another one of ticket scanner views
    def get_object(self):
        """ Delete a ticket scanner user given their id """
        user_id = self.kwargs.get('id')
        user = get_object_or_404(User, id=user_id)
        if not user.event.club.club_admins.filter(id=self.request.user.id).exists():
            raise PermissionDenied('You do not have permission to delete this user')
        return user

class ValidateTicketView(APIView):
    permission_classes = [IsTicketScannerUser]

    def post(self, request, ticket_id, format=None):
        """ Validate a ticket. Ticket scanners can only validate tickets for the event they are assigned to """
        ticket = get_object_or_404(Ticket, id=ticket_id)
        if not ticket_id:
            return Response({'detail': 'Ticket ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        # Check if the authenticated user is a scanner user and if they are associated with the event of the ticket
        if not request.user.user_type == 'ticket_scanner' or request.user.event_id != ticket.event_id:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        if ticket.status == 'U':
            # If the ticket was scanned less than 2 minutes ago, treat it as successfully validated
            # Changed this to 10 seconds for testing purposes
            time_difference = timezone.now() - ticket.scanned_at
            if time_difference <= timedelta(seconds=2):
                return Response({
                    'detail': 'Ticket validated successfully', 
                    'first_name': ticket.user.first_name,
                    'last_name': ticket.user.last_name,
                    'student_id': ticket.user.student_id,
                    'ticket_status': 'active',
                    'scanned_ago': str(int(time_difference.total_seconds())) + ' seconds ago'}, 
                    status=status.HTTP_200_OK)
            else:
                return Response({
                    'detail': 'Ticket already scanned', 
                    'ticket_status': 'used', 
                    'scanned_ago': str(int(time_difference.total_seconds() / 60)) + ' minutes ago'}, 
                    status=status.HTTP_200_OK)
        elif ticket.status == 'A':
            ticket.status = 'U'
            if ticket.scanned_at is None:
                ticket.scanned_at = timezone.now()
                ticket.scanned_by = request.user
            ticket.save()
            user = ticket.user
            return Response({
                'detail': 'Ticket validated successfully', 
                'first_name': user.first_name,
                'last_name': user.last_name,
                'student_id': user.student_id,
                'ticket_status': 'active',
                'scanned_ago': 'just now'}, 
                status=status.HTTP_200_OK)
        return Response({'detail': 'Ticket is not active'}, status=status.HTTP_400_BAD_REQUEST)

class RetrieveEventTicketsView(APIView):
    permission_classes = [IsTicketScannerUser]

    def get(self, request, format=None):
        """ Retrieve all the tickets for the event the authenticated ticket scanner user has been assigned to """
        if not request.user.user_type == 'ticket_scanner':
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        # Check if the user is associated with an event
        if not request.user.event_id:
            return Response({'detail': 'No event associated with this user'}, status=status.HTTP_400_BAD_REQUEST)
        # Get the tickets for the event
        tickets = Ticket.objects.filter(event_id=request.user.event_id)
        # If no tickets found, return an error
        if not tickets:
            return Response({'detail': 'No tickets found for this event'}, status=status.HTTP_404_NOT_FOUND)
        # Serialize all the tickets at once
        serialized_tickets = TicketWithUserSerializer(tickets, many=True).data
        # Group the serialized tickets by their status
        tickets_by_status = defaultdict(list)
        for ticket in serialized_tickets:
            tickets_by_status[ticket['status']].append(ticket)
        # Return the tickets grouped by their status
        return Response({
            'active_tickets': tickets_by_status['A'],
            'used_tickets': tickets_by_status['U'],
            'cancelled_tickets': tickets_by_status['C'],
            'refunded_tickets': tickets_by_status['R']
        }, status=status.HTTP_200_OK)

