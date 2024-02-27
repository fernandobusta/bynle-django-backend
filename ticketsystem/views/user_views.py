from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import User, Profile
from ..serializers.serializers import UserSerializer, ProfileSerializer, UserNameSerializer, UserFriendSerializer

# ====================================================================================================
# User and Profile API
# ====================================================================================================

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

class UserNameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """ Return a list of usernames """
        users = User.objects.filter(user_type='user')
        username = self.request.query_params.get('username')
        if username is not None:
            users = users.filter(username__icontains=username)
        
        serializer = UserNameSerializer(users, many=True)
        return Response(serializer.data)

class UserPersonalProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, format=None):
        """ Return the user's personal profile """
        profile = Profile.objects.get(user=user_id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

class UserPublicProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username, format=None):
        """ Return a user's public profile. This profile is visible to all users """
        # These are the values that we want to send: username, first_name, profile_picture, description, course, year, verified
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserFriendSerializer(user)
        return Response(serializer.data)