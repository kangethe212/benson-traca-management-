
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
    extra = 3
    fields = ['media_type', 'file', 'caption', 'is_primary', 'order']
    ordering = ['order']
    classes = ['collapse']
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Add help text for media types
        formset.form.base_fields['media_type'].help_text = 'Choose image for photos, video for property videos'
        formset.form.base_fields['is_primary'].help_text = 'Only one primary image per property'
        formset.form.base_fields['order'].help_text = 'Display order (1 = first)'
        return formset


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'property_type', 'county', 'price', 'bedrooms', 'bathrooms', 'is_verified', 'media_count', 'created_at'
    ]
    list_filter = [
        'property_type', 'county', 'is_verified', 'bedrooms', 'bathrooms', 'created_at'
    ]
    search_fields = ['title', 'description', 'county__name']
    list_editable = ['is_verified']
    readonly_fields = ['created_at', 'media_count']
    inlines = [PropertyMediaInline]
    list_per_page = 25
    
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
            'fields': ('is_verified', 'virtual_tour_url', 'video_tour', 'media_count')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('county').prefetch_related('media')
    
    def media_count(self, obj):
        """Display the number of media files for this property"""
        count = obj.media.count()
        if count == 0:
            return format_html('<span style="color: red;">No media</span>')
        elif count == 1:
            return format_html('<span style="color: orange;">1 file</span>')
        else:
            return format_html('<span style="color: green;">{} files</span>', count)
    media_count.short_description = 'Media Files'
    media_count.admin_order_field = 'media__count'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add help text for important fields
        form.base_fields['title'].help_text = 'Enter a descriptive title for the property'
        form.base_fields['price'].help_text = 'Enter price in KSh (e.g., 5000000 for 5 million)'
        form.base_fields['area'].help_text = 'Enter area in square feet'
        form.base_fields['virtual_tour_url'].help_text = 'URL for virtual tour (e.g., Matterport, 360° tour)'
        form.base_fields['video_tour'].help_text = 'Upload a video file for property tour'
        return form
    
    actions = ['mark_as_verified', 'mark_as_unverified', 'duplicate_property']
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:property_id>/bulk-upload/',
                self.admin_site.admin_view(self.bulk_media_upload_view),
                name='listings_property_bulk_upload',
            ),
            path(
                '<int:property_id>/media-manager/',
                self.admin_site.admin_view(self.media_manager_view),
                name='listings_property_media_manager',
            ),
        ]
        return custom_urls + urls
    
    def bulk_media_upload_view(self, request, property_id):
        """Redirect to custom bulk upload view"""
        from django.shortcuts import redirect
        return redirect(f'/admin/listings/property/{property_id}/bulk-upload/')
    
    def media_manager_view(self, request, property_id):
        """Redirect to custom media manager view"""
        from django.shortcuts import redirect
        return redirect(f'/admin/listings/property/{property_id}/media-manager/')
    
    def mark_as_verified(self, request, queryset):
        """Mark selected properties as verified"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} properties marked as verified.')
    mark_as_verified.short_description = "Mark selected properties as verified"
    
    def mark_as_unverified(self, request, queryset):
        """Mark selected properties as unverified"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} properties marked as unverified.')
    mark_as_unverified.short_description = "Mark selected properties as unverified"
    
    def duplicate_property(self, request, queryset):
        """Duplicate selected properties"""
        for property_obj in queryset:
            # Create a copy of the property
            property_obj.pk = None
            property_obj.title = f"{property_obj.title} (Copy)"
            property_obj.is_verified = False
            property_obj.save()
        self.message_user(request, f'{queryset.count()} properties duplicated.')
    duplicate_property.short_description = "Duplicate selected properties"


@admin.register(PropertyMedia)
class PropertyMediaAdmin(admin.ModelAdmin):
    list_display = ['property', 'media_type', 'file_preview', 'caption', 'is_primary', 'order', 'created_at']
    list_filter = ['media_type', 'is_primary', 'created_at']
    search_fields = ['property__title', 'caption']
    list_editable = ['is_primary', 'order']
    ordering = ['property', 'order']
    list_per_page = 50
    
    fieldsets = (
        ('Media Information', {
            'fields': ('property', 'media_type', 'file', 'caption')
        }),
        ('Display Settings', {
            'fields': ('is_primary', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    def file_preview(self, obj):
        """Show a preview of the media file"""
        if obj.file:
            if obj.media_type == 'image':
                return format_html(
                    '<img src="{}" style="max-width: 100px; max-height: 60px; object-fit: cover;" />',
                    obj.file.url
                )
            else:
                return format_html(
                    '<a href="{}" target="_blank">📹 Video File</a>',
                    obj.file.url
                )
        return "No file"
    file_preview.short_description = 'Preview'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['media_type'].help_text = 'Choose "image" for photos, "video" for property videos'
        form.base_fields['is_primary'].help_text = 'Only one primary image per property (used as main image)'
        form.base_fields['order'].help_text = 'Display order (1 = first, 2 = second, etc.)'
        return form


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

