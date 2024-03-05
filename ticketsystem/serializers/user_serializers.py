from rest_framework import serializers
from ..models import User, Profile, Friend
from django.conf import settings
from datetime import datetime, timedelta, date
from django.db.models import Q

class UserSerializer(serializers.ModelSerializer):
    """ Serializer for the User model """
    class Meta:
        model = User
        fields = ('username', 'email', 'student_id', 'first_name', 'last_name')

class ProfileSerializer(serializers.ModelSerializer):
    """ Serializer for the Profile model """
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = '__all__'

    def get_profile_picture(self, obj):
        """ Return the profile picture if it exists, otherwise return None """
        profile_picture = obj.profile_picture
        if profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(profile_picture.url)
            return profile_picture.url
        return None

class UserNameSerializer(serializers.ModelSerializer):
    """ Serializer for the User model with only the username """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

class BasicUserInfoSerializer(serializers.ModelSerializer):
    """ Serializer for the User model with the profile picture and fields """
    profile_picture = serializers.SerializerMethodField()
    course = serializers.CharField(source='profile.course')
    year = serializers.IntegerField(source='profile.year')
    verified = serializers.BooleanField(source='profile.verified')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'profile_picture', 'course', 'year', 'verified')

    def get_profile_picture(self, obj):
        """ Return the profile picture if it exists, otherwise return None """
        profile_picture = obj.profile.profile_picture
        if profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(profile_picture.url)
            return profile_picture.url
        return None

def validate_file_size(value):
    """ Validate the file size of the profile picture """
    filesize = value.size
    if filesize > 1048576:
        raise serializers.ValidationError("The maximum file size that can be uploaded is 1MB")
    else:
        return value

class ProfileUpdateSerializer(serializers.ModelSerializer):
    """ Optimised: True
        Serializer to update the profile of the user """
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

class ProfilePageSerializer(serializers.ModelSerializer):
    """ Optimised: True
        Serializer for the User model with the profile picture and fields """
    profile_picture = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    verified = serializers.SerializerMethodField()
    friendship_status = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    show_details = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'profile_picture', 'course', 'year', 'description', 'verified', 'friendship_status', 'show_details')

    def get_friendship_status(self, obj):
        # Check if the friendship status is already in the context
        if 'friendship_status' in self.context:
            return self.context['friendship_status']

        request = self.context.get('request')
        if request.user == obj:
            status = 'you'
        elif obj.account_type == User.CLOSED:
            status = 'closed'
        else:
            friend_requests = Friend.objects.filter(
                Q(sender=request.user, receiver=obj) | 
                Q(sender=obj, receiver=request.user)
            )
            if friend_requests.filter(status=True).exists():
                status = 'friends'
            elif friend_requests.filter(status=False).exists():
                if friend_requests.first().sender == request.user:
                    status = 'pending'
                else:
                    status = 'accept'
            else:
                status = 'none'

        self.context['friendship_status'] = status
        return status

    def get_field_value(self, obj, field):
        request = self.context.get('request')
        if request.user == obj:
            return getattr(obj.profile, field)
        friendship_status = self.get_friendship_status(obj)
        if obj.account_type == User.CLOSED or (obj.account_type == User.PRIVATE and (friendship_status == 'none' or friendship_status == 'pending' or friendship_status == 'accept')):
            return None
        return getattr(obj.profile, field)

    def get_first_name(self, obj):
        if obj.account_type == User.CLOSED:
            return 'Restricted'
        return obj.first_name

    def get_last_name(self, obj):
        if obj.account_type == User.CLOSED:
            return 'Account'
        return obj.last_name

    def get_profile_picture(self, obj):
        profile_picture = obj.profile.profile_picture
        if profile_picture and obj.account_type != User.CLOSED:
            request = self.context.get('request')
            return request.build_absolute_uri(profile_picture.url)
        return None

    def get_course(self, obj):
        return self.get_field_value(obj, 'course')

    def get_year(self, obj):
        return self.get_field_value(obj, 'year')

    def get_description(self, obj):
        if obj.account_type == User.CLOSED:
            return None
        return obj.profile.description

    def get_verified(self, obj):
        if obj.account_type == User.CLOSED:
            return None
        return obj.profile.verified
    
    def get_show_details(self, obj):
        """ Can the user see the details of the profile? """
        # If the account is public, return True
        if obj.account_type == User.PUBLIC or obj == self.context['request'].user:
            return True
        # If the account is private, check if the user is friends with the profile
        elif obj.account_type == User.PRIVATE:
            return obj.is_friends_with(self.context['request'].user)
        else:
            return False