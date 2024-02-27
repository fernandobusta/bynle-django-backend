from django.core.files.base import ContentFile

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..utils import ticketCodeGenerator, ticketQRCodeGenerator
from ..models import Ticket, User, Event
from ..serializers.serializers import TicketSerializer

# ====================================================================================================
# Tickets API
# ====================================================================================================

class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    # Override the retrieve method to check if the ticket belongs to the authenticated user
    def retrieve(self, request, *args, **kwargs):
        """ Only the user who created the ticket (owner) can view it """
        instance = self.get_object()
        if instance.user != request.user:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    # Override the create method to replace the username with the user's id
    def create(self, request, *args, **kwargs):
        """ Create a ticket and generate a QR code """
        username = request.data.get('user')
        event_id = request.data.get('event')
        if not username:
            return Response({'detail': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
            event = Event.objects.get(id=event_id)
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a Ticket already exists for this user
        if Ticket.objects.filter(user=user, event=event).exists():
            return Response({'detail': 'A ticket already exists for this user'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the event has reached its capacity
        ticket_count = Ticket.objects.filter(event=event).count()
        if ticket_count >= event.capacity:
            event.soldout = True  # Set the soldout attribute to True
            event.save()  # Save the event
            return Response({'detail': 'This event has sold out'}, status=status.HTTP_400_BAD_REQUEST)
        request.data['user'] = user.id  # Replace the username with the user's id
        request.data['price'] = event.price  # Set the price to the price of the event
        request.data['code'] = ticketCodeGenerator()  # Generate the ticket code
        request.data['event'] = int(event_id)
        
        response = super().create(request, *args, **kwargs)

        # Generate and save the QR code after the Ticket object is created
        if response.status_code == status.HTTP_201_CREATED:
            ticket = Ticket.objects.get(id=response.data['id'])
            try:
                qr_code_image = ticketQRCodeGenerator(ticket.id)
                ticket.qr_code.save(f"ticket_{ticket.id}_qr_code.png", ContentFile(qr_code_image.getvalue()))
                ticket.save()
                return Response({'detail': 'Ticket created and QR code generated successfully'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"Error generating QR code: {e}")
                return Response({'detail': 'Error generating QR code'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response

class UserTicketsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, format=None):
        """ Return a list of tickets that the user has """
        tickets = Ticket.objects.filter(user_id=user_id)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)

class UserHasTicketView(APIView):
    def get(self, request, user_id, event_id, format=None):
        """ Return true if the user has a ticket for the event """
        try:
            user = User.objects.get(id=user_id)
            event = Event.objects.get(id=event_id)
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Event.DoesNotExist:
            return Response({'detail': 'Event does not exist'}, status=status.HTTP_404_NOT_FOUND)

        has_ticket = Ticket.objects.filter(user=user, event=event).exists()

        return Response({'has_ticket': has_ticket}, status=status.HTTP_200_OK)