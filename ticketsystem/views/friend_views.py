from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..models import Friend, User
from ..serializers.serializers import FriendSerializer
from ..serializers.user_serializers import UserFriendSerializer

# ====================================================================================================
# Friends API
# ====================================================================================================
class FriendViewSet(viewsets.ModelViewSet):
    queryset = Friend.objects.all()
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

class UserFriends(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, friendship_status, format=None):
        """ Return a list of friends of the user given the status (True: Friends, False: Pending request) """
        if friendship_status == 'accepted' or friendship_status == 'True':
            friends = Friend.objects.filter(Q(sender_id=user_id) | Q(receiver_id=user_id), status=True)
        elif friendship_status == 'pending' or friendship_status == 'False':
            friends = Friend.objects.filter(receiver_id=user_id, status=False)
        else:
            return Response({'detail': 'Invalid friendship status'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the ids of the friends
        friend_ids = [friend.receiver_id if friend.sender_id == user_id else friend.sender_id for friend in friends]

        # Get the users corresponding to the friends
        users = User.objects.filter(id__in=friend_ids)
        
        # Use the new serializer here
        serializer = UserFriendSerializer(users, many=True)
        return Response(serializer.data)

class CommonFriendsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id1, username2, format=None):
        """ Return a list of common friends between two users """
        user1 = get_object_or_404(User, id=user_id1)
        user2 = get_object_or_404(User, username=username2)

        # Get friends of user1
        user1_friends = Friend.objects.filter(Q(sender=user1) | Q(receiver=user1), status=True)
        # Get friends of user2 that are also friends of user1
        common_friends = Friend.objects.filter(Q(sender=user2) | Q(receiver=user2), status=True, id__in=user1_friends)

        # Extract the friend from each friendship
        common_friends = set(friend.receiver if friend.sender == user2 else friend.sender for friend in common_friends)

        serializer = UserFriendSerializer(common_friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateFriendRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """ Create a friend request"""
        # Check if the request is valid (sender and receiver exist and are different)
        # The sender is the authenticated user, so we are getting the id from the token
        sender = request.user
        # The receiver variable is the username, we need to get the user id
        receiver_username = request.data.get('receiver')
        try:
            receiver = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        if sender == receiver:
            return Response({'detail': 'Users must be different'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the request already exists (in either direction)
        friend_query = Friend.objects.filter(Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender))
        if friend_query.exists():
            friend = friend_query.first()
            if friend.sender == sender:
                return Response({'detail': 'Friend request already exists'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # If the inverse request exists, we have to accept the request
                friend.status = True
                friend.save()
                return Response({'detail': 'Friend request accepted'}, status=status.HTTP_201_CREATED)

        # If the inverse request does not exist, we create a new request
        data = request.data.copy()
        data['sender'] = sender.id
        data['receiver'] = receiver.id

        # Save the request to the database
        serializer = FriendSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
        return Response({'detail': "Could not create friend request"}, status=status.HTTP_400_BAD_REQUEST)
    

class ManageFriendship(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user1, username2, format=None):
        """ Return if the friendship status between the two users, if it exists 
            user1 is the authenticated user, user2 is the user that we want to check the friendship status with 
            In the JSON reponses:
            status: True if they are friends, False if the friendship is pending
            sender: current if the authenticated user is the sender, other if the authenticated user is the receiver"""
        # username2 variable is the username, we need to get the user id
        try:
            user2 = User.objects.get(username=username2).id
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to get the friendship (Check both ways)
        friend = Friend.objects.filter(Q(sender_id=user1, receiver_id=user2) | Q(sender_id=user2, receiver_id=user1)).first()
        if friend is None:
            return Response({'detail': 'Friendship does not exist', 'status': 'None', 'sender': 'None'}, status=status.HTTP_200_OK)

        # Check the friendship status and sender
        friendship_status = 'True' if friend.status else 'False'
        sender = 'current' if friend.sender_id == user1 else 'other'
        detail = 'Friends' if friend.status else 'Pending'

        return Response({'detail': detail, 'status': friendship_status, 'sender': sender}, status=status.HTTP_200_OK)
    
    def post(self, request, user1, username2, format=None):
        """ Accept the friendship request between the two users, if it exists"""
        # username2 variable is the username, we need to get the user id
        user2 = User.objects.filter(username=username2).first()
        if user2 is None:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to get the friendship
        friend = Friend.objects.filter(sender_id=user2.id, receiver_id=user1).first()
        if friend is None:
            return Response({'detail': 'Friendship does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the friendship has already been accepted
        if friend.status:
            return Response({'detail': 'Friendship already accepted'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Accept the friendship
        friend.status = True
        friend.created_at = timezone.now()  # Update from request creation to acceptance
        friend.save()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request, user1, username2, format=None):
        """ Delete the friendship between the two users, if it exists 
            user1 is the authenticated user, user2 is the user that we want to delete the friendship with """
        # username2 variable is the username, we need to get the user id
        try:
            user2 = User.objects.get(username=username2).id
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Try to get the friendship (Check both ways)
        friend = Friend.objects.filter(Q(sender_id=user1, receiver_id=user2) | Q(sender_id=user2, receiver_id=user1)).first()
        # Check if the friendship does not exist (Check both ways)
        if friend is None:
            return Response({'detail': 'Friendship does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        # Delete the friendship
        friend.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)