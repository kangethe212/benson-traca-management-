
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from . import admin_views
from .models import (
    County, Agent, Amenity, Property, PropertyMedia, Inquiry, ManagementRequest,
    Testimonial, PropertyViewing, TeamMember, HomepageHeroSettings
)


@admin.register(HomepageHeroSettings)
class HomepageHeroSettingsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'updated_at']
    fieldsets = (
        ('Hero Settings', {
            'fields': ('title', 'hero_image', 'hero_image_url', 'is_active')
        }),
    )

    def has_add_permission(self, request):
        return not HomepageHeroSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'main_towns_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'main_towns']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Location Details', {
            'fields': ('main_towns',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def main_towns_count(self, obj):
        """Display the number of main towns"""
        if obj.main_towns:
            towns = [town.strip() for town in obj.main_towns.split(',') if town.strip()]
            return f"{len(towns)} towns"
        return "No towns listed"
    main_towns_count.short_description = 'Main Towns'


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
    search_fields = ['title', 'description', 'county__name', 'town']
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
            'fields': ('county', 'town')
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
                self.admin_site.admin_view(admin_views.bulk_media_upload),
                name='listings_property_bulk_upload',
            ),
            path(
                '<int:property_id>/media-manager/',
                self.admin_site.admin_view(admin_views.property_media_manager),
                name='listings_property_media_manager',
            ),
        ]
        return custom_urls + urls
    
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


@admin.register(ManagementRequest)
class ManagementRequestAdmin(admin.ModelAdmin):
    list_display = ['landlord_name', 'landlord_contact', 'property', 'rent_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['landlord_name', 'landlord_contact', 'property__title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'rating', 'property', 'is_featured', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_featured', 'is_approved', 'created_at']
    search_fields = ['name', 'role', 'content', 'property__title']
    list_editable = ['is_featured', 'is_approved']
    readonly_fields = ['created_at']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    """Enhanced admin for managing property amenities"""
    list_display = ['name', 'icon_preview', 'is_active', 'property_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['name']
    list_per_page = 50
    
    fieldsets = (
        ('Amenity Information', {
            'fields': ('name', 'icon', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'property_count']
    
    def icon_preview(self, obj):
        """Show the FontAwesome icon preview"""
        if obj.icon:
            return format_html(
                '<i class="{}" style="font-size: 20px; color: #1e3a8a;"></i> {}',
                obj.icon, obj.icon
            )
        return "No icon"
    icon_preview.short_description = 'Icon'
    
    def property_count(self, obj):
        """Show how many properties use this amenity"""
        count = obj.properties.count()
        if count > 0:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 8px;">{} properties</span>',
                count
            )
        return format_html('<span style="color: gray;">Not used yet</span>')
    property_count.short_description = 'Usage'
    
    actions = ['activate_amenities', 'deactivate_amenities']
    
    def activate_amenities(self, request, queryset):
        """Activate selected amenities"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} amenities activated.')
    activate_amenities.short_description = "✓ Activate selected amenities"
    
    def deactivate_amenities(self, request, queryset):
        """Deactivate selected amenities"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} amenities deactivated.')
    deactivate_amenities.short_description = "✗ Deactivate selected amenities"
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['icon'].help_text = 'Enter FontAwesome icon class (e.g., "fas fa-wifi")'
        return form


@admin.register(PropertyViewing)
class PropertyViewingAdmin(admin.ModelAdmin):
    """Admin interface for property viewing bookings - Daytime only (9 AM - 6 PM)"""
    list_display = [
        'booking_info', 'property_item', 'viewing_date', 'viewing_time', 
        'name', 'phone', 'number_of_people', 'status_badge', 'created_at'
    ]
    list_filter = ['status', 'viewing_date', 'created_at', 'is_notified', 'confirmation_sent']
    search_fields = ['name', 'email', 'phone', 'property_item__title', 'property_item__county__name']
    readonly_fields = ['created_at', 'updated_at', 'is_notified', 'confirmation_sent']
    date_hierarchy = 'viewing_date'
    list_per_page = 50
    ordering = ['-viewing_date', '-viewing_time']
    
    fieldsets = (
        ('Property Information', {
            'fields': ('property_item',)
        }),
        ('Customer Details', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Viewing Schedule', {
            'fields': ('viewing_date', 'viewing_time', 'number_of_people'),
            'description': 'Viewings are only available during daytime hours (9 AM - 6 PM)'
        }),
        ('Additional Information', {
            'fields': ('message',)
        }),
        ('Status & Notifications', {
            'fields': ('status', 'is_notified', 'confirmation_sent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def booking_info(self, obj):
        """Display booking info with icon"""
        if obj.is_today:
            return format_html(
                '<span style="color: orange; font-weight: bold;">🔥 TODAY - {}</span>',
                obj.get_viewing_time_display()
            )
        elif obj.is_upcoming:
            return format_html(
                '<span style="color: green;">📅 {}</span>',
                obj.viewing_date.strftime('%b %d')
            )
        else:
            return format_html(
                '<span style="color: gray;">⏰ Past</span>'
            )
    booking_info.short_description = 'Booking Status'
    
    def status_badge(self, obj):
        """Display colored status badge"""
        colors = {
            'pending': '#fbbf24',
            'confirmed': '#10b981',
            'cancelled': '#ef4444',
            'completed': '#6b7280'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    actions = ['mark_as_confirmed', 'mark_as_cancelled', 'mark_as_completed', 'send_reminder_email']
    
    def mark_as_confirmed(self, request, queryset):
        """Confirm selected viewings"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} viewing(s) marked as confirmed.')
    mark_as_confirmed.short_description = "✓ Mark as Confirmed"
    
    def mark_as_cancelled(self, request, queryset):
        """Cancel selected viewings"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} viewing(s) cancelled.')
    mark_as_cancelled.short_description = "✗ Mark as Cancelled"
    
    def mark_as_completed(self, request, queryset):
        """Mark selected viewings as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} viewing(s) marked as completed.')
    mark_as_completed.short_description = "✓ Mark as Completed"
    
    def send_reminder_email(self, request, queryset):
        """Send reminder emails for upcoming viewings"""
        from .notifications import NotificationService
        count = 0
        for viewing in queryset.filter(status__in=['pending', 'confirmed']):
            if viewing.is_upcoming:
                try:
                    message = f"""
Viewing Reminder

Dear {viewing.name},

This is a reminder of your upcoming property viewing:

Property: {viewing.property_item.title}
Date: {viewing.viewing_date.strftime('%A, %B %d, %Y')}
Time: {viewing.get_viewing_time_display()}
Location: {viewing.property_item.county.name}

Please arrive 5 minutes early. If you need to cancel or reschedule, please contact us.

Best regards,
Traca Management Team
                    """
                    NotificationService.send_email(
                        subject="Reminder: Property Viewing Tomorrow",
                        message=message,
                        recipient_list=[viewing.email]
                    )
                    count += 1
                except Exception:
                    pass
        
        self.message_user(request, f'{count} reminder email(s) sent.')
    send_reminder_email.short_description = "📧 Send Reminder Emails"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property_item', 'property_item__county')


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """Admin interface for team members"""
    list_display = [
        'photo_preview', 'name', 'title', 'order', 'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'title', 'bio']
    list_editable = ['order', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['order', 'name']
    list_per_page = 20
    
    fieldsets = (
        ('Team Member Information', {
            'fields': ('name', 'title', 'bio')
        }),
        ('Photo', {
            'fields': ('photo',),
            'description': 'Upload a square photo (120x120px recommended for best display)'
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
            'description': 'Order: 0 = first, 1 = second, etc.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def photo_preview(self, obj):
        """Show a preview of the team member photo"""
        if obj.photo:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 50%; border: 2px solid #C9A227;" />',
                obj.photo.url
            )
        return "No photo"
    photo_preview.short_description = 'Photo'
    
    actions = ['activate_members', 'deactivate_members']
    
    def activate_members(self, request, queryset):
        """Activate selected team members"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✓ {updated} team member(s) activated.')
    activate_members.short_description = "✓ Activate Selected Members"
    
    def deactivate_members(self, request, queryset):
        """Deactivate selected team members"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'✗ {updated} team member(s) deactivated.')
    deactivate_members.short_description = "✗ Deactivate Selected Members"

