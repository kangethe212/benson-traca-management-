from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    PropertyListAPIView, PropertyDetailAPIView, PropertyMediaListAPIView,
    property_statistics_api, county_properties_api, featured_properties_api,
    property_search_api, submit_inquiry_api, testimonials_api
)

# Create a router for API endpoints
router = DefaultRouter()

urlpatterns = [
    # Core API endpoints
    path('properties/', PropertyListAPIView.as_view(), name='api-property-list'),
    path('properties/<int:pk>/', PropertyDetailAPIView.as_view(), name='api-property-detail'),
    path('media/', PropertyMediaListAPIView.as_view(), name='api-media-list'),
    
    # Enhanced API endpoints
    path('statistics/', property_statistics_api, name='api-property-statistics'),
    path('counties/<str:county_slug>/properties/', county_properties_api, name='api-county-properties'),
    path('featured/', featured_properties_api, name='api-featured-properties'),
    path('search/', property_search_api, name='api-property-search'),
    path('inquiries/', submit_inquiry_api, name='api-submit-inquiry'),
    path('testimonials/', testimonials_api, name='api-testimonials'),
]
