from rest_framework import serializers
from .models import Property, PropertyMedia, Agent, County, Amenity


class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = ['id', 'name', 'slug', 'description']


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon', 'description']


class AgentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='full_name', read_only=True)
    
    class Meta:
        model = Agent
        fields = ['id', 'full_name', 'phone', 'bio', 'profile_image', 'license_number']


class PropertyMediaSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertyMedia
        fields = ['id', 'media_type', 'file_url', 'caption', 'is_primary', 'order']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class PropertyListSerializer(serializers.ModelSerializer):
    """Serializer for property list view (minimal data)"""
    county_name = serializers.CharField(source='county.name', read_only=True)
    agent_name = serializers.CharField(source='agent.full_name', read_only=True)
    main_image = serializers.SerializerMethodField()
    amenities_list = serializers.StringRelatedField(source='amenities', many=True, read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'property_type', 'status', 'price', 'area',
            'bedrooms', 'bathrooms', 'parking_slots', 'county_name',
            'location', 'agent_name', 'main_image', 'amenities_list',
            'is_featured', 'created_at'
        ]
    
    def get_main_image(self, obj):
        main_image = obj.main_image
        if main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.file.url)
            return main_image.file.url
        return None


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Serializer for property detail view (full data)"""
    county = CountySerializer(read_only=True)
    agent = AgentSerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    media = PropertyMediaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'property_type', 'status',
            'price', 'area', 'bedrooms', 'bathrooms', 'bathtubs',
            'washrooms', 'parking_slots', 'county', 'location', 'address',
            'latitude', 'longitude', 'agent', 'amenities', 'media',
            'is_featured', 'published', 'created_at', 'updated_at'
        ]
