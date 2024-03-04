from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
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

    @action(detail=True, methods=['get'])
    def account_type(self, request, pk=None):
        user = self.get_object()
        return Response({'account_type': user.account_type})

    @action(detail=True, methods=['patch'])
    def change_account_type(self, request, pk=None):
        print(request.data)
        user = self.get_object()
        # Check if the user from the request is the same as the user from the URL
        if request.user != user:
            return Response({'detail': 'You do not have permission to change this user\'s account type'}, status=status.HTTP_403_FORBIDDEN)
        new_account_type = request.data.get('account_type')
        if new_account_type not in [User.PUBLIC, User.PRIVATE, User.CLOSED]:
            return Response({'detail': 'Invalid account type'}, status=status.HTTP_400_BAD_REQUEST)
        user.account_type = new_account_type
        user.save()
        return Response({'account_type': user.account_type}, status=status.HTTP_200_OK)

class ProfileViewSet(viewsets.ModelViewSet):
    """ ProfileViewSet, Used in personal profile page """
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

class UserPublicProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username, format=None):
        """ Optimised: True
        Return a user's public profile depending on the account type and friendship status
         - Public: Everyone can view the profile (Sending friendship as well)
         - Private: Only friends can view the profile (Sending friendship as well)
         - Closed: No one can view the profile """
        user = get_object_or_404(User.objects.select_related('profile'), username=username)
        serializer = ProfilePageSerializer(user, context={'request': request})
        return Response(serializer.data)