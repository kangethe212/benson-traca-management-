from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('properties/', views.properties_list, name='properties_list'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('agent/<int:pk>/', views.agent_detail, name='agent_detail'),
    path('contact/', views.contact_view, name='contact'),
    path('services/', views.services_view, name='services'),
    path('about/', views.about_view, name='about'),
    
    # Property management
    path('management-request/', views.management_request, name='management_request'),
    path('admin/management-requests/', views.management_requests_list, name='management_requests_list'),
    
    # API endpoints
    path('api/search/', views.property_search_api, name='property_search_api'),
]
