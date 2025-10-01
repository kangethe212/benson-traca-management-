
from django.contrib import admin
from django.utils.html import format_html
from .models import County, Agent, Amenity, Property, PropertyMedia, Inquiry, Testimonial, ManagementRequest


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'phone', 'license_number', 'is_active', 'is_verified', 'created_at']
    list_filter = ['is_active', 'is_verified', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'phone', 'license_number']
    list_editable = ['is_active', 'is_verified']
    readonly_fields = ['created_at', 'updated_at']


class PropertyMediaInline(admin.TabularInline):
    model = PropertyMedia
    extra = 1
    fields = ['media_type', 'file', 'caption', 'is_primary', 'order']
    ordering = ['order']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'property_type', 'county', 'price', 'is_verified', 'created_at'
    ]
    list_filter = [
        'property_type', 'county', 'is_verified', 'created_at'
    ]
    search_fields = ['title', 'description']
    list_editable = ['is_verified']
    readonly_fields = ['created_at']
    inlines = [PropertyMediaInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'property_type')
        }),
        ('Pricing & Details', {
            'fields': ('price', 'area', 'bedrooms', 'bathrooms', 'bathtubs', 'washrooms', 'parking_slots')
        }),
        ('Location', {
            'fields': ('county',)
        }),
        ('Media & Verification', {
            'fields': ('is_verified', 'virtual_tour_url', 'video_tour')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('county')


@admin.register(PropertyMedia)
class PropertyMediaAdmin(admin.ModelAdmin):
    list_display = ['property', 'media_type', 'caption', 'is_primary', 'order', 'created_at']
    list_filter = ['media_type', 'is_primary', 'created_at']
    search_fields = ['property__title', 'caption']
    list_editable = ['is_primary', 'order']
    ordering = ['property', 'order']


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'inquiry_type', 'property', 
        'is_read', 'is_responded', 'created_at'
    ]
    list_filter = ['inquiry_type', 'is_read', 'is_responded', 'created_at']
    search_fields = ['name', 'email', 'phone', 'message', 'property__title']
    list_editable = ['is_read', 'is_responded']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Inquiry Details', {
            'fields': ('inquiry_type', 'message', 'property')
        }),
        ('Status', {
            'fields': ('is_read', 'is_responded')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'rating', 'property', 'is_featured', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_featured', 'is_approved', 'created_at']
    search_fields = ['name', 'role', 'content', 'property__title']
    list_editable = ['is_featured', 'is_approved']
    readonly_fields = ['created_at']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


@admin.register(ManagementRequest)
class ManagementRequestAdmin(admin.ModelAdmin):
    list_display = [
        'landlord_name', 'landlord_contact', 'property', 'rent_amount', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['landlord_name', 'landlord_contact', 'property__title']
    list_editable = ['status']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Landlord Information', {
            'fields': ('landlord_name', 'landlord_contact')
        }),
        ('Property Details', {
            'fields': ('property', 'rent_amount', 'service_terms')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

