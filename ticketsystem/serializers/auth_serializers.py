from ..models import *
from rest_framework import serializers, exceptions
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.timezone import localdate
from datetime import date, datetime

# ====================================================================================================
#  Authentication Serializers 
# ====================================================================================================


class GeneralTokenObtainPairSerializer(TokenObtainPairSerializer):
    def get_token(self, user):
        token = super().get_token(user)
        # Add any fields that are common to all user types
        token['username'] = user.username
        token['email'] = user.email
        token['user_type'] = user.user_type
        return token

# Token serializer for regular users
class UserTokenObtainPairSerializer(GeneralTokenObtainPairSerializer):
    """ Optimised: True 
        Sending profile picture of users and username"""
    def get_token(self, user):
        if user.user_type != 'user':
            raise exceptions.ValidationError("Only regular users can obtain a token through this method.")
        token = super().get_token(user)
        token['student_id'] = user.student_id
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        profile_picture = user.profile.profile_picture if user.profile and user.profile.profile_picture else None
        if profile_picture:
            token['profile_picture'] = self.context['request'].build_absolute_uri(profile_picture.url)
        else:
            token['profile_picture'] = None

        token['birthday'] = str(user.profile.birthday)
        token['course'] = user.profile.course
        token['year'] = user.profile.year
        token['description'] = user.profile.description
        token['verified'] = user.profile.verified
        return token

class ProfileCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('course', 'year', 'description')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    profile = ProfileCreationSerializer()

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password2', 'profile', 'account_type')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})
        
        # Validate the ProfileCreationSerializer
        profile_serializer = ProfileCreationSerializer(data=attrs['profile'])
        profile_serializer.is_valid(raise_exception=True)

        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            account_type=validated_data['account_type'],
        )

        user.set_password(validated_data['password'])
        user.save()

        # Create the profile
        Profile.objects.create(user=user, **profile_data)

        return user

class TicketScannerTokenObtainPairSerializer(GeneralTokenObtainPairSerializer):
    def get_token(self, user):
        if user.user_type != 'ticket_scanner':
            raise exceptions.ValidationError("Only ticket scanner users can obtain a token through this method.")
        token = super().get_token(user)
        # Add any additional fields for ticket scanner users
        return token