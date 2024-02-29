from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import Club, User, Follow
from ..serializers.serializers import ClubSerializer, ClubUpdateSerializer, FollowSerializer
from ..serializers.user_serializers import UserFriendSerializer

# ====================================================================================================
# Club, Follows and Club Admin API
# ====================================================================================================

# CLUBS ==============================================================================================
class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer
    permission_classes = [IsAuthenticated]

class CreateClubView(APIView):
    permission_classes = [IsAuthenticated]
    # This had its own class because we were assigning a second
    # username as club second club admin. We are not doing that
    # anymore, so we can just use the ClubViewSet.

    def post(self, request, format=None):
        """ Create a club """
        new_data = request.data.copy()
        email = request.data.get('email')
        if Club.objects.filter(email=email).exists():
            return Response({"detail": "There already exists a club with this email"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ClubSerializer(data=new_data)
        if serializer.is_valid():
            club = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
        return Response({'detail': "Could not create club"}, status=status.HTTP_400_BAD_REQUEST)

class ClubUpdateView(APIView):
    def get_object(self, club_id):
        try:
            return Club.objects.get(pk=club_id)
        except Club.DoesNotExist:
            return None

    def patch(self, request, club_id):
        """ Update a club """
        club = self.get_object(club_id)
        if club is None:
            return Response({'error': 'Club not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ClubUpdateSerializer(club, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# CLUB ADMINS ========================================================================================
class ClubAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, club_id, format=None):
        """ Return true if the user admins the club """
        try:
            club = get_object_or_404(Club, id=club_id)
            user = get_object_or_404(User, id=user_id)
            if user in club.club_admins.all():
                return Response(True)
            else:
                return Response(False)
        except Club.DoesNotExist:
            return Response({'detail': 'Club not found'}, status=status.HTTP_400_BAD_REQUEST)

class ClubsAdminedByUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, format=None):
        """ Return a list of clubs that the user admins """
        user = get_object_or_404(User, id=user_id)
        clubs = Club.objects.filter(club_admins=user)
        serializer = ClubSerializer(clubs, many=True)
        return Response(serializer.data)

class AdminsInClubView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id, format=None):
        """ Return a list of users that admin the club """
        club = get_object_or_404(Club, id=club_id)
        users = club.club_admins.all()
        serializer = UserFriendSerializer(users, many=True)
        return Response(serializer.data)

class RemoveClubAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, username, club_id, format=None):
        """ Remove the user from the club admins, given their username and the club id """
        # Here we should check if the authenticated user is a club admin 
        club = get_object_or_404(Club, id=club_id)
        user = get_object_or_404(User, username=username)
        if user in club.club_admins.all():
            club.club_admins.remove(user)
            club.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class AddClubAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, club_id, format=None):
        """ Add the users to the club admins """
        try:
            club = get_object_or_404(Club, id=club_id)
            usernames = request.data.get('usernames', [])
            # If we only get one username, we convert it to a list
            if type(usernames) == str:
                usernames = [usernames]
            for username in usernames:
                user = get_object_or_404(User, username=username)
                if user not in club.club_admins.all():
                    club.club_admins.add(user)
            club.save()
            return Response({"detail": "Admins added!"}, status=status.HTTP_201_CREATED)
        except Club.DoesNotExist:
            return Response({'detail': 'Club not found'}, status=status.HTTP_400_BAD_REQUEST)

# FOLLOWS ============================================================================================
class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """ User follows a club given club id and user id """
        user_id = request.data.get('user')
        club_id = request.data.get('club')
        if not user_id or not club_id:
            return Response({'detail': 'User id and club id are required'}, status=status.HTTP_400_BAD_REQUEST)

        if Follow.objects.filter(user_id=user_id, club_id=club_id).exists():
            return Response({'detail': 'User already follows this club'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)
        club = get_object_or_404(Club, id=club_id)

        data = {'user': user.id, 'club': club.id}
        
        # Create a new Request object with the new data
        new_request = Request(request._request)
        new_request._full_data = data

        return super().create(new_request, *args, **kwargs)

class UserFollowsClubView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, club_id, format=None):
        """ Return true if the user follows the club """
        if Follow.objects.filter(user_id=user_id, club_id=club_id).exists():
            return Response(True)
        else:
            return Response(False)

    def delete(self, request, user_id, club_id, format=None):
        """ Delete the follow of the user for the club """
        deleted_count, _ = Follow.objects.filter(user_id=user_id, club_id=club_id).delete()
        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'Follow does not exist'}, status=status.HTTP_400_BAD_REQUEST)

class UserFollowsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, format=None):
        """ Return a list of clubs that the user follows """
        follows = Follow.objects.filter(user_id=user_id)
        clubs = Club.objects.filter(id__in=[follow.club_id for follow in follows])
        serializer = ClubSerializer(clubs, many=True)
        return Response(serializer.data)

class CommonClubsView(APIView):
    def get(self, request, user_id1, username2, format=None):
        """ Return a list of common clubs between two users """
        user1 = get_object_or_404(User, id=user_id1)
        user2 = get_object_or_404(User, username=username2)

        # Get clubs of user1
        user1_clubs = Follow.objects.filter(user=user1).values_list('club', flat=True)
        # Get clubs of user2 that are also clubs of user1
        common_clubs = Follow.objects.filter(user=user2, club__in=user1_clubs)

        # Extract the club from each follow
        common_clubs = set(follow.club for follow in common_clubs)

        serializer = ClubSerializer(common_clubs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)