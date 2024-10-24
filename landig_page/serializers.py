from rest_framework import serializers

class ProgramSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    coast = serializers.FloatField()
    status = serializers.CharField(max_length=50)
    hostName = serializers.CharField(max_length=255, allow_blank=True)
    slug = serializers.SlugField()
    thumbnailUrl = serializers.URLField(max_length=500, required=False)  

    # Determine whether to include programId based on a condition
    def to_representation(self, instance):
        # Using dictionary access since instance is passed as a dictionary
        representation = super().to_representation(instance)
        
        # 'Include programId if 'include_program_id' value exists
        if self.context.get('include_program_id') and 'programId' in instance:
            representation['programId'] = instance['programId']
            representation.pop('slug', None)  
        
        return representation