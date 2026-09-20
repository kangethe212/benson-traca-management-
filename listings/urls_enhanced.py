"""
Enhanced URLs configuration for TRACA Management listings app
Optimized for performance and mobile responsiveness
"""

from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from . import views_enhanced as views

app_name = 'listings'

# Cache durations (in seconds)
CACHE_DURATION_SHORT = 300      # 5 minutes
CACHE_DURATION_MEDIUM = 1800    # 30 minutes
CACHE_DURATION_LONG = 3600      # 1 hour

urlpatterns = [
    # Homepage with enhanced caching
    path('', views.home, name='home'),
    
    # Enhanced properties list with advanced filtering
    path('properties/', views.properties_list, name='properties_list'),
    
    # Property detail with caching
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    
    # API endpoints with caching
    path('api/search/', views.property_search_api, name='property_search_api'),
    path('api/counties/', cache_page(CACHE_DURATION_LONG)(views.counties_api), name='counties_api'),
    
    # Property inquiry
    path('property/<int:pk>/inquiry/', views.property_inquiry, name='property_inquiry'),
    
    # Viewing booking
    path('property/<int:property_id>/book-viewing/', views.book_viewing, name='book_viewing'),
    path('viewing/<int:viewing_id>/confirmation/', views.viewing_confirmation, name='viewing_confirmation'),
    
    # Static pages with caching
    path('about/', cache_page(CACHE_DURATION_LONG)(views.about), name='about'),
    path('services/', cache_page(CACHE_DURATION_LONG)(views.services), name='services'),
    path('contact/', views.contact, name='contact'),
    
    # Property management
    path('management-request/', views.management_request, name='management_request'),
    path('management-request/success/', views.management_request_success, name='management_request_success'),
    
    # Admin views
    path('management-requests/', views.management_requests_list, name='management_requests_list'),
    
    # Legacy URLs for backward compatibility
    path('list-property/', views.management_request, name='list_property'),
    path('property-compare/', cache_page(CACHE_DURATION_SHORT)(views.property_compare), name='property_compare'),
]

# Enhanced error handlers (will be configured in main urls.py)
handler404 = 'listings.views_enhanced.custom_404'
handler500 = 'listings.views_enhanced.custom_500'
