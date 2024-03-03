from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..utils import ticketCodeGenerator, ticketQRCodeGenerator
from ..models import TransferRequest, Ticket, User
from ..serializers.serializers import TicketSerializer
from ..serializers.transfer_serializers import TransferRequestSerializer

# ====================================================================================================
# Transfer API
# ====================================================================================================

class TransferRequestViewSet(viewsets.ModelViewSet):
    queryset = TransferRequest.objects.all()
    serializer_class = TransferRequestSerializer
    permission_classes = [IsAuthenticated]

class AvailableToTransferTicketsView(APIView):
    def get(self, request, user_id, format=None):
        """ Return a list of tickets that the user can transfer """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Get all active tickets of the user
        active_tickets = Ticket.objects.filter(user=user, status='A')

        # Get all tickets that have been selected for transfer
        transfer_tickets = TransferRequest.objects.values_list('ticket', flat=True)

        # Filter the active tickets to exclude the transfer tickets
        available_to_transfer_tickets = active_tickets.exclude(id__in=transfer_tickets)

        serializer = TicketSerializer(available_to_transfer_tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateTransferRequest(APIView):
    permission_classes = [IsAuthenticated]

    # Could probably merge this with another view here
    def post(self, request, format=None):
        """ Create a transfer request given a sender, receiver and ticket """
        receiver_username = request.data.get('receiver')
        ticket_id = request.data.get('ticket').get('id')
        sender = request.user

        try:
            receiver = User.objects.get(username=receiver_username)
            ticket = Ticket.objects.get(id=ticket_id)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid receiver'}, status=status.HTTP_400_BAD_REQUEST)
        except Ticket.DoesNotExist:
            return Response({'detail': 'Invalid ticket'}, status=status.HTTP_400_BAD_REQUEST)

        if sender == receiver:
            return Response({'detail': 'Sender and receiver must be different'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            transfer_request = TransferRequest.objects.create(sender=sender, receiver=receiver, ticket=ticket)
        except IntegrityError:
            return Response({'detail': 'Transfer request already exists'}, status=status.HTTP_400_BAD_REQUEST)

        transfer_request_serializer = TransferRequestSerializer(transfer_request)
        return Response(transfer_request_serializer.data, status=status.HTTP_201_CREATED)

class UserSentTransferRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, format=None):
        """ Return a list of the transfer requests that the user has sent """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Get all TransferRequest sent by the user
        sent_transfer_requests = TransferRequest.objects.filter(sender=user)

        # Group the transfer requests by status
        pending_transfer_requests = sent_transfer_requests.filter(status='pending')
        accepted_transfer_requests = sent_transfer_requests.filter(status='accepted')
        declined_transfer_requests = sent_transfer_requests.filter(status='declined')

        # Serialize the transfer requests
        context = {'request': request}
        pending_serializer = TransferRequestSerializer(pending_transfer_requests, many=True, context=context)
        accepted_serializer = TransferRequestSerializer(accepted_transfer_requests, many=True, context=context)
        declined_serializer = TransferRequestSerializer(declined_transfer_requests, many=True, context=context)

        return Response({
            'pending_transfer_requests': pending_serializer.data,
            'accepted_transfer_requests': accepted_serializer.data,
            'declined_transfer_requests': declined_serializer.data
        }, status=status.HTTP_200_OK)

class UserTransferRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id, format=None):
        """ Return a list of the transfer requests that the user has received """
        transfer_requests = TransferRequest.objects.filter(receiver_id=user_id)
        serializer = TransferRequestSerializer(transfer_requests, many=True, context={'request': request})
        return Response(serializer.data,  status=status.HTTP_200_OK)

class UserReceivedTransferRequestView(APIView):
    def get(self, request, user_id, format=None):
        """ Get the number of pending TransferRequest received by the user """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Get all pending TransferRequest received by the user
        pending_transfer_requests = TransferRequest.objects.filter(receiver=user, status='pending')

        # Count the number of pending TransferRequest received by the user
        num_of_transfers = pending_transfer_requests.count()

        return Response({'num_of_transfers': num_of_transfers}, status=status.HTTP_200_OK)

class CanAcceptTransferView(APIView):
    def get(self, request, user_id, transfer_id, format=None):
        """ Return true if the user can accept the transfer request. This is useful for when the event is
        paid, we block the user from accessing the payment pannel """
        try:
            user = User.objects.get(id=user_id)
            transfer_request = TransferRequest.objects.get(id=transfer_id)
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except TransferRequest.DoesNotExist:
            return Response({'detail': 'Transfer request does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user already has a ticket for the event
        has_ticket_for_event = Ticket.objects.filter(user=user, event=transfer_request.ticket.event).exists()

        # The user can accept the transfer if they don't have a ticket for the event
        can_accept_transfer = not has_ticket_for_event

        return Response({'can_accept_transfer': can_accept_transfer}, status=status.HTTP_200_OK)

class AcceptTransferRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id, format=None):
        """ Accept a transfer request, delete the old ticket and create a new ticket for the receiver """
        try:
            transfer_request = TransferRequest.objects.get(id=request_id)
            # Check if the ticket is still active
            if transfer_request.ticket.status != 'A':
                return Response({'detail': 'Ticket is not active anymore.'}, status=status.HTTP_400_BAD_REQUEST)
            # Check if the receiver already has a ticket for the event
            if Ticket.objects.filter(user=transfer_request.receiver, event=transfer_request.ticket.event).exists():
                return Response({'detail': 'You already have a ticket for this event'}, status=status.HTTP_400_BAD_REQUEST)
            # Check if the transfer request is valid and can be accepted
            
            if transfer_request.status == 'pending':
                # Create a new ticket based on the accepted transfer request
                new_ticket = Ticket.objects.create(
                    title=transfer_request.ticket.title,
                    code=ticketCodeGenerator(),
                    price=transfer_request.ticket.price,  # Include the price here
                    order_date=transfer_request.ticket.order_date,
                    status='A',  # Assuming new tickets are always 'Active'
                    user=transfer_request.receiver,  # Assign the receiver as the user
                    event=transfer_request.ticket.event
                )
                try:
                    # Get the ticket we just created from user and event
                    new_ticket_qr = Ticket.objects.get(id=new_ticket.id)
                    qr_code_image = ticketQRCodeGenerator(new_ticket_qr.id)
                    new_ticket_qr.qr_code.save(f"ticket_{new_ticket.id}_qr_code.png", ContentFile(qr_code_image.getvalue()))
                    new_ticket_qr.save()
                except Exception as e:
                    print(f"Error generating QR code: {e}")
                    return Response({'detail': 'Error generating QR code'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                # delete old ticket
                transfer_request.ticket.delete()
                # delete transfer request
                transfer_request.delete()

                return Response({'detail': 'Transfer request accepted'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Transfer request cannot be accepted'}, status=status.HTTP_400_BAD_REQUEST)
        except TransferRequest.DoesNotExist:
            return Response({'detail': 'Transfer request does not exist'}, status=status.HTTP_404_NOT_FOUND)
