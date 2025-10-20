from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Min, Max
from django.utils import timezone
from datetime import timedelta

from .models import Property, PropertyMedia, County, Testimonial, Inquiry
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


@api_view(['GET'])
@permission_classes([AllowAny])
def property_statistics_api(request):
    """API endpoint for property statistics"""
    stats = {
        'total_properties': Property.objects.filter(is_verified=True).count(),
        'sale_properties': Property.objects.filter(is_verified=True, property_type='sale').count(),
        'rent_properties': Property.objects.filter(is_verified=True, property_type='rent').count(),
        'verified_properties': Property.objects.filter(is_verified=True).count(),
        'counties_served': County.objects.filter(is_active=True).count(),
        'average_price': Property.objects.filter(is_verified=True, price__isnull=False).aggregate(
            avg_price=Avg('price')
        )['avg_price'],
        'price_range': Property.objects.filter(is_verified=True, price__isnull=False).aggregate(
            min_price=Min('price'),
            max_price=Max('price')
        ),
        'recent_listings': Property.objects.filter(
            is_verified=True,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count(),
    }
    
    # Convert Decimal to float for JSON serialization
    if stats['average_price']:
        stats['average_price'] = float(stats['average_price'])
    if stats['price_range']['min_price']:
        stats['price_range']['min_price'] = float(stats['price_range']['min_price'])
    if stats['price_range']['max_price']:
        stats['price_range']['max_price'] = float(stats['price_range']['max_price'])
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([AllowAny])
def county_properties_api(request, county_slug):
    """API endpoint for properties in a specific county"""
    try:
        county = County.objects.get(slug=county_slug, is_active=True)
        properties = Property.objects.filter(
            county=county,
            is_verified=True
        ).select_related('county').prefetch_related('media')
        
        # Apply filters
        property_type = request.query_params.get('property_type')
        if property_type:
            properties = properties.filter(property_type=property_type)
        
        min_price = request.query_params.get('min_price')
        if min_price:
            try:
                properties = properties.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        max_price = request.query_params.get('max_price')
        if max_price:
            try:
                properties = properties.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        bedrooms = request.query_params.get('bedrooms')
        if bedrooms:
            try:
                properties = properties.filter(bedrooms__gte=int(bedrooms))
            except ValueError:
                pass
        
        serializer = PropertyListSerializer(properties, many=True)
        return Response({
            'county': {
                'name': county.name,
                'slug': county.slug,
                'description': county.description
            },
            'properties': serializer.data,
            'count': properties.count()
        })
    except County.DoesNotExist:
        return Response(
            {'error': 'County not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def featured_properties_api(request):
    """API endpoint for featured properties"""
    # Get verified properties with images, ordered by creation date
    featured = Property.objects.filter(
        is_verified=True,
        media__isnull=False
    ).select_related('county').prefetch_related('media').distinct()[:6]
    
    serializer = PropertyListSerializer(featured, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def property_search_api(request):
    """Advanced property search API"""
    query = request.query_params.get('q', '')
    property_type = request.query_params.get('type', '')
    county = request.query_params.get('county', '')
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    bedrooms = request.query_params.get('bedrooms')
    bathrooms = request.query_params.get('bathrooms')
    sort_by = request.query_params.get('sort', 'newest')
    
    # Start with verified properties
    properties = Property.objects.filter(is_verified=True).select_related('county').prefetch_related('media')
    
    # Apply search query
    if query:
        properties = properties.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(county__name__icontains=query) |
            Q(county__main_towns__icontains=query)
        )
    
    # Apply filters
    if property_type:
        properties = properties.filter(property_type=property_type)
    
    if county:
        properties = properties.filter(county__slug=county)
    
    if min_price:
        try:
            properties = properties.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            properties = properties.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    if bedrooms:
        try:
            properties = properties.filter(bedrooms__gte=int(bedrooms))
        except ValueError:
            pass
    
    if bathrooms:
        try:
            properties = properties.filter(bathrooms__gte=int(bathrooms))
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'price_low':
        properties = properties.order_by('price')
    elif sort_by == 'price_high':
        properties = properties.order_by('-price')
    elif sort_by == 'bedrooms':
        properties = properties.order_by('-bedrooms')
    elif sort_by == 'area':
        properties = properties.order_by('-area')
    else:  # newest
        properties = properties.order_by('-created_at')
    
    serializer = PropertyListSerializer(properties, many=True)
    return Response({
        'properties': serializer.data,
        'count': properties.count(),
        'filters_applied': {
            'query': query,
            'type': property_type,
            'county': county,
            'min_price': min_price,
            'max_price': max_price,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'sort': sort_by
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_inquiry_api(request):
    """API endpoint for submitting property inquiries"""
    data = request.data
    
    # Validate required fields
    required_fields = ['name', 'email', 'message']
    for field in required_fields:
        if not data.get(field):
            return Response(
                {'error': f'{field} is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Create inquiry
    inquiry = Inquiry.objects.create(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone', ''),
        message=data['message'],
        inquiry_type=data.get('inquiry_type', 'general'),
        property_id=data.get('property_id')
    )
    
    return Response({
        'message': 'Inquiry submitted successfully',
        'inquiry_id': inquiry.id
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def testimonials_api(request):
    """API endpoint for testimonials"""
    testimonials = Testimonial.objects.filter(is_approved=True).order_by('-created_at')
    
    # Filter by featured if requested
    featured_only = request.query_params.get('featured')
    if featured_only:
        testimonials = testimonials.filter(is_featured=True)
    
    # Limit results
    limit = request.query_params.get('limit')
    if limit:
        try:
            testimonials = testimonials[:int(limit)]
        except ValueError:
            pass
    
    serializer_data = []
    for testimonial in testimonials:
        serializer_data.append({
            'id': testimonial.id,
            'name': testimonial.name,
            'role': testimonial.role,
            'content': testimonial.content,
            'rating': testimonial.rating,
            'is_featured': testimonial.is_featured,
            'created_at': testimonial.created_at
        })
    
    return Response(serializer_data)
