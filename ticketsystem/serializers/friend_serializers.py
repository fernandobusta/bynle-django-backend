from rest_framework import serializers
from ..models import User, Profile, Friend

class FriendSerializer(serializers.ModelSerializer):
    """ Serializer for the Friend model """
    class Meta:
        model = Friend
        fields = ('__all__')

class CommonFriendsSerializer(serializers.ModelSerializer):
    """ 
    Optimised: True
    Sending profile picture of users and username """
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'profile_picture')

    def get_profile_picture(self, obj):
        """ Return the profile picture if it exists, otherwise return None """
        profile_picture = obj.profile.profile_picture
        if profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(profile_picture.url)
            return profile_picture.url
        return None

class FriendStatusSerializer(serializers.ModelSerializer):
    """ Serializer for the User model with the profile picture main profile fields """
    profile_picture = serializers.SerializerMethodField()
    verified = serializers.BooleanField(source='profile.verified')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'profile_picture', 'verified')

    def get_profile_picture(self, obj):
        """ Return the profile picture if it exists, otherwise return None """
        profile_picture = obj.profile.profile_picture
        if profile_picture and hasattr(profile_picture, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(profile_picture.url)
            return profile_picture.url
        return None