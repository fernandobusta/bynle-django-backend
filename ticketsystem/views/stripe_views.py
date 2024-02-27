from django.conf import settings
from django.http import JsonResponse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import stripe
from decouple import config

from ..utils import get_stripe_account_completion, account_create_link, account_create_link_user, create_account_custom, create_account_express, get_stripe_accountid, stripe_tos_acceptance, calculate_application_fee, ticketCodeGenerator
from ..models import StripeAccount, Club, Profile, TransferRequest, Ticket, Event
from ..serializers.serializers import StripeAccountSerializer

# ====================================================================================================
# Stripe API
# ====================================================================================================
class StripeAccountClubView(APIView):
    queryset = StripeAccount.objects.all()
    serializer_class = StripeAccountSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id, format=None):
        """ Return a stripe account that is connected to the club """
        try:
            club = Club.objects.get(id=club_id)
            stripe = club.stripe
            if not stripe:
                return Response({'detail': 'No Stripe account found for the club'}, status=status.HTTP_200_OK)
            else:
                serializer = StripeAccountSerializer(stripe)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Club.DoesNotExist:
            return Response({'detail': 'Club not found'}, status=status.HTTP_400_BAD_REQUEST)
        
class StripeAccountUserView(APIView):
    queryset = StripeAccount.objects.all()
    serializer_class = StripeAccountSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, format=None):
        """ Return a stripe account that is connected to the user """
        try:
            user = Profile.objects.get(user_id=user_id)
            stripe = user.stripe
            if not stripe:
                 return Response({'detail': 'No Stripe account found for the user', 'stripe_connected': False}, status=status.HTTP_200_OK)
            else:
                serializer = StripeAccountSerializer(stripe)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

class StripeStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id, *args, **kwargs):
        """ Return the status of the Stripe account associated with the club """
        try:
            club = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            return Response({'detail': 'Club not found'}, status=status.HTTP_400_BAD_REQUEST)

        if club.stripe and club.stripe.stripe_connected:
            stripe_completion_status = get_stripe_account_completion(club.stripe.stripe_id)
            if club.stripe.stripe_complete:
                return Response({'detail': 'Stripe account is complete', 'stripe_connected': club.stripe.stripe_connected}, status=status.HTTP_200_OK)
            elif stripe_completion_status:
                club.stripe.stripe_complete = stripe_completion_status
                club.stripe.save()
                return Response({'detail': 'Stripe account is complete please refresh', 'stripe_connected': club.stripe.stripe_connected}, status=status.HTTP_200_OK)

            else:
                # Stripe account needs finishing
                account_link_response = account_create_link(club.stripe.stripe_id, club_id)
                account_link_url = account_link_response.url
                return Response({ "detail": 'Stripe account setup not complete', 'stripe_connected': club.stripe.stripe_connected, 'account_link_url': account_link_url}, status=status.HTTP_200_OK)
        else:
            # The club has no associated Stripe account
            return Response({'detail': 'No Stripe account found for the club', 'stripe_connected': False}, status=status.HTTP_200_OK)



class StripeStatusUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, *args, **kwargs):
        """ Return the status of the Stripe account associated with the user """
        try:
            user = Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profile not found'}, status=status.HTTP_400_BAD_REQUEST)

        if user.stripe and user.stripe.stripe_connected:
            stripe_completion_status = get_stripe_account_completion(user.stripe.stripe_id)
            if user.stripe.stripe_complete:
                return Response({'detail': 'Stripe account is complete', 'stripe_connected': user.stripe.stripe_connected}, status=status.HTTP_200_OK)
    
            elif stripe_completion_status:
                user.stripe.stripe_complete = stripe_completion_status
                user.stripe.save()
                return Response({'detail': 'Stripe account is complete please refresh', 'stripe_connected': user.stripe.stripe_connected}, status=status.HTTP_200_OK)

            else:
                # Stripe account needs finishing
                account_link_response = account_create_link_user(user.stripe.stripe_id, user_id)
                account_link_url = account_link_response.url
                return Response({ "detail": 'Stripe account setup not complete', 'stripe_connected': user.stripe.stripe_connected, 'account_link_url': account_link_url}, status=status.HTTP_200_OK)
        else:
            # The club has no associated Stripe account
            return Response({'detail': 'No Stripe account found for the user', 'stripe_connected': False}, status=status.HTTP_200_OK)

class CreateStripeUserCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """ Create a stripe checkout session for User """
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            data = request.data
            transfer_id = int(data.get('transferRequestId'))
            transfer_obj = TransferRequest.objects.get(id=transfer_id)
            ticket = transfer_obj.ticket
            price_ticket = ticket.price 
            user_id = ticket.user 
            user_instance = Profile.objects.get(user_id=user_id)
            # Access the associated user
            price = int(price_ticket * 100)
            connected_account_id = user_instance.stripe.stripe_id
            intent = stripe.PaymentIntent.create(
                amount=price,
                currency='eur',
                # In the latest version of the API, specifying the `automatic_payment_methods` parameter is optional because Stripe enables its functionality by default.
                automatic_payment_methods={
                    'enabled': True,
                },
                transfer_data={"destination": connected_account_id},
                application_fee_amount= calculate_application_fee(price),            
            )
            return Response({'clientSecret': intent['client_secret']}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'detail':'Something went wrong', 'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateStripeCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """ Create a stripe checkout session for Club """
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            data = request.data
            event_id = data.get('eventId')
            # Assuming you have an instance of the Event model
            event_instance = Event.objects.get(id=event_id)
            # Access the associated club using the ForeignKey relationship
            price = int(event_instance.price * 100)
            connected_account_id = event_instance.club.stripe.stripe_id
            intent = stripe.PaymentIntent.create(
                amount=price,
                currency='eur',
                # In the latest version of the API, specifying the `automatic_payment_methods` parameter is optional because Stripe enables its functionality by default.
                automatic_payment_methods={
                    'enabled': True,
                },
                transfer_data={"destination": connected_account_id},
                application_fee_amount= calculate_application_fee(price),            
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        
        except Exception as e:
            return Response({'detail':'Something went wrong', 'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StripeSuccessView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, club_id, *args, **kwargs):
        """ Update Completion status for Club """
        try:
            club = Club.objects.get(id=club_id)
        except Club.DoesNotExist:
            # Handle the case where the club is not found (print a message or any other desired action)
            return Response({'detail': 'Club not found'}, status=status.HTTP_400_BAD_REQUEST)

        stripe_completion_status = get_stripe_account_completion(club.stripe.stripe_id)
        club.stripe.stripe_complete = stripe_completion_status
        club.stripe.save()
        # The club has an associated StripeAccount and is already connected
        return Response({'detail': 'Stripe account is complete'}, status=status.HTTP_200_OK)

class StripeSuccessUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id, *args, **kwargs):

        """ Update Completion status for User """
        try:
            user = Profile.objects.get(user_id=user_id)
            user.stripe.stripe_complete = True
            user.stripe.save()
            return Response({'detail': 'Stripe account is complete'}, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'detail': 'Profile not found'}, status=status.HTTP_400_BAD_REQUEST)


class CreateStripeAccountCustom(APIView):
    permission_classes = [IsAuthenticated]
    stripe.api_key = config('STRIPE_SECRET_KEY')

    def get(self, request, club_id, *args, **kwargs):
        try:
            club = Club.objects.get(id=club_id)
            context = {
                "user_email": club.email,
            }
            found = get_stripe_accountid(club.email)
            if not found:
                account_id = create_account_custom(context)
                stripe_account = StripeAccount.objects.create(
                    stripe_id=account_id,
                    stripe_connected=True,
                    stripe_complete=False
                )
                club.stripe = stripe_account
                club.save()
                stripe_tos_acceptance(account_id) # Accept the Stripe TOS
                account_link_response = account_create_link(account_id, club_id)
                account_link_url = account_link_response.url

                return Response({'account_link_url': account_link_url}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Email is already associated with a Stripe account.'}, status=status.HTTP_200_OK)
        except Club.DoesNotExist:
            return Response({'detail': 'Club not found'}, status=status.HTTP_400_BAD_REQUEST)


class CreateStripeAccountExpress(APIView):

    permission_classes = [IsAuthenticated]
    stripe.api_key = config('STRIPE_SECRET_KEY')

    def get(self, request, user_id, *args, **kwargs):
        user = Profile.objects.get(user_id=user_id)
        context = {
            "user_email": user.user.email,
        }
        found = get_stripe_accountid(user.user.email)

        if not found:
            account_id = create_account_express(context)
            stripe_account = StripeAccount.objects.create(
                stripe_id=account_id,
                stripe_connected=True,
                stripe_complete=False
            )
            user.stripe = stripe_account
            user.save()
            account_link_response = account_create_link_user(account_id, user_id)
            account_link_url = account_link_response.url

            return Response({'account_link_url': account_link_url}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Email is already associated with a Stripe account.'}, status=status.HTTP_400_BAD_REQUEST)

