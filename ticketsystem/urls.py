from django.urls import path, include
from django.contrib.auth import views

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views.auth_views import *
from .views.club_views import *
from .views.event_views import *
from .views.friend_views import *
from .views.scanner_views import *
from .views.stripe_views import *
from .views.ticket_views import *
from .views.transfer_views import *
from .views.user_views import *
from .views.clubstats_views import *


# Routes for the API
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'friends', FriendViewSet)
router.register(r'tickets', TicketViewSet)
router.register(r'clubs', ClubViewSet)
router.register(r'events', EventViewSet)
router.register(r'follows', FollowViewSet)
router.register(r'transfer_requests', TransferRequestViewSet)


urlpatterns = [
    path('api/', include(router.urls)),

    # Users and Profiles
    path('usernames/', UserNameView.as_view(), name='public-usernames'),
    path('user/<int:user_id>/profile/', UserPersonalProfileView.as_view(), name='user-profile'),
    path('user/<str:username>/public-profile/', UserPublicProfileView.as_view(), name='public-users'),

    # Ticket Scanners
    path('create-ticket-scanner/', CreateTicketScannerView.as_view(), name='create-ticket-scanner'),
    path('ticket-scanner-users/', TicketScannerUserListView.as_view(), name='ticket-scanner-user-list'),
    path('ticket-scanner-users/<int:id>/delete/', TicketScannerUserDeleteView.as_view(), name='ticket-scanner-user-delete'),
    path('ticket-scanner-users/<int:id>/reset-password/', TicketScannerUserPasswordResetView.as_view(), name='ticket-scanner-user-reset-password'),
    path('validate-ticket/<int:ticket_id>/', ValidateTicketView.as_view(), name='validate-ticket'),
    path('scanner/event-tickets/', RetrieveEventTicketsView.as_view(), name='scanner-event-tickets'),

    # Tickets
    path('user/<int:user_id>/tickets/', UserTicketsView.as_view(), name='user-tickets'),
    path('validate-ticket/<int:ticket_id>/user/<int:user_id>/', ValidateTicketView.as_view(), name='validate-ticket'),
    path('user/<int:user_id>/available-to-transfer-tickets/', AvailableToTransferTicketsView.as_view(), name='available-to-transfer-tickets'),
    path('user/<int:user_id>/has-ticket-for-event/<int:event_id>/', UserHasTicketView.as_view(), name='user-has-ticket-for-event'),
    
    #Transfer
    path('create-transfer-request/', CreateTransferRequest.as_view(), name='create-transfer-request'),
    path('user/<int:user_id>/transfer-request/', UserTransferRequestView.as_view(), name='transfer-request'),
    path('accept-transfer-request/<int:request_id>/', AcceptTransferRequest.as_view(), name='accept-transfer-request'),
    path('user/<int:user_id>/received-transfer-request/', UserReceivedTransferRequestView.as_view(), name='received-transfer-request'),
    path('user/<int:user_id>/sent-transfer-requests/', UserSentTransferRequestsView.as_view(), name='sent-transfer-requests'),
    path('user/<int:user_id>/can-accept-transfer/<int:transfer_id>/', CanAcceptTransferView.as_view(), name='can-accept-transfer'),
    
    # Clubs and Admins
    path('create-club/', CreateClubView.as_view(), name='create-club'),
    path('update-club/<int:club_id>/', ClubUpdateView.as_view(), name='update-club'),
    path('user/<int:user_id>/admins/', ClubsAdminedByUserView.as_view(), name='user-admins'),
    path('user/<int:user_id>/admins/<int:club_id>/', ClubAdminView.as_view(), name='user-admins-club'),
    path('club/<int:club_id>/admins/', AdminsInClubView.as_view(), name='club-admins'),
    path('club/<int:club_id>/remove-admin/<str:username>/', RemoveClubAdminView.as_view(), name='remove-club-admin'),
    path('club/<int:club_id>/add-admin/', AddClubAdminView.as_view(), name='add-club-admin'),
    
    # Events
    path('club/<int:club_id>/events/', ClubEventsView.as_view(), name='club-events'),
    path('user/<str:username>/events/', UserEventsView.as_view(), name='user-events'),
    path('event/<int:event_id>/soldout/', EventSoldOutView.as_view(), name='event-soldout'),

    # Follows
    path('user/<int:user_id>/follows/<int:club_id>/', UserFollowsClubView.as_view(), name='user-follows-club'),
    path('user/<int:user_id>/follows/', UserFollowsView.as_view(), name='user-follows'),
    path('common-followed-clubs/<int:user_id1>/<str:username2>/', CommonClubsView.as_view(), name='common-followed-clubs'),
    
    # Friends
    path('user/<int:user_id>/friends/<str:friendship_status>/', UserFriends.as_view(), name='user-friends'),
    path('user/<int:user1>/friendship/<str:username2>/', ManageFriendship.as_view(), name='manage-friendship'),
    path('create-friend-request/', CreateFriendRequest.as_view(), name='create-friend-request'),
    path('common-friends/<int:user_id1>/<str:username2>/', CommonFriendsView.as_view(), name='common-friends'),
        
    # Stripe
    path('stripe-account/club/<int:club_id>/', StripeAccountClubView.as_view(), name='club-stripe-account'),
    path('stripe-account/user/<int:user_id>/', StripeAccountUserView.as_view(), name='user-stripe-account'),
    path('api/create-checkout-session/', CreateStripeCheckoutSession.as_view(), name='checkout-session'),
    path('api/create-user-checkout-session/', CreateStripeUserCheckoutSession.as_view(), name='checkout-session-user'),
    path("stripe-status/<int:club_id>/", StripeStatusView.as_view(), name='stripe-status-club'),
    path("stripe-status-user/<int:user_id>/", StripeStatusUserView.as_view(), name='stripe-status-user'),
    path('create-stripe-account-custom/<int:club_id>/', CreateStripeAccountCustom.as_view(), name='create_account_custom'),
    path('stripe-successful/<int:club_id>/', StripeSuccessView.as_view(), name='stripe-successful'),
    path('stripe-successful/user/<int:user_id>/', StripeSuccessUserView.as_view(), name='stripe-successful-user'),
    path('create-stripe-account-express/<int:user_id>/', CreateStripeAccountExpress.as_view(), name='create_account_express'),
    
    # Authentication
    path('token/', UserTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/ticket-scanner/', TicketScannerTokenObtainPairView.as_view(), name='token_ticket_scanner_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),

    # Stats
    path('stats/club/<int:club_id>/event-user-year/', StatEventsYearView.as_view(), name='stats-event-user-year'),
    path('stats/club/<int:club_id>/followers/', StatClubFollowersView.as_view(), name='stats-club-followers'),
]
