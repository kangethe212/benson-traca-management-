from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PropertyListAPIView, PropertyDetailAPIView, PropertyMediaListAPIView

# Create a router for API endpoints
router = DefaultRouter()

urlpatterns = [
    # API endpoints
    path('properties/', PropertyListAPIView.as_view(), name='api-property-list'),
    path('properties/<int:pk>/', PropertyDetailAPIView.as_view(), name='api-property-detail'),
    path('media/', PropertyMediaListAPIView.as_view(), name='api-media-list'),
]
