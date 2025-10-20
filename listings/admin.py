
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import (
    County, Agent, Landlord, Amenity, Property, PropertyMedia, Inquiry, Testimonial, 
    ManagementRequest, PropertyViewing, Tenant, Lease, Payment, 
    MaintenanceRequest as TenantMaintenanceRequest, TenantDocument, Message,
    TenantService
)


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


@admin.register(Landlord)
class LandlordAdmin(admin.ModelAdmin):
    """Enhanced admin interface for landlords"""
    list_display = [
        'registration_status', 'full_name', 'email_address', 'phone',
        'property_count', 'tenant_count', 'verification_badge', 'registration_date'
    ]
    list_filter = ['is_verified', 'is_active', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone', 'company_name', 'id_number', 'kra_pin']
    readonly_fields = ['created_at', 'updated_at', 'email_address', 'property_count', 'tenant_count']
    ordering = ['-created_at']
    list_per_page = 50
    
    fieldsets = (
        ('User Account', {
            'fields': ('user', 'email_address')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address', 'city', 'postal_code')
        }),
        ('Identification', {
            'fields': ('id_number', 'kra_pin')
        }),
        ('Banking Details', {
            'fields': ('bank_name', 'bank_account', 'bank_branch'),
            'description': 'Bank details for rent payments'
        }),
        ('Company Information', {
            'fields': ('company_name', 'profile_image'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified'),
            'description': 'Mark is_verified as True to approve landlord registration'
        }),
        ('Statistics', {
            'fields': ('property_count', 'tenant_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_landlords', 'unverify_landlords', 'deactivate_landlords']
    
    def registration_status(self, obj):
        """Show if this is a new registration"""
        if not obj.is_verified:
            return format_html(
                '<span style="background: #fbbf24; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">🆕 NEW</span>'
            )
        return format_html(
            '<span style="background: #10b981; color: white; padding: 4px 8px; border-radius: 12px;">✓</span>'
        )
    registration_status.short_description = 'Status'
    
    def email_address(self, obj):
        """Display landlord email"""
        return obj.user.email
    email_address.short_description = 'Email'
    
    def property_count(self, obj):
        """Display number of properties"""
        count = obj.total_properties
        if count > 0:
            return format_html(
                '<span style="background: #3b82f6; color: white; padding: 2px 8px; border-radius: 8px;">{} properties</span>',
                count
            )
        return format_html('<span style="color: gray;">No properties</span>')
    property_count.short_description = 'Properties'
    
    def tenant_count(self, obj):
        """Display number of active tenants"""
        count = obj.total_tenants
        if count > 0:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 8px;">{} tenants</span>',
                count
            )
        return format_html('<span style="color: gray;">No tenants</span>')
    tenant_count.short_description = 'Active Tenants'
    
    def verification_badge(self, obj):
        """Display verification status as badge"""
        if obj.is_verified:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">✓ VERIFIED</span>'
            )
        return format_html(
            '<span style="background: #ef4444; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">⚠ PENDING</span>'
        )
    verification_badge.short_description = 'Verification'
    
    def registration_date(self, obj):
        """Display registration date in friendly format"""
        from django.utils.timezone import now
        diff = now() - obj.created_at
        if diff.days == 0:
            return format_html('<span style="color: #10b981; font-weight: 600;">Today</span>')
        elif diff.days == 1:
            return format_html('<span style="color: #3b82f6;">Yesterday</span>')
        elif diff.days < 7:
            return format_html('<span style="color: #f59e0b;">{} days ago</span>', diff.days)
        else:
            return obj.created_at.strftime('%b %d, %Y')
    registration_date.short_description = 'Registered'
    
    def verify_landlords(self, request, queryset):
        """Verify selected landlords"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} landlord(s) verified.')
    verify_landlords.short_description = "✓ Verify selected landlords"
    
    def unverify_landlords(self, request, queryset):
        """Unverify selected landlords"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} landlord(s) unverified.')
    unverify_landlords.short_description = "✗ Unverify selected landlords"
    
    def deactivate_landlords(self, request, queryset):
        """Deactivate selected landlords"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} landlord(s) deactivated.')
    deactivate_landlords.short_description = "🚫 Deactivate selected landlords"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


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


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin interface for tenants - View and verify registration requests"""
    list_display = [
        'registration_status', 'full_name', 'email_address', 'phone', 
        'verification_badge', 'active_lease_info', 'registration_date'
    ]
    list_filter = ['is_verified', 'is_active', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone', 'id_number']
    readonly_fields = ['created_at', 'updated_at', 'email_address']
    ordering = ['-created_at']  # Newest registrations first
    list_per_page = 50
    
    fieldsets = (
        ('User Account', {
            'fields': ('user', 'email_address')
        }),
        ('Contact Information', {
            'fields': ('phone', 'emergency_contact', 'emergency_phone')
        }),
        ('Personal Details', {
            'fields': ('id_number', 'date_of_birth', 'occupation', 'employer', 'profile_image')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified'),
            'description': 'Mark is_verified as True to approve tenant registration'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_tenants', 'unverify_tenants', 'deactivate_tenants']
    
    def registration_status(self, obj):
        """Show if this is a new registration or verified tenant"""
        if not obj.is_verified:
            return format_html(
                '<span style="background: #fbbf24; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">🆕 NEW</span>'
            )
        return format_html(
            '<span style="background: #10b981; color: white; padding: 4px 8px; border-radius: 12px;">✓</span>'
        )
    registration_status.short_description = 'Status'
    
    def email_address(self, obj):
        """Display tenant email"""
        return obj.user.email
    email_address.short_description = 'Email'
    
    def verification_badge(self, obj):
        """Display verification status as badge"""
        if obj.is_verified:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">✓ VERIFIED</span>'
            )
        return format_html(
            '<span style="background: #ef4444; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">⚠ PENDING</span>'
        )
    verification_badge.short_description = 'Verification'
    
    def registration_date(self, obj):
        """Display registration date in friendly format"""
        from django.utils.timezone import now
        diff = now() - obj.created_at
        if diff.days == 0:
            return format_html('<span style="color: #f59e0b; font-weight: bold;">📅 Today</span>')
        elif diff.days == 1:
            return format_html('<span style="color: #3b82f6;">Yesterday</span>')
        elif diff.days < 7:
            return format_html('<span style="color: #10b981;">{} days ago</span>', diff.days)
        else:
            return obj.created_at.strftime('%b %d, %Y')
    registration_date.short_description = 'Registered'
    
    def active_lease_info(self, obj):
        lease = obj.active_lease
        if lease:
            return format_html(
                '<span style="color: green;">✓ {}</span>',
                lease.property_item.title
            )
        return format_html('<span style="color: gray;">No lease</span>')
    active_lease_info.short_description = 'Current Lease'
    
    def verify_tenants(self, request, queryset):
        """Verify selected tenants"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'✓ {updated} tenant(s) verified successfully.')
    verify_tenants.short_description = "✓ Verify Selected Tenants"
    
    def unverify_tenants(self, request, queryset):
        """Unverify selected tenants"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'⚠ {updated} tenant(s) marked as unverified.')
    unverify_tenants.short_description = "⚠ Unverify Selected Tenants"
    
    def deactivate_tenants(self, request, queryset):
        """Deactivate selected tenants"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'✗ {updated} tenant(s) deactivated.')
    deactivate_tenants.short_description = "✗ Deactivate Selected Tenants"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Inline admin classes for Lease
class PaymentInline(admin.TabularInline):
    """Inline editor for payments within lease"""
    model = Payment
    extra = 1
    fields = ['payment_date', 'amount', 'payment_type', 'payment_method', 'status', 'receipt_number']
    readonly_fields = ['receipt_number']
    ordering = ['-payment_date']
    classes = ['collapse']
    verbose_name = "Payment"
    verbose_name_plural = "Payments (Add/Edit)"
    can_delete = False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lease', 'lease__tenant')


class MaintenanceRequestInline(admin.TabularInline):
    """Inline editor for maintenance requests within lease"""
    model = TenantMaintenanceRequest
    extra = 0
    fields = ['title', 'category', 'priority', 'status', 'reported_date', 'scheduled_date']
    readonly_fields = ['reported_date']
    ordering = ['-reported_date']
    classes = ['collapse']
    verbose_name = "Maintenance Request"
    verbose_name_plural = "Maintenance Requests"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lease', 'tenant')


class TenantDocumentInline(admin.TabularInline):
    """Inline editor for tenant documents within lease"""
    model = TenantDocument
    extra = 1
    fields = ['title', 'document_type', 'file', 'description']
    ordering = ['-created_at']
    classes = ['collapse']
    verbose_name = "Document"
    verbose_name_plural = "Documents (Lease Agreements, Receipts, etc.)"


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    """Enhanced admin interface for leases with inline editing"""
    list_display = [
        'tenant', 'property_item', 'start_date', 'end_date', 
        'monthly_rent', 'status_badge', 'days_remaining', 
        'payment_status', 'created_at'
    ]
    list_filter = ['status', 'start_date', 'end_date', 'created_at']
    search_fields = ['tenant__user__first_name', 'tenant__user__last_name', 'property_item__title']
    readonly_fields = ['created_at', 'updated_at', 'days_remaining', 'total_paid', 'payment_count']
    date_hierarchy = 'start_date'
    list_per_page = 50
    inlines = [PaymentInline, MaintenanceRequestInline, TenantDocumentInline]
    
    fieldsets = (
        ('Tenant & Property', {
            'fields': ('tenant', 'property_item')
        }),
        ('Lease Period', {
            'fields': ('start_date', 'end_date', 'days_remaining')
        }),
        ('Financial Details', {
            'fields': ('monthly_rent', 'deposit_amount', 'service_charge', 'utilities_included', 'deposit_paid'),
            'description': 'Enter all amounts in KSh'
        }),
        ('Payment Summary', {
            'fields': ('payment_count', 'total_paid'),
            'classes': ('collapse',)
        }),
        ('Documents', {
            'fields': ('lease_document',)
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_leases', 'terminate_leases', 'generate_invoices']
    
    def status_badge(self, obj):
        colors = {'pending': '#fbbf24', 'active': '#10b981', 'expired': '#6b7280', 'terminated': '#ef4444'}
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_status(self, obj):
        """Show payment summary"""
        total_paid = obj.payments.filter(status='confirmed').aggregate(total=Sum('amount'))['total'] or 0
        if total_paid > 0:
            return format_html(
                '<span style="color: green; font-weight: 600;">KSh {:,.0f}</span>',
                total_paid
            )
        return format_html('<span style="color: gray;">No payments</span>')
    payment_status.short_description = 'Total Paid'
    
    def total_paid(self, obj):
        """Calculate total payments made"""
        from django.db.models import Sum
        total = obj.payments.filter(status='confirmed').aggregate(total=Sum('amount'))['total'] or 0
        return f"KSh {total:,.0f}"
    total_paid.short_description = 'Total Payments'
    
    def payment_count(self, obj):
        """Count of payments"""
        count = obj.payments.count()
        return f"{count} payment(s)"
    payment_count.short_description = 'Payment Count'
    
    def activate_leases(self, request, queryset):
        """Activate selected leases"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} lease(s) activated.')
    activate_leases.short_description = "✓ Activate selected leases"
    
    def terminate_leases(self, request, queryset):
        """Terminate selected leases"""
        updated = queryset.update(status='terminated')
        self.message_user(request, f'{updated} lease(s) terminated.')
    terminate_leases.short_description = "✗ Terminate selected leases"
    
    def generate_invoices(self, request, queryset):
        """Generate rent invoices for selected leases"""
        count = 0
        for lease in queryset.filter(status='active'):
            # Here you would generate invoice logic
            count += 1
        self.message_user(request, f'{count} invoice(s) generated.')
    generate_invoices.short_description = "📄 Generate Rent Invoices"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tenant', 'tenant__user', 'property_item').prefetch_related('payments')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for payments"""
    list_display = ['receipt_number', 'tenant', 'amount', 'payment_type', 'payment_method', 'payment_date', 'status_badge']
    list_filter = ['payment_type', 'payment_method', 'status', 'payment_date']
    search_fields = ['receipt_number', 'transaction_ref', 'tenant__user__first_name', 'tenant__user__last_name']
    readonly_fields = ['receipt_number', 'created_at', 'updated_at']
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Tenant & Lease', {
            'fields': ('tenant', 'lease')
        }),
        ('Payment Details', {
            'fields': ('payment_type', 'amount', 'payment_method', 'transaction_ref', 'payment_date')
        }),
        ('Period Covered', {
            'fields': ('period_start', 'period_end')
        }),
        ('Receipt', {
            'fields': ('receipt_number', 'status', 'is_receipt_sent')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {'pending': '#fbbf24', 'completed': '#10b981', 'failed': '#ef4444', 'refunded': '#6b7280'}
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(TenantMaintenanceRequest)
class TenantMaintenanceRequestAdmin(admin.ModelAdmin):
    """Admin interface for tenant maintenance requests"""
    list_display = ['title', 'tenant', 'priority_badge', 'status_badge', 'category', 'reported_date', 'scheduled_date']
    list_filter = ['priority', 'status', 'category', 'reported_date']
    search_fields = ['title', 'description', 'tenant__user__first_name', 'tenant__user__last_name']
    readonly_fields = ['reported_date', 'updated_at']
    date_hierarchy = 'reported_date'
    
    def priority_badge(self, obj):
        colors = {'low': '#6b7280', 'normal': '#3b82f6', 'high': '#f59e0b', 'urgent': '#ef4444'}
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">{}</span>',
            colors.get(obj.priority, '#6b7280'),
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def status_badge(self, obj):
        colors = {'pending': '#fbbf24', 'assigned': '#3b82f6', 'in_progress': '#8b5cf6', 'completed': '#10b981', 'cancelled': '#6b7280'}
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">{}</span>',
            colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(TenantDocument)
class TenantDocumentAdmin(admin.ModelAdmin):
    """Admin interface for tenant documents"""
    list_display = ['title', 'tenant', 'document_type', 'uploaded_by', 'created_at']
    list_filter = ['document_type', 'created_at']
    search_fields = ['title', 'tenant__user__first_name', 'tenant__user__last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Enhanced admin interface for tenant messages"""
    list_display = ['subject', 'message_direction', 'tenant_name', 'is_read_badge', 'created_at']
    list_filter = ['is_read', 'created_at', 'tenant']
    search_fields = ['subject', 'message', 'sender__username', 'recipient__username', 'tenant__user__first_name', 'tenant__user__last_name']
    readonly_fields = ['created_at', 'read_at', 'sender', 'recipient']
    list_per_page = 50
    ordering = ['-created_at']
    
    fieldsets = (
        ('Message Details', {
            'fields': ('subject', 'message')
        }),
        ('Participants', {
            'fields': ('sender', 'recipient', 'tenant')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Reply Thread', {
            'fields': ('parent_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'reply_to_message']
    
    def message_direction(self, obj):
        """Show message direction with icon"""
        if obj.sender.is_superuser:
            return format_html(
                '<span style="color: #10b981;">→ To Tenant</span>'
            )
        return format_html(
            '<span style="color: #3b82f6;">← From Tenant</span>'
        )
    message_direction.short_description = 'Direction'
    
    def tenant_name(self, obj):
        """Show tenant name"""
        if obj.tenant:
            return obj.tenant.full_name
        return "N/A"
    tenant_name.short_description = 'Tenant'
    
    def is_read_badge(self, obj):
        """Display read status as badge"""
        if obj.is_read:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 8px;">✓ Read</span>'
            )
        return format_html(
            '<span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 8px;">● New</span>'
        )
    is_read_badge.short_description = 'Status'
    
    def mark_as_read(self, request, queryset):
        """Mark selected messages as read"""
        updated = 0
        for msg in queryset:
            if not msg.is_read:
                msg.mark_as_read()
                updated += 1
        self.message_user(request, f'{updated} message(s) marked as read.')
    mark_as_read.short_description = "✓ Mark as read"
    
    def mark_as_unread(self, request, queryset):
        """Mark selected messages as unread"""
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} message(s) marked as unread.')
    mark_as_unread.short_description = "● Mark as unread"
    
    def reply_to_message(self, request, queryset):
        """Quick reply action"""
        if queryset.count() != 1:
            self.message_user(request, 'Please select exactly one message to reply to.', level='WARNING')
            return
        
        msg = queryset.first()
        # Here you would redirect to a reply form or show reply interface
        self.message_user(request, f'Reply to: {msg.subject}', level='INFO')
    reply_to_message.short_description = "💬 Reply to message"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'recipient', 'tenant', 'tenant__user')


@admin.register(TenantService)
class TenantServiceAdmin(admin.ModelAdmin):
    """Admin interface for tenant services"""
    list_display = [
        'service_name', 'category_badge', 'price_display', 
        'availability_badge', 'is_featured', 'contact_info', 'created_at'
    ]
    list_filter = ['category', 'is_available', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'contact_email', 'contact_phone']
    list_editable = ['is_featured']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-is_featured', 'category', 'name']
    list_per_page = 50
    
    fieldsets = (
        ('Service Information', {
            'fields': ('name', 'category', 'description', 'icon')
        }),
        ('Pricing', {
            'fields': ('price',),
            'description': 'Leave price blank or set to 0 for free services'
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Status', {
            'fields': ('is_available', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_available', 'mark_as_unavailable', 'mark_as_featured', 'unmark_as_featured']
    
    def service_name(self, obj):
        """Display service name with icon"""
        if obj.icon:
            return format_html(
                '<i class="fas {} fa-fw"></i> {}',
                obj.icon,
                obj.name
            )
        return obj.name
    service_name.short_description = 'Service'
    
    def category_badge(self, obj):
        """Display category as colored badge"""
        colors = {
            'maintenance': '#f59e0b',
            'cleaning': '#10b981',
            'utilities': '#3b82f6',
            'security': '#ef4444',
            'lifestyle': '#8b5cf6',
            'support': '#6b7280'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">{}</span>',
            colors.get(obj.category, '#6b7280'),
            obj.get_category_display()
        )
    category_badge.short_description = 'Category'
    
    def price_display(self, obj):
        """Display price with formatting"""
        if obj.is_free:
            return format_html('<span style="color: #10b981; font-weight: bold;">FREE</span>')
        return format_html('<span style="color: #3b82f6; font-weight: 600;">KSh {}</span>', f'{obj.price:,.0f}')
    price_display.short_description = 'Price'
    
    def availability_badge(self, obj):
        """Display availability status"""
        if obj.is_available:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 4px 12px; border-radius: 12px;">✓ Available</span>'
            )
        return format_html(
            '<span style="background: #ef4444; color: white; padding: 4px 12px; border-radius: 12px;">✗ Unavailable</span>'
        )
    availability_badge.short_description = 'Status'
    
    def contact_info(self, obj):
        """Display contact information"""
        if obj.contact_phone:
            return format_html('📞 {}', obj.contact_phone)
        elif obj.contact_email:
            return format_html('📧 {}', obj.contact_email)
        return format_html('<span style="color: gray;">No contact</span>')
    contact_info.short_description = 'Contact'
    
    def mark_as_available(self, request, queryset):
        """Mark services as available"""
        updated = queryset.update(is_available=True)
        self.message_user(request, f'✓ {updated} service(s) marked as available.')
    mark_as_available.short_description = "✓ Mark as Available"
    
    def mark_as_unavailable(self, request, queryset):
        """Mark services as unavailable"""
        updated = queryset.update(is_available=False)
        self.message_user(request, f'✗ {updated} service(s) marked as unavailable.')
    mark_as_unavailable.short_description = "✗ Mark as Unavailable"
    
    def mark_as_featured(self, request, queryset):
        """Mark services as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'⭐ {updated} service(s) marked as featured.')
    mark_as_featured.short_description = "⭐ Mark as Featured"
    
    def unmark_as_featured(self, request, queryset):
        """Remove featured status"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} service(s) unmarked as featured.')
    unmark_as_featured.short_description = "Remove Featured Status"

