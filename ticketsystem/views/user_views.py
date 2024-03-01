from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.db.models import Q
from django.shortcuts import get_object_or_404

from ..models import User, Profile, Friend
from ..serializers.user_serializers import UserSerializer, ProfileSerializer, UserNameSerializer, ProfilePageSerializer, ProfileUpdateSerializer

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

    def update(self, request, *args, **kwargs):
        serializer = ProfileUpdateSerializer(data=request.data, instance=self.get_object(), partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

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
        """ Return a user's public profile depending on the account type and friendship status
         - Public: Everyone can view the profile (Sending friendship as well)
         - Private: Only friends can view the profile (Sending friendship as well)
         - Closed: No one can view the profile """
        user = get_object_or_404(User.objects.select_related('profile'), username=username)
        serializer = ProfilePageSerializer(user, context={'request': request})
        return Response(serializer.data)