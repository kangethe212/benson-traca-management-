from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('properties/', views.properties_list, name='properties_list'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('properties/<int:pk>/inquiry/', views.property_inquiry, name='property_inquiry'),
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    
    # API endpoints
    path('api/search/', views.property_search_api, name='property_search_api'),
]
