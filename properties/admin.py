from django.contrib import admin
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'county', 'price', 'bedrooms', 'bathrooms', 'status', 'is_featured', 'created_at']
    list_filter = ['county', 'property_type', 'status', 'is_featured', 'created_at']
    search_fields = ['title', 'location', 'county', 'description']
    list_editable = ['status', 'is_featured']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'property_type', 'status', 'is_featured')
        }),
        ('Location', {
            'fields': ('location', 'county')
        }),
        ('Property Details', {
            'fields': ('price', 'bedrooms', 'bathrooms', 'parking', 'area')
        }),
        ('Images', {
            'fields': ('main_image', 'image_2', 'image_3')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']