from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.db.models import Q, Count, Avg, Sum
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie

from .models import Property, County, Agent, Amenity, Testimonial, Inquiry, ManagementRequest, PropertyMedia, PropertyViewing, TeamMember
from .forms import PropertyForm, InquiryForm, ContactForm, PropertySearchForm, ManagementRequestForm, PropertyViewingForm
from .notifications import NotificationService
from datetime import date, timedelta


def home(request):
    """Enhanced homepage with featured properties and testimonials - optimized for performance"""
    # Cache featured properties for 30 minutes
    cache_key = 'featured_properties_home'
    featured_properties = cache.get(cache_key)
    
    if featured_properties is None:
        # Get featured properties (sale and rent) - show up to 12
        featured_properties = Property.objects.filter(
            property_type__in=['sale', 'rent'],
            is_verified=True,
            status='available'
        ).select_related('county').prefetch_related('media').order_by('-created_at')[:12]
        
        # Cache for 30 minutes (1800 seconds)
        cache.set(cache_key, featured_properties, 1800)
    
    # Cache featured testimonials for 1 hour
    testimonials_cache_key = 'featured_testimonials_home'
    featured_testimonials = cache.get(testimonials_cache_key)
    
    if featured_testimonials is None:
        # Get featured testimonials
        featured_testimonials = Testimonial.objects.filter(
            is_featured=True, 
            is_approved=True
        ).select_related('property').order_by('-created_at')[:3]
        
        # Cache for 1 hour (3600 seconds)
        cache.set(testimonials_cache_key, featured_testimonials, 3600)
    
    # Get statistics (cache for 15 minutes)
    stats_cache_key = 'property_stats_home'
    stats = cache.get(stats_cache_key)
    
    if stats is None:
        stats = {
            'total_properties': Property.objects.filter(property_type__in=['sale', 'rent']).count(),
            'available_properties': Property.objects.filter(
                property_type__in=['sale', 'rent'],
                status='available'
            ).count(),
            'counties_covered': County.objects.filter(
                properties__property_type__in=['sale', 'rent']
            ).distinct().count(),
            'verified_properties': Property.objects.filter(
                property_type__in=['sale', 'rent'],
                is_verified=True
            ).count(),
        }
        cache.set(stats_cache_key, stats, 900)  # 15 minutes
    
    context = {
        'featured_properties': featured_properties,
        'featured_testimonials': featured_testimonials,
        'stats': stats,
        'year': timezone.now().year,
    }
    
    # Use enhanced template if available, fallback to original
    template_name = 'listings/home_enhanced.html' if hasattr(request, 'is_enhanced') else 'listings/home.html'
    return render(request, template_name, context)


def properties_list(request):
    """Enhanced property listings page with advanced filters, pagination, and performance optimizations"""
    # Initialize search form
    search_form = PropertySearchForm(request.GET)
    
    # Build base queryset with optimizations
    properties = Property.objects.filter(
        property_type__in=['sale', 'rent'],
        status='available'
    ).select_related('county').prefetch_related('media', 'amenities')
    
    # Apply filters with enhanced logic
    apply_filters(request, properties)
    
    # Sorting options
    sort_by = request.GET.get('sort', '-created_at')
    valid_sort_options = {
        '-created_at': 'Newest First',
        'created_at': 'Oldest First',
        '-price': 'Price: High to Low',
        'price': 'Price: Low to High',
        'title': 'Alphabetical',
        '-view_count': 'Most Viewed',
    }
    
    if sort_by in valid_sort_options:
        properties = properties.order_by(sort_by)
    
    # Enhanced pagination with better performance
    paginator = Paginator(properties, 12)  # 12 properties per page
    page = request.GET.get('page', 1)
    
    try:
        properties_page = paginator.page(page)
    except PageNotAnInteger:
        properties_page = paginator.page(1)
    except EmptyPage:
        properties_page = paginator.page(paginator.num_pages)
    
    # Get filter counts for sidebar
    filter_counts = get_filter_counts(properties)
    
    context = {
        'properties': properties_page,
        'search_form': search_form,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': properties_page,
        'sort_options': valid_sort_options,
        'current_sort': sort_by,
        'filter_counts': filter_counts,
        'year': timezone.now().year,
    }
    
    # Use enhanced template if available
    template_name = 'listings/properties_list_enhanced.html'
    return render(request, template_name, context)


def apply_filters(request, queryset):
    """Apply filters to property queryset with enhanced logic"""
    # County filter (text input with autocomplete support)
    county = request.GET.get('county')
    if county:
        queryset = queryset.filter(county__name__icontains=county)
    
    # Town/Area filter
    town = request.GET.get('town')
    if town:
        queryset = queryset.filter(town__icontains=town)
    
    # Property type filter
    property_type = request.GET.get('property_type')
    if property_type:
        queryset = queryset.filter(property_type=property_type)
    
    # Category filter (new field)
    category = request.GET.get('category')
    if category:
        queryset = queryset.filter(category=category)
    
    # Price range filters with better handling
    min_price = request.GET.get('min_price')
    if min_price and min_price.isdigit():
        queryset = queryset.filter(price__gte=int(min_price))
    
    max_price = request.GET.get('max_price')
    if max_price and max_price.isdigit():
        queryset = queryset.filter(price__lte=int(max_price))
    
    # Price range preset
    price_range = request.GET.get('price_range')
    if price_range:
        if price_range == '0-500000':
            queryset = queryset.filter(price__lte=500000)
        elif price_range == '500000-1000000':
            queryset = queryset.filter(price__gte=500000, price__lte=1000000)
        elif price_range == '1000000-5000000':
            queryset = queryset.filter(price__gte=1000000, price__lte=5000000)
        elif price_range == '5000000-10000000':
            queryset = queryset.filter(price__gte=5000000, price__lte=10000000)
        elif price_range == '10000000+':
            queryset = queryset.filter(price__gte=10000000)
    
    # Room filters
    bedrooms = request.GET.get('bedrooms')
    if bedrooms and bedrooms.isdigit():
        queryset = queryset.filter(bedrooms__gte=int(bedrooms))
    
    bathrooms = request.GET.get('bathrooms')
    if bathrooms and bathrooms.isdigit():
        queryset = queryset.filter(bathrooms__gte=int(bathrooms))
    
    # Parking filter
    parking = request.GET.get('parking')
    if parking and parking.isdigit():
        queryset = queryset.filter(parking_slots__gte=int(parking))
    
    # Status filter
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)
    
    # Verified filter
    verified = request.GET.get('verified')
    if verified == 'true':
        queryset = queryset.filter(is_verified=True)
    
    # Distance filter (if implemented with geolocation)
    distance = request.GET.get('distance')
    if distance:
        # This would require geolocation implementation
        pass
    
    return queryset


def get_filter_counts(queryset):
    """Get counts for each filter option - cached for performance"""
    cache_key = f'filter_counts_{hash(str(queryset.query))}'
    counts = cache.get(cache_key)
    
    if counts is None:
        counts = {
            'counties': County.objects.filter(
                properties__in=queryset
            ).annotate(count=Count('properties')).order_by('-count')[:10],
            'price_ranges': {
                'under_500k': queryset.filter(price__lte=500000).count(),
                '500k_1m': queryset.filter(price__gt=500000, price__lte=1000000).count(),
                '1m_5m': queryset.filter(price__gt=1000000, price__lte=5000000).count(),
                '5m_10m': queryset.filter(price__gt=5000000, price__lte=10000000).count(),
                'over_10m': queryset.filter(price__gt=10000000).count(),
            },
            'bedroom_counts': {
                '1_plus': queryset.filter(bedrooms__gte=1).count(),
                '2_plus': queryset.filter(bedrooms__gte=2).count(),
                '3_plus': queryset.filter(bedrooms__gte=3).count(),
                '4_plus': queryset.filter(bedrooms__gte=4).count(),
                '5_plus': queryset.filter(bedrooms__gte=5).count(),
            }
        }
        cache.set(cache_key, counts, 600)  # Cache for 10 minutes
    
    return counts


def property_detail(request, pk):
    """Enhanced property detail page with performance optimizations"""
    # Cache property lookup for 15 minutes
    cache_key = f'property_detail_{pk}'
    property = cache.get(cache_key)
    
    if property is None:
        property = get_object_or_404(
            Property.objects.select_related('county').prefetch_related(
                'media', 'amenities', 'inquiries'
            ),
            pk=pk, property_type__in=['sale', 'rent']
        )
        cache.set(cache_key, property, 900)  # 15 minutes
    
    # Increment view count (with optimization)
    increment_view_count(property)
    
    # Get similar properties (cache for 30 minutes)
    similar_cache_key = f'similar_properties_{pk}'
    similar_properties = cache.get(similar_cache_key)
    
    if similar_properties is None:
        similar_properties = Property.objects.filter(
            property_type__in=['sale', 'rent'],
            county=property.county,
            status='available'
        ).exclude(pk=pk).select_related('county').prefetch_related('media')[:6]
        
        cache.set(similar_cache_key, similar_properties, 1800)  # 30 minutes
    
    context = {
        'property': property,
        'similar_properties': similar_properties,
        'inquiry_form': InquiryForm(),
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/property_detail.html', context)


def increment_view_count(property):
    """Optimized view count increment"""
    # Use cache to avoid frequent database writes
    cache_key = f'property_views_{property.id}'
    views = cache.get(cache_key, 0)
    
    if views >= 10:  # Write to database every 10 views
        property.view_count = F('view_count') + views
        property.save(update_fields=['view_count'])
        cache.set(cache_key, 0, 3600)  # Reset counter
    else:
        cache.set(cache_key, views + 1, 3600)  # Increment counter


@require_http_methods(["GET"])
def property_search_api(request):
    """AJAX API for property search with performance optimizations"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Cache search results for 5 minutes
    cache_key = f'search_suggestions_{hash(query)}'
    suggestions = cache.get(cache_key)
    
    if suggestions is None:
        properties = Property.objects.filter(
            title__icontains=query,
            property_type__in=['sale', 'rent'],
            status='available'
        ).select_related('county').only('title', 'county__name', 'price', 'pk')[:10]
        
        suggestions = [
            {
                'id': prop.id,
                'title': prop.title,
                'county': prop.county.name,
                'price': prop.price,
                'url': f'/property/{prop.id}/'
            }
            for prop in properties
        ]
        
        cache.set(cache_key, suggestions, 300)  # 5 minutes
    
    return JsonResponse({'suggestions': suggestions})


@cache_page(3600)  # Cache for 1 hour
@vary_on_headers('User-Agent')
def counties_api(request):
    """API endpoint for counties with caching"""
    counties = County.objects.filter(
        properties__property_type__in=['sale', 'rent']
    ).annotate(
        property_count=Count('properties')
    ).order_by('name').values('id', 'name', 'property_count')
    
    return JsonResponse({'counties': list(counties)})


@require_http_methods(["POST"])
def property_inquiry(request, pk):
    """Handle property inquiry with enhanced validation and notifications"""
    property = get_object_or_404(Property, pk=pk)
    
    form = InquiryForm(request.POST)
    if form.is_valid():
        inquiry = form.save(commit=False)
        inquiry.property = property
        inquiry.save()
        
        # Send notifications asynchronously
        try:
            NotificationService.send_property_inquiry_notification(inquiry)
            messages.success(request, 'Your inquiry has been sent successfully!')
        except Exception as e:
            messages.warning(request, 'Inquiry sent, but notification failed. We will contact you soon.')
        
        return redirect('listings:property_detail', pk=pk)
    else:
        messages.error(request, 'Please correct the errors below.')
    
    # Get similar properties
    similar_properties = Property.objects.filter(
        property_type__in=['sale', 'rent'],
        county=property.county,
        status='available'
    ).exclude(pk=pk)[:6]
    
    context = {
        'property': property,
        'similar_properties': similar_properties,
        'inquiry_form': form,
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/property_detail.html', context)


def contact(request):
    """Enhanced contact page with better performance"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save inquiry
            inquiry = form.save()
            
            # Send notification
            try:
                NotificationService.send_contact_notification(inquiry)
                messages.success(request, 'Your message has been sent successfully!')
            except Exception as e:
                messages.warning(request, 'Message sent, but we had trouble sending notifications.')
            
            return redirect('listings:contact')
    else:
        form = ContactForm()
    
    # Get team members (cache for 1 hour)
    team_cache_key = 'team_members_contact'
    team_members = cache.get(team_cache_key)
    
    if team_members is None:
        team_members = TeamMember.objects.filter(is_active=True).order_by('order')
        cache.set(team_cache_key, team_members, 3600)
    
    context = {
        'form': form,
        'team_members': team_members,
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/contact.html', context)


def about(request):
    """Enhanced about page with cached testimonials"""
    # Get all approved testimonials (cache for 2 hours)
    testimonials_cache_key = 'all_testimonials_about'
    testimonials = cache.get(testimonials_cache_key)
    
    if testimonials is None:
        testimonials = Testimonial.objects.filter(
            is_approved=True
        ).select_related('property').order_by('-created_at')
        cache.set(testimonials_cache_key, testimonials, 7200)  # 2 hours
    
    # Get team members (reuse cache)
    team_cache_key = 'team_members_contact'
    team_members = cache.get(team_cache_key)
    
    if team_members is None:
        team_members = TeamMember.objects.filter(is_active=True).order_by('order')
        cache.set(team_cache_key, team_members, 3600)
    
    context = {
        'testimonials': testimonials,
        'team_members': team_members,
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/about.html', context)


def services(request):
    """Services page with enhanced content"""
    context = {
        'year': timezone.now().year,
    }
    return render(request, 'listings/services.html', context)


@require_http_methods(["GET", "POST"])
def management_request(request):
    """Enhanced property management request form"""
    if request.method == 'POST':
        form = ManagementRequestForm(request.POST, request.FILES)
        if form.is_valid():
            management_request = form.save()
            
            # Send notifications
            try:
                NotificationService.send_management_request_notification(management_request)
                messages.success(request, 'Your property management request has been submitted successfully!')
            except Exception as e:
                messages.warning(request, 'Request submitted, but we had trouble sending notifications.')
            
            return redirect('listings:management_request_success')
    else:
        form = ManagementRequestForm()
    
    context = {
        'form': form,
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/management_request.html', context)


def management_request_success(request):
    """Success page for management requests"""
    return render(request, 'listings/management_requests_list.html', {
        'year': timezone.now().year,
    })


@require_http_methods(["GET", "POST"])
def book_viewing(request, property_id):
    """Enhanced property viewing booking with better validation"""
    property = get_object_or_404(Property, pk=property_id)
    
    if request.method == 'POST':
        form = PropertyViewingForm(request.POST)
        if form.is_valid():
            viewing = form.save(commit=False)
            viewing.property = property
            viewing.save()
            
            # Send confirmation
            try:
                NotificationService.send_viewing_confirmation(viewing)
                messages.success(request, 'Your viewing has been booked successfully!')
            except Exception as e:
                messages.warning(request, 'Viewing booked, but we had trouble sending confirmation.')
            
            return redirect('listings:viewing_confirmation', viewing_id=viewing.id)
    else:
        form = PropertyViewingForm(initial={'property': property})
    
    context = {
        'form': form,
        'property': property,
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/book_viewing.html', context)


def viewing_confirmation(request, viewing_id):
    """Viewing confirmation page"""
    viewing = get_object_or_404(PropertyViewing, pk=viewing_id)
    
    context = {
        'viewing': viewing,
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/viewing_confirmation.html', context)


@staff_member_required
def management_requests_list(request):
    """Admin view for management requests"""
    requests = ManagementRequest.objects.all().order_by('-created_at')
    
    context = {
        'requests': requests,
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/management_requests_list.html', context)


# Enhanced error handlers
def custom_404(request, exception):
    """Custom 404 page with property suggestions"""
    # Get some featured properties to show
    featured_properties = Property.objects.filter(
        property_type__in=['sale', 'rent'],
        is_verified=True,
        status='available'
    ).select_related('county').prefetch_related('media')[:6]
    
    context = {
        'featured_properties': featured_properties,
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/404.html', context, status=404)


def custom_500(request):
    """Custom 500 page"""
    context = {
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/500.html', context, status=500)


# Performance monitoring middleware helper
def get_performance_stats():
    """Get basic performance statistics for monitoring"""
    cache_stats = {
        'featured_properties_cache': cache.get('featured_properties_home') is not None,
        'testimonials_cache': cache.get('featured_testimonials_home') is not None,
        'stats_cache': cache.get('property_stats_home') is not None,
    }
    
    return cache_stats
