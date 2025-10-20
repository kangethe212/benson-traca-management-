"""
URL configuration for landlord portal
"""

from django.urls import path
from . import landlord_views

app_name = 'landlord'

urlpatterns = [
    # Authentication
    path('login/', landlord_views.landlord_login, name='login'),
    path('register/', landlord_views.landlord_register, name='register'),
    path('logout/', landlord_views.landlord_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', landlord_views.landlord_dashboard, name='dashboard'),
    
    # Properties
    path('properties/', landlord_views.landlord_properties, name='properties'),
    path('properties/add/', landlord_views.landlord_property_add, name='property_add'),
    path('properties/<int:property_id>/', landlord_views.landlord_property_detail, name='property_detail'),
    
    # Tenants
    path('tenants/', landlord_views.landlord_tenants, name='tenants'),
    path('tenants/<int:tenant_id>/', landlord_views.landlord_tenant_detail, name='tenant_detail'),
    
    # Financials
    path('financials/', landlord_views.landlord_financials, name='financials'),
    
    # Maintenance
    path('maintenance/', landlord_views.landlord_maintenance, name='maintenance'),
    
    # Profile
    path('profile/', landlord_views.landlord_profile, name='profile'),
    
    # Advanced Features
    path('reports/', landlord_views.landlord_reports, name='reports'),
    path('export/', landlord_views.landlord_export_data, name='export_data'),
    path('bulk-operations/', landlord_views.landlord_bulk_operations, name='bulk_operations'),
]

