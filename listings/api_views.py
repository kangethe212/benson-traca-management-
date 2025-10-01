from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Property, PropertyMedia
from .serializers import PropertyListSerializer, PropertyDetailSerializer, PropertyMediaSerializer


class PropertyListAPIView(generics.ListAPIView):
    """API view for listing properties with filtering and search"""
    queryset = Property.objects.filter(is_verified=True).select_related(
        'county'
    ).prefetch_related('media')
    serializer_class = PropertyListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtering options
    filterset_fields = {
        'property_type': ['exact'],
        'county__slug': ['exact'],
        'bedrooms': ['gte'],
        'bathrooms': ['gte'],
        'price': ['gte', 'lte'],
        'is_verified': ['exact'],
    }
    
    # Search fields
    search_fields = ['title', 'description', 'county__name']
    
    # Ordering options
    ordering_fields = ['price', 'area', 'bedrooms', 'created_at']
    ordering = ['-created_at']  # Default ordering
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Additional custom filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        return queryset


class PropertyDetailAPIView(generics.RetrieveAPIView):
    """API view for retrieving a single property"""
    queryset = Property.objects.filter(is_verified=True).select_related(
        'county'
    ).prefetch_related('media')
    serializer_class = PropertyDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PropertyMediaListAPIView(generics.ListAPIView):
    """API view for listing property media"""
    queryset = PropertyMedia.objects.all()
    serializer_class = PropertyMediaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['property', 'media_type', 'is_primary']
    
    def get_queryset(self):
        """Filter media by property if specified"""
        queryset = super().get_queryset()
        property_id = self.request.query_params.get('property')
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        return queryset
