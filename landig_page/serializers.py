from rest_framework import serializers

class ProgramSerializer(serializers.Serializer):
    programId = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    cost = serializers.FloatField()
    status = serializers.CharField(max_length=50)
    hostName = serializers.CharField(max_length=255, allow_blank=True)
    thumbnailUrl = serializers.URLField(max_length=500, required=False)  

class MentorSerializer(serializers.Serializer):
    userId = serializers.UUIDField()
    mentorName = serializers.CharField(max_length=255, allow_blank=True)
    userType = serializers.CharField(max_length=255)
    photoUrl = serializers.URLField(max_length=500, required=False, allow_blank=True)
    industry = serializers.CharField(max_length=255, allow_blank=True)
    
class ReviewSerializer(serializers.Serializer):
    reviewId = serializers.UUIDField()
    reviewerName = serializers.CharField(max_length=255, allow_blank=True)
    content = serializers.URLField(max_length=500, allow_blank=True)
    programId = serializers.UUIDField()
    rating = serializers.FloatField()
    photoUrl = serializers.URLField(max_length=500, required=False, allow_blank=True)
    industry = serializers.CharField(max_length=255, allow_blank=True)