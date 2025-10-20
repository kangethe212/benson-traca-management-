from django.urls import path, include
from . import views
from . import tenant_views
from . import admin_views
from . import landlord_views

app_name = 'listings'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('properties/', views.properties_list, name='properties_list'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('properties/compare/', views.property_compare, name='property_compare'),
    path('properties/<int:pk>/book-viewing/', views.book_property_viewing, name='book_viewing'),
    path('viewing/confirmation/<int:pk>/', views.viewing_confirmation, name='viewing_confirmation'),
    path('agent/<int:pk>/', views.agent_detail, name='agent_detail'),
    path('contact/', views.contact_view, name='contact'),
    path('services/', views.services_view, name='services'),
    path('about/', views.about_view, name='about'),
    
    # Property management
    path('management-request/', views.management_request, name='management_request'),
    path('admin/management-requests/', views.management_requests_list, name='management_requests_list'),
    
    # API endpoints
    path('api/search/', views.property_search_api, name='property_search_api'),
    
    # Tenant Authentication
    path('tenant/login/', tenant_views.tenant_login, name='tenant_login'),
    path('tenant/register/', tenant_views.tenant_register, name='tenant_register'),
    path('tenant/logout/', tenant_views.tenant_logout, name='tenant_logout'),
    
    # Tenant Portal
    path('tenant/', tenant_views.tenant_dashboard, name='tenant_portal'),
    path('tenant/dashboard/', tenant_views.tenant_dashboard, name='tenant_dashboard'),
    path('tenant/profile/', tenant_views.tenant_profile, name='tenant_profile'),
    path('tenant/payments/', tenant_views.tenant_payments, name='tenant_payments'),
    path('tenant/maintenance/', tenant_views.tenant_maintenance, name='tenant_maintenance'),
    path('tenant/documents/', tenant_views.tenant_documents, name='tenant_documents'),
    path('tenant/messages/', tenant_views.tenant_messages, name='tenant_messages'),
    path('tenant/services/', tenant_views.tenant_services, name='tenant_services'),
    path('tenant/registration/', tenant_views.tenant_registration, name='tenant_registration'),
    path('tenant/complete-profile/', tenant_views.tenant_complete_profile, name='tenant_complete_profile'),
    
    # Landlord Portal
    path('landlord/', include('listings.landlord_urls', namespace='landlord')),
]
