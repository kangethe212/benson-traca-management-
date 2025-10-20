"""
URL Configuration for Tenant Portal
Traca Management Services
"""

from django.urls import path
from . import tenant_views

app_name = 'tenant'

urlpatterns = [
    # Authentication
    path('login/', tenant_views.tenant_login, name='login'),
    path('register/', tenant_views.tenant_register, name='register'),
    path('logout/', tenant_views.tenant_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', tenant_views.tenant_dashboard, name='dashboard'),
    
    # Payments
    path('payments/', tenant_views.tenant_payments, name='payments'),
    path('payments/<int:payment_id>/receipt/', tenant_views.tenant_download_receipt, name='download_receipt'),
    
    # Maintenance
    path('maintenance/', tenant_views.tenant_maintenance, name='maintenance'),
    
    # Documents
    path('documents/', tenant_views.tenant_documents, name='documents'),
    
    # Messages
    path('messages/', tenant_views.tenant_messages, name='messages'),
    
    # Services
    path('services/', tenant_views.tenant_services, name='services'),
    
    # Profile
    path('profile/', tenant_views.tenant_profile, name='profile'),
    
    # Advanced Features
    path('notifications/', tenant_views.tenant_notifications, name='notifications'),
    path('lease-calculator/', tenant_views.tenant_lease_calculator, name='lease_calculator'),
    path('service-requests/', tenant_views.tenant_service_requests, name='service_requests'),
    path('preferences/', tenant_views.tenant_preferences, name='preferences'),
]

