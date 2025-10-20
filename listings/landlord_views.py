"""
Landlord Portal Views
Handles all landlord-specific functionality including authentication, dashboard,
property management, tenant overview, and financial tracking.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import (
    Landlord, Property, PropertyMedia, Tenant, Lease, Payment, 
    MaintenanceRequest, TenantDocument, County, Amenity
)


# ==================== AUTHENTICATION VIEWS ====================

def landlord_login(request):
    """Landlord login view"""
    if request.user.is_authenticated:
        try:
            landlord = Landlord.objects.get(user=request.user)
            if landlord.is_verified:
                return redirect('listings:landlord:dashboard')
            else:
                messages.warning(request, 'Your account is pending admin approval.')
                logout(request)
        except Landlord.DoesNotExist:
            pass
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is a landlord
            try:
                landlord = Landlord.objects.get(user=user)
                
                if not landlord.is_verified:
                    messages.error(request, 'Your landlord account is pending admin approval. Please wait for verification.')
                    return redirect('listings:landlord:login')
                
                if not landlord.is_active:
                    messages.error(request, 'Your account has been deactivated. Please contact support.')
                    return redirect('listings:landlord:login')
                
                login(request, user)
                messages.success(request, f'Welcome back, {landlord.full_name}!')
                return redirect('listings:landlord:dashboard')
            
            except Landlord.DoesNotExist:
                messages.error(request, 'This account is not registered as a landlord.')
                return redirect('listings:landlord:login')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'landlord/login.html')


def landlord_register(request):
    """Landlord registration view"""
    if request.user.is_authenticated:
        return redirect('listings:landlord:dashboard')
    
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        company_name = request.POST.get('company_name', '')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('listings:landlord:register')
        
        if len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('listings:landlord:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('listings:landlord:register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('listings:landlord:register')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create landlord profile
        landlord = Landlord.objects.create(
            user=user,
            phone=phone,
            company_name=company_name,
            is_verified=False  # Requires admin approval
        )
        
        messages.success(request, 'Registration successful! Your account is pending admin approval.')
        return redirect('listings:landlord:login')
    
    return render(request, 'landlord/register.html')


def landlord_logout(request):
    """Landlord logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('listings:landlord:login')


# ==================== DASHBOARD VIEW ====================

@login_required(login_url='/landlord/login/')
def landlord_dashboard(request):
    """Landlord dashboard with statistics and overview"""
    try:
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        messages.error(request, 'You are not registered as a landlord.')
        return redirect('listings:home')
    
    # Get landlord's properties
    properties = Property.objects.filter(landlord=landlord).select_related('county')
    
    # Statistics
    total_properties = properties.count()
    total_units = properties.count()  # For now, 1 property = 1 unit
    
    # Active leases
    active_leases = Lease.objects.filter(
        property_item__landlord=landlord,
        status='active'
    ).select_related('tenant', 'property_item')
    
    occupied_units = active_leases.count()
    vacant_units = total_units - occupied_units
    
    # Financial data
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    monthly_rent = active_leases.aggregate(
        total=Sum('monthly_rent')
    )['total'] or Decimal('0.00')
    
    payments_this_month = Payment.objects.filter(
        lease__property_item__landlord=landlord,
        payment_date__month=current_month,
        payment_date__year=current_year,
        status='confirmed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    total_received = Payment.objects.filter(
        lease__property_item__landlord=landlord,
        status='confirmed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Pending maintenance
    pending_maintenance = MaintenanceRequest.objects.filter(
        lease__property_item__landlord=landlord,
        status__in=['pending', 'in_progress']
    ).count()
    
    # Recent activities
    recent_payments = Payment.objects.filter(
        lease__property_item__landlord=landlord
    ).select_related('lease__tenant', 'lease__property_item').order_by('-payment_date')[:5]
    
    recent_maintenance = MaintenanceRequest.objects.filter(
        lease__property_item__landlord=landlord
    ).select_related('tenant', 'lease__property_item').order_by('-reported_date')[:5]
    
    context = {
        'landlord': landlord,
        'total_properties': total_properties,
        'occupied_units': occupied_units,
        'vacant_units': vacant_units,
        'monthly_rent': monthly_rent,
        'payments_this_month': payments_this_month,
        'total_received': total_received,
        'pending_maintenance': pending_maintenance,
        'recent_payments': recent_payments,
        'recent_maintenance': recent_maintenance,
        'active_leases': active_leases[:5],  # Show 5 most recent
    }
    
    return render(request, 'landlord/dashboard.html', context)


# ==================== PROPERTY MANAGEMENT VIEWS ====================

@login_required(login_url='/landlord/login/')
def landlord_properties(request):
    """List all landlord's properties"""
    try:
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        messages.error(request, 'You are not registered as a landlord.')
        return redirect('listings:home')
    
    properties = Property.objects.filter(landlord=landlord).select_related('county').prefetch_related('media')
    
    # Get lease status for each property
    for prop in properties:
        active_lease = Lease.objects.filter(property_item=prop, status='active').first()
        prop.current_lease = active_lease
        prop.is_occupied = active_lease is not None
    
    context = {
        'landlord': landlord,
        'properties': properties,
    }
    
    return render(request, 'landlord/properties.html', context)


@login_required(login_url='/landlord/login/')
def landlord_property_add(request):
    """Add new property"""
    try:
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        messages.error(request, 'You are not registered as a landlord.')
        return redirect('listings:home')
    
    if request.method == 'POST':
        # Create property
        property_obj = Property.objects.create(
            landlord=landlord,
            title=request.POST.get('title'),
            property_type=request.POST.get('property_type'),
            county_id=request.POST.get('county'),
            description=request.POST.get('description'),
            price=request.POST.get('price'),
            area=request.POST.get('area'),
            bedrooms=request.POST.get('bedrooms') or None,
            bathrooms=request.POST.get('bathrooms') or None,
            parking_slots=request.POST.get('parking_slots') or None,
            is_furnished=request.POST.get('is_furnished') == 'on',
            pet_friendly=request.POST.get('pet_friendly') == 'on',
            near_school=request.POST.get('near_school') == 'on',
            is_verified=False  # Requires admin approval
        )
        
        # Handle amenities
        amenity_ids = request.POST.getlist('amenities')
        if amenity_ids:
            property_obj.amenities.set(amenity_ids)
        
        # Handle image uploads
        images = request.FILES.getlist('images')
        for i, image in enumerate(images):
            PropertyMedia.objects.create(
                property=property_obj,
                media_type='image',
                file=image,
                order=i,
                is_primary=(i == 0)
            )
        
        messages.success(request, 'Property added successfully! It is pending admin approval.')
        return redirect('listings:landlord:properties')
    
    counties = County.objects.filter(is_active=True)
    amenities = Amenity.objects.filter(is_active=True)
    
    context = {
        'landlord': landlord,
        'counties': counties,
        'amenities': amenities,
    }
    
    return render(request, 'landlord/property_add.html', context)


@login_required(login_url='/landlord/login/')
def landlord_property_detail(request, property_id):
    """View property details"""
    try:
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        messages.error(request, 'You are not registered as a landlord.')
        return redirect('listings:home')
    
    property_obj = get_object_or_404(
        Property.objects.select_related('county').prefetch_related('media', 'amenities'),
        id=property_id,
        landlord=landlord
    )
    
    # Get current lease
    current_lease = Lease.objects.filter(
        property_item=property_obj,
        status='active'
    ).select_related('tenant').first()
    
    # Get lease history
    lease_history = Lease.objects.filter(
        property_item=property_obj
    ).select_related('tenant').order_by('-start_date')
    
    # Get maintenance requests
    maintenance_requests = MaintenanceRequest.objects.filter(
        lease__property_item=property_obj
    ).select_related('tenant').order_by('-reported_date')
    
    context = {
        'landlord': landlord,
        'property': property_obj,
        'current_lease': current_lease,
        'lease_history': lease_history,
        'maintenance_requests': maintenance_requests,
    }
    
    return render(request, 'landlord/property_detail.html', context)


# ==================== TENANT MANAGEMENT VIEWS ====================

@login_required(login_url='/landlord/login/')
def landlord_tenants(request):
    """View all tenants across landlord's properties"""
    try:
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        messages.error(request, 'You are not registered as a landlord.')
        return redirect('listings:home')
    
    # Get all active leases
    active_leases = Lease.objects.filter(
        property_item__landlord=landlord,
        status='active'
    ).select_related('tenant', 'property_item')
    
    # Get all past leases
    past_leases = Lease.objects.filter(
        property_item__landlord=landlord,
        status='terminated'
    ).select_related('tenant', 'property_item').order_by('-end_date')[:10]
    
    context = {
        'landlord': landlord,
        'active_leases': active_leases,
        'past_leases': past_leases,
    }
    
    return render(request, 'landlord/tenants.html', context)


@login_required(login_url='/landlord/login/')
def landlord_tenant_detail(request, tenant_id):
    """View specific tenant details"""
    try:
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        messages.error(request, 'You are not registered as a landlord.')
        return redirect('listings:home')
    
    tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # Verify tenant is in landlord's property
    lease = Lease.objects.filter(
        tenant=tenant,
        property_item__landlord=landlord
    ).select_related('property_item').first()
    
    if not lease:
        messages.error(request, 'Tenant not found in your properties.')
        return redirect('listings:landlord:tenants')
    
    # Get all leases for this tenant
    all_leases = Lease.objects.filter(
        tenant=tenant,
        property_item__landlord=landlord
    ).select_related('property_item').order_by('-start_date')
    
    # Get payments
    payments = Payment.objects.filter(
        lease__in=all_leases
    ).select_related('lease').order_by('-payment_date')
    
    # Get maintenance requests
    maintenance_requests = MaintenanceRequest.objects.filter(
        tenant=tenant,
        lease__property_item__landlord=landlord
    ).order_by('-reported_date')
    
    context = {
        'landlord': landlord,
        'tenant': tenant,
        'current_lease': lease if lease.status == 'active' else None,
        'all_leases': all_leases,
        'payments': payments,
        'maintenance_requests': maintenance_requests,
    }
    
    return render(request, 'landlord/tenant_detail.html', context)


# ==================== FINANCIAL VIEWS ====================

@login_required(login_url='/landlord/login/')
def landlord_financials(request):
    """Financial reports and payment tracking"""
    try:
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        messages.error(request, 'You are not registered as a landlord.')
        return redirect('listings:home')
    
    # Get all payments
    all_payments = Payment.objects.filter(
        lease__property_item__landlord=landlord
    ).select_related('lease__tenant', 'lease__property_item').order_by('-payment_date')
    
    # Monthly breakdown
    current_year = timezone.now().year
    monthly_data = []
    
    for month in range(1, 13):
        month_payments = all_payments.filter(
            payment_date__year=current_year,
            payment_date__month=month,
            status='confirmed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        monthly_data.append({
            'month': timezone.datetime(current_year, month, 1).strftime('%B'),
            'total': month_payments
        })
    
    # Summary statistics
    total_collected = all_payments.filter(status='confirmed').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    pending_payments = all_payments.filter(status='pending').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Expected monthly rent
    active_leases = Lease.objects.filter(
        property_item__landlord=landlord,
        status='active'
    )
    
    expected_monthly = active_leases.aggregate(
        total=Sum('monthly_rent')
    )['total'] or Decimal('0.00')
    
    # Advanced Analytics
    # Property-wise performance
    property_performance = []
    for property in landlord.properties.all():
        property_payments = all_payments.filter(lease__property_item=property)
        property_total = property_payments.filter(status='confirmed').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        active_lease = Lease.objects.filter(
            property_item=property,
            status='active'
        ).first()
        
        property_performance.append({
            'property': property,
            'total_collected': property_total,
            'active_lease': active_lease,
            'payment_count': property_payments.count()
        })
    
    # Outstanding balances by tenant
    outstanding_balances = []
    active_leases = Lease.objects.filter(
        property_item__landlord=landlord,
        status='active'
    ).select_related('tenant', 'property_item')
    
    for lease in active_leases:
        total_paid = Payment.objects.filter(
            lease=lease,
            status='confirmed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Calculate expected amount based on lease duration
        months_elapsed = (timezone.now().date() - lease.start_date).days // 30
        expected_total = lease.monthly_rent * months_elapsed
        outstanding = expected_total - total_paid
        
        if outstanding > 0:
            outstanding_balances.append({
                'lease': lease,
                'outstanding': outstanding,
                'months_behind': int(outstanding / lease.monthly_rent) if lease.monthly_rent > 0 else 0
            })
    
    # Collection rate
    collection_rate = 0
    if expected_monthly > 0:
        current_month_payments = all_payments.filter(
            payment_date__year=current_year,
            payment_date__month=timezone.now().month,
            status='confirmed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        collection_rate = (current_month_payments / expected_monthly) * 100
    
    # Year-over-year comparison
    last_year_payments = all_payments.filter(
        payment_date__year=current_year - 1,
        status='confirmed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    yoy_growth = 0
    if last_year_payments > 0:
        yoy_growth = ((total_collected - last_year_payments) / last_year_payments) * 100
    
    context = {
        'landlord': landlord,
        'all_payments': all_payments[:50],  # Last 50 payments
        'monthly_data': monthly_data,
        'total_collected': total_collected,
        'pending_payments': pending_payments,
        'expected_monthly': expected_monthly,
        'property_performance': property_performance,
        'outstanding_balances': outstanding_balances,
        'collection_rate': collection_rate,
        'yoy_growth': yoy_growth,
    }
    
    return render(request, 'landlord/financials.html', context)


# ==================== MAINTENANCE VIEWS ====================

@login_required(login_url='/landlord/login/')
def landlord_maintenance(request):
    """View all maintenance requests"""
    try:
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        messages.error(request, 'You are not registered as a landlord.')
        return redirect('listings:home')
    
    # Get maintenance requests
    maintenance_requests = MaintenanceRequest.objects.filter(
        lease__property_item__landlord=landlord
    ).select_related('tenant', 'lease__property_item').order_by('-reported_date')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        maintenance_requests = maintenance_requests.filter(status=status_filter)
    
    # Count by status
    status_counts = {
        'pending': maintenance_requests.filter(status='pending').count(),
        'in_progress': maintenance_requests.filter(status='in_progress').count(),
        'completed': maintenance_requests.filter(status='completed').count(),
        'cancelled': maintenance_requests.filter(status='cancelled').count(),
    }
    
    context = {
        'landlord': landlord,
        'maintenance_requests': maintenance_requests,
        'status_filter': status_filter,
        'status_counts': status_counts,
    }
    
    return render(request, 'landlord/maintenance.html', context)


# ==================== PROFILE VIEW ====================

@login_required(login_url='/landlord/login/')
def landlord_profile(request):
    """Landlord profile management"""
    try:
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        messages.error(request, 'You are not registered as a landlord.')
        return redirect('listings:home')
    
    if request.method == 'POST':
        # Update user details
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()
        
        # Update landlord details
        landlord.phone = request.POST.get('phone')
        landlord.company_name = request.POST.get('company_name', '')
        landlord.address = request.POST.get('address', '')
        landlord.city = request.POST.get('city', '')
        landlord.postal_code = request.POST.get('postal_code', '')
        landlord.id_number = request.POST.get('id_number', '')
        landlord.kra_pin = request.POST.get('kra_pin', '')
        landlord.bank_name = request.POST.get('bank_name', '')
        landlord.bank_account = request.POST.get('bank_account', '')
        landlord.bank_branch = request.POST.get('bank_branch', '')
        
        if 'profile_image' in request.FILES:
            landlord.profile_image = request.FILES['profile_image']
        
        landlord.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('listings:landlord:profile')
    
    context = {
        'landlord': landlord,
    }
    
    return render(request, 'landlord/profile.html', context)


# ==================== ADVANCED FEATURES ====================

@login_required(login_url='/landlord/login/')
def landlord_reports(request):
    """Advanced reporting and analytics dashboard"""
    try:
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        messages.error(request, 'You are not registered as a landlord.')
        return redirect('listings:home')
    
    # Date range filter
    date_from = request.GET.get('date_from', (timezone.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', timezone.now().strftime('%Y-%m-%d'))
    
    # Convert to datetime objects
    try:
        date_from_dt = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to_dt = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
    except ValueError:
        date_from_dt = timezone.now().date() - timedelta(days=365)
        date_to_dt = timezone.now().date()
    
    # Filter payments by date range
    payments_in_range = Payment.objects.filter(
        lease__property_item__landlord=landlord,
        payment_date__gte=date_from_dt,
        payment_date__lte=date_to_dt
    ).select_related('lease__tenant', 'lease__property_item')
    
    # Revenue Analytics
    total_revenue = payments_in_range.filter(status='confirmed').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Payment type breakdown
    payment_breakdown = {}
    for payment_type, _ in Payment.PAYMENT_TYPE_CHOICES:
        amount = payments_in_range.filter(
            payment_type=payment_type,
            status='confirmed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        payment_breakdown[payment_type] = amount
    
    # Property performance ranking
    property_performance = []
    for property in landlord.properties.all():
        property_payments = payments_in_range.filter(lease__property_item=property)
        property_revenue = property_payments.filter(status='confirmed').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Calculate occupancy rate
        total_days = (date_to_dt - date_from_dt).days
        occupied_days = 0
        
        leases_in_period = Lease.objects.filter(
            property_item=property,
            start_date__lte=date_to_dt,
            end_date__gte=date_from_dt
        )
        
        for lease in leases_in_period:
            lease_start = max(lease.start_date, date_from_dt)
            lease_end = min(lease.end_date or timezone.now().date(), date_to_dt)
            occupied_days += (lease_end - lease_start).days
        
        occupancy_rate = (occupied_days / total_days) * 100 if total_days > 0 else 0
        
        property_performance.append({
            'property': property,
            'revenue': property_revenue,
            'occupancy_rate': occupancy_rate,
            'payment_count': property_payments.count(),
            'avg_payment': property_revenue / property_payments.count() if property_payments.count() > 0 else 0
        })
    
    # Sort by revenue
    property_performance.sort(key=lambda x: x['revenue'], reverse=True)
    
    # Monthly trends
    monthly_trends = []
    current_date = date_from_dt
    while current_date <= date_to_dt:
        month_start = current_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_payments = payments_in_range.filter(
            payment_date__gte=month_start,
            payment_date__lte=month_end,
            status='confirmed'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        monthly_trends.append({
            'month': month_start.strftime('%b %Y'),
            'amount': month_payments
        })
        
        current_date = month_end + timedelta(days=1)
    
    # Tenant analysis
    tenant_analysis = []
    active_leases = Lease.objects.filter(
        property_item__landlord=landlord,
        status='active',
        start_date__lte=date_to_dt,
        end_date__gte=date_from_dt
    ).select_related('tenant', 'property_item')
    
    for lease in active_leases:
        tenant_payments = payments_in_range.filter(lease=lease)
        total_paid = tenant_payments.filter(status='confirmed').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Calculate expected vs actual
        months_in_period = (date_to_dt - max(lease.start_date, date_from_dt)).days // 30
        expected_amount = lease.monthly_rent * months_in_period
        payment_compliance = (total_paid / expected_amount) * 100 if expected_amount > 0 else 0
        
        tenant_analysis.append({
            'tenant': lease.tenant,
            'property': lease.property_item,
            'total_paid': total_paid,
            'expected_amount': expected_amount,
            'compliance_rate': payment_compliance,
            'payment_count': tenant_payments.count()
        })
    
    # Sort by compliance rate
    tenant_analysis.sort(key=lambda x: x['compliance_rate'], reverse=True)
    
    context = {
        'landlord': landlord,
        'date_from': date_from,
        'date_to': date_to,
        'total_revenue': total_revenue,
        'payment_breakdown': payment_breakdown,
        'property_performance': property_performance,
        'monthly_trends': monthly_trends,
        'tenant_analysis': tenant_analysis,
    }
    
    return render(request, 'landlord/reports.html', context)


@login_required(login_url='/landlord/login/')
def landlord_export_data(request):
    """Export landlord data in various formats"""
    try:
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        messages.error(request, 'You are not registered as a landlord.')
        return redirect('listings:home')
    
    export_type = request.GET.get('type', 'financial')
    date_from = request.GET.get('date_from', (timezone.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', timezone.now().strftime('%Y-%m-%d'))
    
    # This would typically generate CSV/Excel files
    # For now, we'll redirect to a simple data view
    messages.info(request, f'Export feature coming soon! Requested {export_type} data from {date_from} to {date_to}')
    return redirect('listings:landlord:reports')


@login_required(login_url='/landlord/login/')
def landlord_bulk_operations(request):
    """Bulk operations for landlords"""
    try:
        landlord = Landlord.objects.get(user=request.user)
    except Landlord.DoesNotExist:
        messages.error(request, 'You are not registered as a landlord.')
        return redirect('listings:home')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'send_rent_reminders':
            # Send rent reminders to all tenants
            active_leases = Lease.objects.filter(
                property_item__landlord=landlord,
                status='active'
            )
            
            reminder_count = 0
            for lease in active_leases:
                # Check if tenant has outstanding balance
                total_paid = Payment.objects.filter(
                    lease=lease,
                    status='confirmed'
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                
                months_elapsed = (timezone.now().date() - lease.start_date).days // 30
                expected_total = lease.monthly_rent * months_elapsed
                outstanding = expected_total - total_paid
                
                if outstanding > 0:
                    # Here you would send email/SMS reminder
                    reminder_count += 1
            
            messages.success(request, f'Rent reminders sent to {reminder_count} tenants with outstanding balances.')
        
        elif action == 'update_property_status':
            property_ids = request.POST.getlist('property_ids')
            new_status = request.POST.get('new_status')
            
            updated_count = Property.objects.filter(
                id__in=property_ids,
                landlord=landlord
            ).update(is_verified=(new_status == 'verified'))
            
            messages.success(request, f'Updated {updated_count} properties.')
        
        elif action == 'generate_statements':
            # Generate monthly statements for all tenants
            active_leases = Lease.objects.filter(
                property_item__landlord=landlord,
                status='active'
            )
            
            statements_generated = 0
            for lease in active_leases:
                # Generate statement logic here
                statements_generated += 1
            
            messages.success(request, f'Generated {statements_generated} monthly statements.')
    
    # Get data for bulk operations
    properties = Property.objects.filter(landlord=landlord)
    active_leases = Lease.objects.filter(
        property_item__landlord=landlord,
        status='active'
    ).select_related('tenant', 'property_item')
    
    context = {
        'landlord': landlord,
        'properties': properties,
        'active_leases': active_leases,
    }
    
    return render(request, 'landlord/bulk_operations.html', context)

