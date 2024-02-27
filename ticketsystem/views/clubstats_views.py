from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from ticketsystem.models import Club, Event, Ticket, Profile, Follow
from ..serializers.stats_serializers import EventYearDataSerializer, ClubFollowersDataSerializer

from collections import defaultdict

class StatEventsYearView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id, format=None):
        # Check if the user is a club admin
        try:
            club = Club.objects.get(id=club_id)
            if request.user != club.admin:
                return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        except Club.DoesNotExist:
            return Response({'detail': 'Club does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Get all the events from the club
        events = Event.objects.filter(club=club)

        # Initialize the data list
        data = []

        # For each event, get all the tickets
        for event in events:
            tickets = Ticket.objects.filter(event=event)

            # Initialize the year count dictionary
            year_count = {f'year{year}': 0 for year in range(1, 7)}

            # For each ticket, get the user's year from the Profile table
            for ticket in tickets:
                user = ticket.user
                profile = Profile.objects.get(user=user)
                year = f'year{profile.year}'

                # Increment the year count
                year_count[year] += 1

            # Serialize the data
            event_data = {'event_title': event.title, 'year_data': year_count}
            serializer = EventYearDataSerializer(data=event_data)
            if serializer.is_valid():
                data.append(serializer.validated_data)

        # Return the data
        return Response(data, status=status.HTTP_200_OK)

class StatClubFollowersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id, format=None):
        # Check if the user is a club admin
        try:
            club = Club.objects.get(id=club_id)
            if request.user not in club.club_admins.all():
                return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        except Club.DoesNotExist:
            return Response({'detail': 'Club does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Get all the followers of the club
        follows = Follow.objects.filter(club=club)

        # Initialize the year and course count dictionaries
        year_count = {f'year{year}': 0 for year in range(1, 7)}
        course_count = defaultdict(int)

        # For each follower, get the user's year and course from the Profile table
        for follow in follows:
            follower = follow.user
            profile = Profile.objects.get(user=follower)
            year = f'year{profile.year}'
            course = profile.course

            # Increment the year and course counts
            year_count[year] += 1
            course_count[course] += 1

        # Serialize the data
        club_data = {'club_name': club.name, 'year_data': year_count, 'course_data': course_count}
        serializer = ClubFollowersDataSerializer(data=club_data)
        if serializer.is_valid():
            data = serializer.validated_data
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Return the data
        return Response(data, status=status.HTTP_200_OK)