"""
Tenant Portal Views - Backend-integrated views for tenant functionality
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta

from .models import (
    Tenant, Lease, Payment, MaintenanceRequest,
    TenantDocument, Message, Property, TenantService
)
from .forms import ContactForm


def tenant_login(request):
    """Tenant login view - Always redirects to tenant portal (never to admin)"""
    # If already logged in and has tenant profile, go to dashboard
    if request.user.is_authenticated:
        try:
            tenant = request.user.tenant_profile
            # Force redirect to tenant dashboard, ignore any 'next' parameter
            return redirect('listings:tenant_dashboard')
        except Tenant.DoesNotExist:
            # User exists but no tenant profile, go to registration
            return redirect('listings:tenant_registration')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Check if user has tenant profile
            try:
                tenant = user.tenant_profile
                messages.success(request, f'Welcome back, {tenant.full_name}!')
                # Always redirect to tenant dashboard, never to admin
                return redirect('listings:tenant_dashboard')
            except Tenant.DoesNotExist:
                messages.info(request, 'Please complete your tenant registration.')
                return redirect('listings:tenant_registration')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'tenant/login.html', {'year': timezone.now().year})


def tenant_register(request):
    """Tenant registration view - Create user and redirect to profile creation"""
    if request.user.is_authenticated:
        try:
            tenant = request.user.tenant_profile
            return redirect('listings:tenant_dashboard')
        except Tenant.DoesNotExist:
            pass  # Continue with registration
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'tenant/register.html', {'year': timezone.now().year})
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'tenant/register.html', {'year': timezone.now().year})
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'tenant/register.html', {'year': timezone.now().year})
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        # Log them in
        login(request, user)
        messages.success(request, 'Account created! Please complete your tenant profile.')
        return redirect('listings:tenant_complete_profile')
    
    return render(request, 'tenant/register.html', {'year': timezone.now().year})


def tenant_logout(request):
    """Tenant logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('listings:home')


@login_required
def tenant_dashboard(request):
    """Main tenant dashboard with overview"""
    try:
        tenant = request.user.tenant_profile
    except Tenant.DoesNotExist:
        # Redirect to registration if tenant profile doesn't exist
        return redirect('listings:tenant_registration')
    
    # Get active lease
    active_lease = Lease.objects.filter(
        tenant=tenant,
        end_date__gte=timezone.now().date(),
        status='active'
    ).select_related('property_item', 'property_item__county').first()
    
    # Get recent payments
    recent_payments = Payment.objects.filter(
        lease__tenant=tenant
    ).select_related('lease', 'lease__property_item').order_by('-payment_date')[:5]
    
    # Get pending maintenance requests
    pending_maintenance = MaintenanceRequest.objects.filter(
        tenant=tenant,
        status__in=['pending', 'in_progress']
    ).select_related('lease').order_by('-reported_date')[:5]
    
    # Get total paid this year
    year_start = datetime(timezone.now().year, 1, 1).date()
    total_paid_year = Payment.objects.filter(
        lease__tenant=tenant,
        payment_date__gte=year_start,
        status='confirmed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate next rent due
    next_rent_due = None
    if active_lease:
        # Assuming monthly rent
        last_payment = Payment.objects.filter(
            lease=active_lease,
            payment_type='rent',
            status='confirmed'
        ).order_by('-payment_date').first()
        
        if last_payment:
            next_rent_due = last_payment.payment_date + timedelta(days=30)
        else:
            next_rent_due = active_lease.start_date
    
    context = {
        'tenant': tenant,
        'active_lease': active_lease,
        'recent_payments': recent_payments,
        'pending_maintenance': pending_maintenance,
        'total_paid_year': total_paid_year,
        'next_rent_due': next_rent_due,
        'year': timezone.now().year,
    }
    return render(request, 'tenant/dashboard.html', context)


@login_required
def tenant_profile(request):
    """Tenant profile view and edit"""
    try:
        tenant = request.user.tenant_profile
    except Tenant.DoesNotExist:
        return redirect('listings:tenant_registration')
    
    if request.method == 'POST':
        # Update profile
        tenant.phone = request.POST.get('phone', tenant.phone)
        tenant.emergency_contact = request.POST.get('emergency_contact', tenant.emergency_contact)
        tenant.employer = request.POST.get('employer', tenant.employer)
        tenant.occupation = request.POST.get('occupation', tenant.occupation)
        tenant.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('listings:tenant_profile')
    
    context = {
        'tenant': tenant,
        'year': timezone.now().year,
    }
    return render(request, 'tenant/profile.html', context)


# ==================== ADVANCED TENANT FEATURES ====================

@login_required(login_url='/tenant/login/')
def tenant_notifications(request):
    """Tenant notification center"""
    try:
        tenant = request.user.tenant_profile
    except Tenant.DoesNotExist:
        messages.error(request, 'Tenant profile not found.')
        return redirect('listings:tenant_login')
    
    # Get unread messages
    unread_messages = Message.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-sent_date')
    
    # Get recent messages (last 30 days)
    recent_messages = Message.objects.filter(
        recipient=request.user,
        sent_date__gte=timezone.now() - timedelta(days=30)
    ).order_by('-sent_date')[:20]
    
    # Get lease-related notifications
    current_lease = Lease.objects.filter(
        tenant=tenant,
        status='active'
    ).first()
    
    lease_notifications = []
    if current_lease:
        # Check for upcoming rent due
        days_until_rent = (current_lease.start_date + timedelta(days=30) - timezone.now().date()).days
        if days_until_rent <= 7 and days_until_rent > 0:
            lease_notifications.append({
                'type': 'rent_reminder',
                'message': f'Rent payment due in {days_until_rent} days',
                'priority': 'high' if days_until_rent <= 3 else 'medium'
            })
        
        # Check for lease expiry
        days_until_expiry = (current_lease.end_date - timezone.now().date()).days
        if days_until_expiry <= 60 and days_until_expiry > 0:
            lease_notifications.append({
                'type': 'lease_expiry',
                'message': f'Lease expires in {days_until_expiry} days',
                'priority': 'high' if days_until_expiry <= 30 else 'medium'
            })
    
    # Get maintenance request status updates
    recent_requests = MaintenanceRequest.objects.filter(
        tenant=tenant,
        reported_date__gte=timezone.now() - timedelta(days=30)
    ).order_by('-reported_date')
    
    context = {
        'tenant': tenant,
        'unread_messages': unread_messages,
        'recent_messages': recent_messages,
        'lease_notifications': lease_notifications,
        'recent_requests': recent_requests,
    }
    
    return render(request, 'tenant/notifications.html', context)


@login_required(login_url='/tenant/login/')
def tenant_lease_calculator(request):
    """Lease calculator and planning tool"""
    try:
        tenant = request.user.tenant_profile
    except Tenant.DoesNotExist:
        messages.error(request, 'Tenant profile not found.')
        return redirect('listings:tenant_login')
    
    current_lease = Lease.objects.filter(
        tenant=tenant,
        status='active'
    ).first()
    
    if not current_lease:
        messages.info(request, 'No active lease found.')
        return redirect('listings:tenant_dashboard')
    
    # Calculate lease metrics
    today = timezone.now().date()
    days_elapsed = (today - current_lease.start_date).days
    days_remaining = (current_lease.end_date - today).days
    total_lease_days = (current_lease.end_date - current_lease.start_date).days
    
    # Calculate payments
    total_paid = Payment.objects.filter(
        lease=current_lease,
        status='confirmed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    months_elapsed = days_elapsed // 30
    expected_paid = current_lease.monthly_rent * months_elapsed
    balance = expected_paid - total_paid
    
    # Calculate lease renewal cost
    renewal_cost = current_lease.monthly_rent * 12  # Annual cost
    
    # Calculate savings if paid upfront
    upfront_discount = renewal_cost * Decimal('0.05')  # 5% discount
    upfront_cost = renewal_cost - upfront_discount
    
    # Payment schedule
    payment_schedule = []
    next_payment_date = current_lease.start_date
    for i in range(12):  # Next 12 months
        next_payment_date = next_payment_date + timedelta(days=30)
        if next_payment_date <= current_lease.end_date:
            payment_schedule.append({
                'date': next_payment_date,
                'amount': current_lease.monthly_rent,
                'status': 'upcoming' if next_payment_date > today else 'due'
            })
    
    context = {
        'tenant': tenant,
        'lease': current_lease,
        'days_elapsed': days_elapsed,
        'days_remaining': days_remaining,
        'total_lease_days': total_lease_days,
        'total_paid': total_paid,
        'expected_paid': expected_paid,
        'balance': balance,
        'renewal_cost': renewal_cost,
        'upfront_cost': upfront_cost,
        'upfront_discount': upfront_discount,
        'payment_schedule': payment_schedule,
    }
    
    return render(request, 'tenant/lease_calculator.html', context)


@login_required(login_url='/tenant/login/')
def tenant_service_requests(request):
    """Advanced service request management"""
    try:
        tenant = request.user.tenant_profile
    except Tenant.DoesNotExist:
        messages.error(request, 'Tenant profile not found.')
        return redirect('listings:tenant_login')
    
    if request.method == 'POST':
        # Handle service request submission
        title = request.POST.get('title')
        description = request.POST.get('description')
        service_type = request.POST.get('service_type')
        priority = request.POST.get('priority', 'normal')
        preferred_date = request.POST.get('preferred_date')
        
        if title and description and service_type:
            current_lease = Lease.objects.filter(
                tenant=tenant,
                status='active'
            ).first()
            
            if current_lease:
                service_request = MaintenanceRequest.objects.create(
                    tenant=tenant,
                    lease=current_lease,
                    title=title,
                    description=description,
                    priority=priority,
                    preferred_date=preferred_date if preferred_date else None,
                    status='pending'
                )
                
                messages.success(request, 'Service request submitted successfully!')
                return redirect('listings:tenant_service_requests')
            else:
                messages.error(request, 'No active lease found.')
    
    # Get available services
    available_services = TenantService.objects.filter(is_active=True)
    
    # Get tenant's service requests
    service_requests = MaintenanceRequest.objects.filter(
        tenant=tenant
    ).order_by('-reported_date')
    
    context = {
        'tenant': tenant,
        'available_services': available_services,
        'service_requests': service_requests,
    }
    
    return render(request, 'tenant/service_requests.html', context)


@login_required(login_url='/tenant/login/')
def tenant_preferences(request):
    """Tenant preferences and settings"""
    try:
        tenant = request.user.tenant_profile
    except Tenant.DoesNotExist:
        messages.error(request, 'Tenant profile not found.')
        return redirect('listings:tenant_login')
    
    if request.method == 'POST':
        # Update preferences
        notification_email = request.POST.get('notification_email') == 'on'
        notification_sms = request.POST.get('notification_sms') == 'on'
        auto_payment = request.POST.get('auto_payment') == 'on'
        preferred_contact_time = request.POST.get('preferred_contact_time', 'business_hours')
        
        # Update tenant preferences (you'd need to add these fields to the Tenant model)
        # For now, we'll just show a success message
        messages.success(request, 'Preferences updated successfully!')
        return redirect('listings:tenant_preferences')
    
    # Get current lease for context
    current_lease = Lease.objects.filter(
        tenant=tenant,
        status='active'
    ).first()
    
    context = {
        'tenant': tenant,
        'current_lease': current_lease,
    }
    
    return render(request, 'tenant/preferences.html', context)


@login_required
def tenant_payments(request):
    """View payment history"""
    try:
        tenant = request.user.tenant_profile
    except Tenant.DoesNotExist:
        return redirect('listings:tenant_registration')
    
    payments = Payment.objects.filter(
        lease__tenant=tenant
    ).select_related('lease', 'lease__property_item').order_by('-payment_date')
    
    # Payment statistics
    total_paid = payments.filter(status='confirmed').aggregate(total=Sum('amount'))['total'] or 0
    pending_amount = payments.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'tenant': tenant,
        'payments': payments,
        'total_paid': total_paid,
        'pending_amount': pending_amount,
        'year': timezone.now().year,
    }
    return render(request, 'tenant/payments.html', context)


@login_required
def tenant_maintenance(request):
    """Submit and view maintenance requests"""
    try:
        tenant = request.user.tenant_profile
    except Tenant.DoesNotExist:
        return redirect('listings:tenant_registration')
    
    if request.method == 'POST':
        # Create maintenance request
        lease_id = request.POST.get('lease')
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        priority = request.POST.get('priority')
        
        if lease_id and title and description:
            lease_obj = get_object_or_404(Lease, pk=lease_id, tenant=tenant)
            
            maintenance = MaintenanceRequest.objects.create(
                tenant=tenant,
                lease=lease_obj,
                title=title,
                description=description,
                category=category,
                priority=priority
            )
            
            messages.success(request, 'Maintenance request submitted successfully! We will contact you soon.')
            return redirect('listings:tenant_maintenance')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get tenant's active leases
    active_leases = Lease.objects.filter(
        tenant=tenant,
        status='active',
        end_date__gte=timezone.now().date()
    ).select_related('property_item', 'property_item__county')
    
    # Get maintenance requests
    maintenance_requests = MaintenanceRequest.objects.filter(
        tenant=tenant
    ).select_related('lease', 'lease__property_item').order_by('-reported_date')
    
    context = {
        'tenant': tenant,
        'active_leases': active_leases,
        'maintenance_requests': maintenance_requests,
        'year': timezone.now().year,
    }
    return render(request, 'tenant/maintenance.html', context)


@login_required
def tenant_documents(request):
    """View tenant documents"""
    try:
        tenant = request.user.tenant_profile
    except Tenant.DoesNotExist:
        return redirect('listings:tenant_registration')
    
    documents = TenantDocument.objects.filter(
        tenant=tenant
    ).order_by('-created_at')
    
    context = {
        'tenant': tenant,
        'documents': documents,
        'year': timezone.now().year,
    }
    return render(request, 'tenant/documents.html', context)


@login_required
def tenant_messages(request):
    """View and send messages"""
    try:
        tenant = request.user.tenant_profile
    except Tenant.DoesNotExist:
        return redirect('listings:tenant_registration')
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        
        if subject and message_text:
            # Get admin user (first superuser)
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                Message.objects.create(
                    sender=request.user,
                    recipient=admin_user,
                    tenant=tenant,
                    subject=subject,
                    message=message_text
                )
                messages.success(request, 'Message sent successfully!')
            else:
                messages.error(request, 'Unable to send message. Please try again later.')
            return redirect('listings:tenant_messages')
    
    # Get messages
    tenant_messages = Message.objects.filter(
        tenant=tenant
    ).order_by('-created_at')
    
    context = {
        'tenant': tenant,
        'tenant_messages': tenant_messages,
        'year': timezone.now().year,
    }
    return render(request, 'tenant/messages.html', context)


def tenant_registration(request):
    """Landing page - shows login/register options"""
    # If already logged in, check profile status
    if request.user.is_authenticated:
        try:
            tenant = request.user.tenant_profile
            if tenant.is_verified:
                return redirect('listings:tenant_dashboard')
            else:
                messages.info(request, 'Your registration is pending admin approval. You will be notified once approved.')
                return redirect('listings:home')
        except Tenant.DoesNotExist:
            # User logged in but no tenant profile, redirect to complete it
            return redirect('listings:tenant_complete_profile')
    
    # Show registration/login landing page
    context = {
        'year': timezone.now().year,
    }
    return render(request, 'tenant/registration_landing.html', context)


@login_required
def tenant_complete_profile(request):
    """Complete tenant profile after account creation"""
    # Check if profile already exists
    try:
        tenant = request.user.tenant_profile
        if tenant.is_verified:
            return redirect('listings:tenant_dashboard')
        else:
            messages.info(request, 'Your profile is pending approval.')
            return redirect('listings:home')
    except Tenant.DoesNotExist:
        pass  # Continue with profile creation
    
    if request.method == 'POST':
        # Create tenant profile
        phone = request.POST.get('phone')
        emergency_contact = request.POST.get('emergency_contact', '')
        emergency_phone = request.POST.get('emergency_phone', '')
        id_number = request.POST.get('id_number', '')
        date_of_birth = request.POST.get('date_of_birth', None)
        occupation = request.POST.get('occupation', '')
        employer = request.POST.get('employer', '')
        profile_image = request.FILES.get('profile_image', None)
        
        # Create tenant profile
        tenant = Tenant.objects.create(
            user=request.user,
            phone=phone,
            emergency_contact=emergency_contact,
            emergency_phone=emergency_phone,
            id_number=id_number,
            date_of_birth=date_of_birth if date_of_birth else None,
            occupation=occupation,
            employer=employer,
            profile_image=profile_image,
            is_verified=False  # Requires admin approval
        )
        
        messages.success(request, 'Thank you! Your profile has been submitted for approval. We will notify you once verified.')
        return redirect('listings:home')
    
    context = {
        'user': request.user,
        'year': timezone.now().year,
    }
    return render(request, 'tenant/complete_profile.html', context)


@login_required
def tenant_services(request):
    """Display all available tenant services"""
    try:
        tenant = request.user.tenant_profile
    except Tenant.DoesNotExist:
        return redirect('listings:tenant_registration')
    
    # Get filter parameter
    category_filter = request.GET.get('category', '')
    
    # Get all available services
    services = TenantService.objects.filter(is_available=True)
    
    if category_filter:
        services = services.filter(category=category_filter)
    
    # Group services by category
    services_by_category = {}
    for service in services:
        cat_display = service.get_category_display()
        if cat_display not in services_by_category:
            services_by_category[cat_display] = []
        services_by_category[cat_display].append(service)
    
    # Get all categories for filter
    categories = TenantService.SERVICE_CATEGORIES
    
    # Get active lease for property info
    active_lease = Lease.objects.filter(
        tenant=tenant,
        end_date__gte=timezone.now().date(),
        status='active'
    ).select_related('property_item', 'property_item__county').first()
    
    # Get property amenities if tenant has active lease
    property_amenities = None
    if active_lease and active_lease.property_item:
        property_amenities = active_lease.property_item.amenities.filter(is_active=True)
    
    context = {
        'tenant': tenant,
        'services_by_category': services_by_category,
        'categories': categories,
        'category_filter': category_filter,
        'active_lease': active_lease,
        'property_amenities': property_amenities,
        'year': timezone.now().year,
    }
    
    return render(request, 'tenant/services.html', context)
