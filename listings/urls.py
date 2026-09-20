from django.urls import path, re_path
from django.shortcuts import redirect
from . import views

app_name = 'listings'


def _portal_redirect(request, prefix):
    views._dbg('C', 'listings/urls.py:_portal_redirect', 'legacy portal path hit', {
        'path': request.path,
        'prefix': prefix,
    })
    return redirect('listings:contact')


urlpatterns = [
    # Portal deactivation redirects (keep old links from breaking)
    re_path(r'^landlord(?:/.*)?$', lambda request: _portal_redirect(request, 'landlord')),
    re_path(r'^tenant(?:/.*)?$', lambda request: _portal_redirect(request, 'tenant')),

    # Main pages
    path('', views.home, name='home'),
    path('properties/', views.properties_list, name='properties_list'),
    path('properties/compare/', views.property_compare, name='property_compare'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('properties/<int:pk>/inquiry/', views.property_inquiry, name='property_inquiry'),
    path('properties/<int:pk>/book-viewing/', views.book_property_viewing, name='book_viewing'),
    path('viewing/<int:pk>/confirmation/', views.viewing_confirmation, name='viewing_confirmation'),
    path('property-compare/', views.property_compare, name='property_compare_legacy'),
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
    path('services/', views.services_view, name='services'),
    
    # API endpoints
    path('api/search/', views.property_search_api, name='property_search_api'),
]
