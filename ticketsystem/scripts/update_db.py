from django.contrib.auth import get_user_model
from ticketsystem.models import Club, Event  # Import your Club and Event models

User = get_user_model()

def run():
    # Update profile pictures
    for user in User.objects.all():
        profile_picture_path = f'profile_picture/{user.student_id}.jpg'
        user.profile.profile_picture = profile_picture_path
        user.profile.save()

    # Update club logos
    for club in Club.objects.all():
        club_logo_path = f'club_logo/{club.name.split()[0].lower()}.jpg'
        club.club_logo = club_logo_path
        club.save()

    # Update event covers
    for club in Club.objects.all():
        club_events = Event.objects.filter(club=club).order_by('id')
        for i, event in enumerate(club_events, start=1):
            event_cover_path = f'event_cover/{club.name.split()[0].lower()}-event-{i}.jpg'
            event.event_cover = event_cover_path
            event.save()