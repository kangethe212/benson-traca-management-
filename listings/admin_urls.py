from django.urls import path
from . import admin_views

urlpatterns = [
    path('property/<int:property_id>/bulk-upload/', admin_views.bulk_media_upload, name='bulk_media_upload'),
    path('property/<int:property_id>/media-manager/', admin_views.property_media_manager, name='property_media_manager'),
    path('property/<int:property_id>/ajax-upload/', admin_views.ajax_media_upload, name='ajax_media_upload'),
]
