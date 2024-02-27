from rest_framework import serializers

class YearCountSerializer(serializers.Serializer):
    year1 = serializers.IntegerField()
    year2 = serializers.IntegerField()
    year3 = serializers.IntegerField()
    year4 = serializers.IntegerField()
    year5 = serializers.IntegerField()
    year6 = serializers.IntegerField()

class EventYearDataSerializer(serializers.Serializer):
    event_title = serializers.CharField(max_length=200)
    year_data = YearCountSerializer()

class ClubFollowersDataSerializer(serializers.Serializer):
    club_name = serializers.CharField()
    year_data = serializers.DictField(child=serializers.IntegerField())
    course_data = serializers.DictField(child=serializers.IntegerField())