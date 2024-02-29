from rest_framework import serializers
from ..models import User, Profile
from django.conf import settings
from datetime import datetime, timedelta, date

class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the User model """
    class Meta:
        model = User
        fields = ('username', 'email', 'student_id', 'first_name', 'last_name')

class ProfileSerializer(serializers.ModelSerializer):
    """ Serializer for the Profile model - Default profile picture is used 
    if the user has not uploaded a profile picture """
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('__all__')
    
    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        else:
            return settings.MEDIA_URL + 'default_profile_picture.jpg'

class UserNameSerializer(serializers.ModelSerializer):
    """ Serializer for the User model with only the username """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

class UserFriendSerializer(serializers.ModelSerializer):
    """ Serializer for the User model with the profile picture and fields """
    profile_picture = serializers.SerializerMethodField()
    course = serializers.CharField(source='profile.course')
    year = serializers.IntegerField(source='profile.year')
    verified = serializers.BooleanField(source='profile.verified')
    description = serializers.CharField(source='profile.description')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'profile_picture', 'course', 'year', 'verified', 'description')

    def get_profile_picture(self, obj):
        profile_picture = obj.profile.profile_picture if obj.profile and obj.profile.profile_picture else None
        return profile_picture.url if profile_picture else settings.MEDIA_URL + 'default_profile_picture.jpg' 

def validate_file_size(value):
    filesize = value.size
    if filesize > 1048576:
        raise serializers.ValidationError("The maximum file size that can be uploaded is 1MB")
    else:
        return value

class ProfileUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(validators=[validate_file_size], required=False)

    class Meta:
        model = Profile
        fields = ['profile_picture', 'birthday', 'course', 'year', 'description']

    def validate(self, data):
        """
        Validate the data:
        - Remove fields that are empty or None.
        - Check if year is an integer and between 1 and 10.
        - Check if profile_picture is a file.
        - Check if birthday is a valid date and person is at least 10 years old.
        """
        year = data.get('year')
        if year is not None:
            if not isinstance(year, int):
                raise serializers.ValidationError({"year": "Year must be an integer."})
            if year < 1 or year > 10:
                raise serializers.ValidationError({"year": "Are you sure you are in that year?"})

        profile_picture = data.get('profile_picture')
        if profile_picture is not None and not hasattr(profile_picture, 'read'):
            data.pop('profile_picture')

        birthday = data.get('birthday')
        if birthday is not None:
            if isinstance(birthday, str):
                try:
                    birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
                except ValueError:
                    raise serializers.ValidationError({"birthday": "Invalid date format. Use 'YYYY-MM-DD'."})
            elif not isinstance(birthday, date):
                raise serializers.ValidationError({"birthday": "Invalid date format. Use 'YYYY-MM-DD'."})

            if datetime.now().date() - timedelta(days=365*10) < birthday:
                raise serializers.ValidationError({"birthday": "Is that your real Birthday?"})
        else:
            data.pop('birthday')

        description = data.get('description')
        if description is not None and len(description) > 500:
            raise serializers.ValidationError({"description": "Description must be less than 500 characters."})
        if description is None or description == "":
            data.pop('description')

        return data