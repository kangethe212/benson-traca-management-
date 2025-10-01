from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.property_search, name='property_search'),
    path('properties/', views.properties_list, name='properties_list'),
    path('property/<int:property_id>/', views.property_detail, name='property_detail'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
    path('list-property/', views.list_property, name='list_property'),
]
