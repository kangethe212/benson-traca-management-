"""
TRACA Management - Custom Admin Configuration
Enhanced admin interface with TRACA branding and improved functionality
"""

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import path
from django.shortcuts import render
from django.contrib import messages

from listings.models import Property, Tenant, Landlord, Lease, Payment, MaintenanceRequest, Message
from django.db.models import Sum, Avg, Count
from datetime import datetime, timedelta
import calendar

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """Custom admin for log entries with better display"""
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
    list_filter = ('action_time', 'user', 'content_type', 'action_flag')
    search_fields = ('user__username', 'object_repr', 'change_message')
    date_hierarchy = 'action_time'
    readonly_fields = ('action_time', 'user', 'content_type', 'object_id', 'object_repr', 'action_flag', 'change_message')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class PropertyAdmin(admin.ModelAdmin):
    """Enhanced Property admin with TRACA branding"""
    list_display = ('title', 'property_type', 'status', 'price_display', 'location_display', 'featured_badge', 'created_at')
    list_filter = ('property_type', 'status', 'featured', 'county', 'created_at')
    search_fields = ('title', 'description', 'location', 'county__name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('amenities',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'property_type', 'status')
        }),
        ('Location', {
            'fields': ('location', 'county', 'coordinates')
        }),
        ('Pricing', {
            'fields': ('price', 'price_type')
        }),
        ('Features', {
            'fields': ('bedrooms', 'bathrooms', 'square_feet', 'parking_spaces', 'featured')
        }),
        ('Media', {
            'fields': ('main_image', 'gallery_images')
        }),
        ('Amenities', {
            'fields': ('amenities',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        if obj.price_type == 'rent':
            return f"KES {obj.price:,}/month"
        return f"KES {obj.price:,}"
    price_display.short_description = 'Price'
    
    def location_display(self, obj):
        return f"{obj.location}, {obj.county.name if obj.county else 'Unknown'}"
    location_display.short_description = 'Location'
    
    def featured_badge(self, obj):
        if obj.featured:
            return format_html('<span class="badge badge-warning">Featured</span>')
        return ''
    featured_badge.short_description = 'Featured'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('county').prefetch_related('amenities')


class TenantAdmin(admin.ModelAdmin):
    """Enhanced Tenant admin"""
    list_display = ('full_name', 'email', 'phone', 'status_badge', 'property_display', 'created_at')
    list_filter = ('status', 'created_at', 'county')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'id_number')
        }),
        ('Address', {
            'fields': ('address', 'county')
        }),
        ('Status', {
            'fields': ('status', 'verified')
        }),
        ('Documents', {
            'fields': ('profile_picture', 'id_document')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'
    
    def status_badge(self, obj):
        colors = {
            'active': 'success',
            'inactive': 'secondary',
            'pending': 'warning',
            'suspended': 'danger'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(f'<span class="badge badge-{color}">{obj.status.title()}</span>')
    status_badge.short_description = 'Status'
    
    def property_display(self, obj):
        current_lease = obj.leases.filter(status='active').first()
        if current_lease and current_lease.property:
            return current_lease.property.title
        return 'No active property'
    property_display.short_description = 'Current Property'


class LandlordAdmin(admin.ModelAdmin):
    """Enhanced Landlord admin"""
    list_display = ('full_name', 'email', 'phone', 'verified_badge', 'properties_count', 'created_at')
    list_filter = ('verified', 'created_at', 'county')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'company_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'id_number')
        }),
        ('Company Information', {
            'fields': ('company_name', 'company_registration_number')
        }),
        ('Address', {
            'fields': ('address', 'county')
        }),
        ('Verification', {
            'fields': ('verified', 'verification_documents')
        }),
        ('Documents', {
            'fields': ('profile_picture', 'id_document')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        if obj.company_name:
            return f"{obj.first_name} {obj.last_name} ({obj.company_name})"
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'
    
    def verified_badge(self, obj):
        if obj.verified:
            return format_html('<span class="badge badge-success">Verified</span>')
        return format_html('<span class="badge badge-warning">Not Verified</span>')
    verified_badge.short_description = 'Verification'
    
    def properties_count(self, obj):
        count = obj.properties.count()
        return format_html(f'<span class="badge badge-info">{count} Properties</span>')
    properties_count.short_description = 'Properties'


class LeaseAdmin(admin.ModelAdmin):
    """Enhanced Lease admin"""
    list_display = ('property_display', 'tenant_display', 'landlord_display', 'status_badge', 'rent_amount', 'start_date', 'end_date')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('property__title', 'tenant__first_name', 'tenant__last_name', 'landlord__first_name', 'landlord__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Lease Details', {
            'fields': ('property', 'tenant', 'landlord', 'status')
        }),
        ('Financial Terms', {
            'fields': ('rent_amount', 'deposit_amount', 'payment_frequency')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Terms', {
            'fields': ('terms_conditions', 'notes')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def property_display(self, obj):
        return obj.property.title if obj.property else 'N/A'
    property_display.short_description = 'Property'
    
    def tenant_display(self, obj):
        return f"{obj.tenant.first_name} {obj.tenant.last_name}" if obj.tenant else 'N/A'
    tenant_display.short_description = 'Tenant'
    
    def landlord_display(self, obj):
        return f"{obj.landlord.first_name} {obj.landlord.last_name}" if obj.landlord else 'N/A'
    landlord_display.short_description = 'Landlord'
    
    def status_badge(self, obj):
        colors = {
            'active': 'success',
            'expired': 'danger',
            'terminated': 'warning',
            'pending': 'info'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(f'<span class="badge badge-{color}">{obj.status.title()}</span>')
    status_badge.short_description = 'Status'


class PaymentAdmin(admin.ModelAdmin):
    """Enhanced Payment admin"""
    list_display = ('tenant_display', 'property_display', 'amount_display', 'payment_method', 'status_badge', 'payment_date', 'due_date')
    list_filter = ('status', 'payment_method', 'payment_date', 'due_date')
    search_fields = ('tenant__first_name', 'tenant__last_name', 'property__title', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    
    def amount_display(self, obj):
        return f"KES {obj.amount:,}"
    amount_display.short_description = 'Amount'
    
    def tenant_display(self, obj):
        return f"{obj.tenant.first_name} {obj.tenant.last_name}" if obj.tenant else 'N/A'
    tenant_display.short_description = 'Tenant'
    
    def property_display(self, obj):
        return obj.property.title if obj.property else 'N/A'
    property_display.short_description = 'Property'
    
    def status_badge(self, obj):
        colors = {
            'paid': 'success',
            'pending': 'warning',
            'overdue': 'danger',
            'partial': 'info'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(f'<span class="badge badge-{color}">{obj.status.title()}</span>')
    status_badge.short_description = 'Status'


class MaintenanceRequestAdmin(admin.ModelAdmin):
    """Enhanced Maintenance Request admin"""
    list_display = ('property_display', 'tenant_display', 'title', 'priority_badge', 'status_badge', 'created_at')
    list_filter = ('priority', 'status', 'created_at')
    search_fields = ('title', 'description', 'property__title', 'tenant__first_name', 'tenant__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Request Details', {
            'fields': ('property', 'tenant', 'title', 'description')
        }),
        ('Classification', {
            'fields': ('priority', 'status', 'category')
        }),
        ('Resolution', {
            'fields': ('assigned_to', 'resolution_notes', 'completed_at')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def property_display(self, obj):
        return obj.property.title if obj.property else 'N/A'
    property_display.short_description = 'Property'
    
    def tenant_display(self, obj):
        return f"{obj.tenant.first_name} {obj.tenant.last_name}" if obj.tenant else 'N/A'
    tenant_display.short_description = 'Tenant'
    
    def priority_badge(self, obj):
        colors = {
            'high': 'danger',
            'medium': 'warning',
            'low': 'info'
        }
        color = colors.get(obj.priority, 'secondary')
        return format_html(f'<span class="badge badge-{color}">{obj.priority.title()}</span>')
    priority_badge.short_description = 'Priority'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'in_progress': 'info',
            'completed': 'success',
            'cancelled': 'secondary'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(f'<span class="badge badge-{color}">{obj.status.replace("_", " ").title()}</span>')
    status_badge.short_description = 'Status'


class MessageAdmin(admin.ModelAdmin):
    """Enhanced Message admin"""
    list_display = ('sender_display', 'recipient_display', 'subject', 'status_badge', 'created_at')
    list_filter = ('status', 'message_type', 'created_at')
    search_fields = ('subject', 'content', 'sender__first_name', 'sender__last_name', 'recipient__first_name', 'recipient__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    def sender_display(self, obj):
        if obj.sender:
            return f"{obj.sender.first_name} {obj.sender.last_name}"
        return 'System'
    sender_display.short_description = 'Sender'
    
    def recipient_display(self, obj):
        if obj.recipient:
            return f"{obj.recipient.first_name} {obj.recipient.last_name}"
        return 'All'
    recipient_display.short_description = 'Recipient'
    
    def status_badge(self, obj):
        colors = {
            'sent': 'info',
            'delivered': 'success',
            'read': 'primary',
            'failed': 'danger'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(f'<span class="badge badge-{color}">{obj.status.title()}</span>')
    status_badge.short_description = 'Status'


# Custom admin site with enhanced dashboard
class TRACAAdminSite(admin.AdminSite):
    """Custom admin site with TRACA branding and enhanced dashboard"""
    site_header = "TRACA Management Admin"
    site_title = "TRACA Management"
    index_title = "Welcome to TRACA Management Admin Panel"
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.custom_dashboard), name='dashboard'),
        ]
        return custom_urls + urls
    
    def custom_dashboard(self, request):
        """Custom dashboard with TRACA branding and enhanced statistics"""
        
        # Get statistics
        stats = {
            'total_properties': Property.objects.count(),
            'active_properties': Property.objects.filter(status='available').count(),
            'total_tenants': Tenant.objects.count(),
            'active_tenants': Tenant.objects.filter(status='active').count(),
            'total_landlords': Landlord.objects.count(),
            'verified_landlords': Landlord.objects.filter(verified=True).count(),
            'active_leases': Lease.objects.filter(status='active').count(),
            'pending_maintenance': MaintenanceRequest.objects.filter(status='pending').count(),
        }
        
        # Financial statistics
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_revenue = Payment.objects.filter(
            status='paid',
            payment_date__month=current_month,
            payment_date__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Recent activities
        recent_properties = Property.objects.order_by('-created_at')[:5]
        recent_tenants = Tenant.objects.order_by('-created_at')[:5]
        recent_maintenance = MaintenanceRequest.objects.filter(status='pending').order_by('-created_at')[:5]
        
        context = {
            **self.each_context(request),
            'title': 'TRACA Dashboard',
            'stats': stats,
            'monthly_revenue': monthly_revenue,
            'recent_properties': recent_properties,
            'recent_tenants': recent_tenants,
            'recent_maintenance': recent_maintenance,
            'current_month': calendar.month_name[current_month],
            'current_year': current_year,
        }
        
        return render(request, 'admin/dashboard.html', context)


# Register enhanced admin classes
admin.site.register(Property, PropertyAdmin)
admin.site.register(Tenant, TenantAdmin)
admin.site.register(Landlord, LandlordAdmin)
admin.site.register(Lease, LeaseAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(MaintenanceRequest, MaintenanceRequestAdmin)
admin.site.register(Message, MessageAdmin)

# Customize admin site header
admin.site.site_header = "TRACA Management Admin"
admin.site.site_title = "TRACA Management"
admin.site.index_title = "Welcome to TRACA Management Admin Panel"
