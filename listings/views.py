from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import mail_admins
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required

from .models import Property, County, Agent, Amenity, Testimonial, Inquiry, ManagementRequest, PropertyMedia
from .forms import PropertyForm, InquiryForm, ContactForm, PropertySearchForm, ManagementRequestForm


def home(request):
    """Homepage with featured properties, testimonials, and counties"""
    # Get featured properties (sale and rent)
    featured_properties = Property.objects.filter(
        property_type__in=['sale', 'rent']
    ).select_related('county').prefetch_related('media')[:6]
    
    # Get featured testimonials
    featured_testimonials = Testimonial.objects.filter(
        is_featured=True, 
        is_approved=True
    ).select_related('property')[:3]
    
    # Get active counties with property counts
    counties = County.objects.filter(is_active=True).annotate(
        property_count=Count('properties')
    ).order_by('name')
    
    context = {
        'featured_properties': featured_properties,
        'featured_testimonials': featured_testimonials,
        'counties': counties,
        'year': timezone.now().year,
    }
    return render(request, 'listings/home.html', context)


def properties_list(request):
    """Enhanced property listings page with advanced filters and professional features"""
    # Initialize search form
    search_form = PropertySearchForm(request.GET)
    
    # Start with base queryset - only sale and rent properties
    properties = Property.objects.filter(
        property_type__in=['sale', 'rent']
    ).select_related('county').prefetch_related('media')
    
    # Apply filters if form is valid
    if search_form.is_valid():
        # Keyword search (title and description)
        keyword = search_form.cleaned_data.get('keyword')
        if keyword:
            properties = properties.filter(
                Q(title__icontains=keyword) | 
                Q(description__icontains=keyword) |
                Q(county__name__icontains=keyword)
            )
        
        # County filter
        county = search_form.cleaned_data.get('county')
        if county:
            properties = properties.filter(county=county)
        
        # Property type filter
        property_type = search_form.cleaned_data.get('property_type')
        if property_type:
            properties = properties.filter(property_type=property_type)
        
        # Price range filters
        min_price = search_form.cleaned_data.get('min_price')
        if min_price:
            properties = properties.filter(price__gte=min_price)
        
        max_price = search_form.cleaned_data.get('max_price')
        if max_price:
            properties = properties.filter(price__lte=max_price)
        
        # Room filters
        bedrooms = search_form.cleaned_data.get('bedrooms')
        if bedrooms is not None:
            properties = properties.filter(bedrooms__gte=bedrooms)
        
        bathrooms = search_form.cleaned_data.get('bathrooms')
        if bathrooms is not None:
            properties = properties.filter(bathrooms__gte=bathrooms)
        
        parking_slots = search_form.cleaned_data.get('parking_slots')
        if parking_slots is not None:
            properties = properties.filter(parking_slots__gte=parking_slots)
        
        # Boolean filters
        is_furnished = search_form.cleaned_data.get('is_furnished')
        if is_furnished:
            properties = properties.filter(is_furnished=True)
        
        pet_friendly = search_form.cleaned_data.get('pet_friendly')
        if pet_friendly:
            properties = properties.filter(pet_friendly=True)
    
    # Advanced sorting options
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        properties = properties.order_by('price')
    elif sort_by == 'price_high':
        properties = properties.order_by('-price')
    elif sort_by == 'verified':
        properties = properties.order_by('-is_verified', '-created_at')
    elif sort_by == 'bedrooms':
        properties = properties.order_by('-bedrooms', '-created_at')
    else:  # newest (default)
        properties = properties.order_by('-is_verified', '-created_at')
    
    # Get total count before pagination
    total_results = properties.count()
    
    # Pagination
    paginator = Paginator(properties, 12)  # 12 properties per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options for form
    counties = County.objects.filter(is_active=True).order_by('name')
    property_types = Property.PROPERTY_TYPES
    
    # Get property statistics for display
    stats = {
        'total_properties': total_results,
        'sale_properties': properties.filter(property_type='sale').count(),
        'rent_properties': properties.filter(property_type='rent').count(),
        'verified_properties': properties.filter(is_verified=True).count(),
    }
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'counties': counties,
        'property_types': property_types,
        'total_results': total_results,
        'stats': stats,
        'current_sort': sort_by,
        'year': timezone.now().year,
    }
    return render(request, 'listings/properties_list.html', context)


def property_detail(request, pk):
    """Enhanced property detail view with professional features"""
    property_obj = get_object_or_404(
        Property.objects.select_related('county').prefetch_related('media'),
        pk=pk
    )
    
    # Handle inquiry form submission
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.property = property_obj
            inquiry.save()
            
            # Send email notification to admins
            try:
                mail_admins(
                    subject=f"New Inquiry for {property_obj.title}",
                    message=f"""
                    New inquiry received:
                    
                    Property: {property_obj.title}
                    From: {inquiry.name} ({inquiry.email})
                    Phone: {inquiry.phone}
                    Type: {inquiry.get_inquiry_type_display()}
                    
                    Message:
                    {inquiry.message}
                    """,
                    fail_silently=True
                )
            except Exception:
                pass  # Don't fail if email sending fails
            
            messages.success(request, 'Thank you for your inquiry! We will contact you soon.')
            return redirect('listings:property_detail', pk=pk)
    else:
        form = InquiryForm()
    
    # Get related properties (same county, different property)
    related_properties = Property.objects.filter(
        county=property_obj.county,
        property_type__in=['sale', 'rent']
    ).exclude(pk=pk).select_related('county').prefetch_related('media')[:4]
    
    # Get property images for gallery
    property_images = property_obj.media.filter(media_type='image').order_by('order', 'created_at')
    main_image = property_images.first() if property_images.exists() else None
    
    # Calculate property features
    property_features = []
    if property_obj.bedrooms:
        property_features.append(f"{property_obj.bedrooms} Bedroom{'s' if property_obj.bedrooms > 1 else ''}")
    if property_obj.bathrooms:
        property_features.append(f"{property_obj.bathrooms} Bathroom{'s' if property_obj.bathrooms > 1 else ''}")
    if property_obj.parking_slots:
        property_features.append(f"{property_obj.parking_slots} Parking Space{'s' if property_obj.parking_slots > 1 else ''}")
    if property_obj.area:
        property_features.append(f"{property_obj.area} sq ft")
    
    # Get similar properties in same price range
    price_range = property_obj.price * 0.2 if property_obj.price else 0
    similar_properties = Property.objects.filter(
        property_type=property_obj.property_type,
        price__gte=property_obj.price - price_range,
        price__lte=property_obj.price + price_range
    ).exclude(pk=pk).select_related('county').prefetch_related('media')[:3]
    
    context = {
        'property': property_obj,
        'form': form,
        'related_properties': related_properties,
        'similar_properties': similar_properties,
        'property_images': property_images,
        'main_image': main_image,
        'property_features': property_features,
        'year': timezone.now().year,
    }
    return render(request, 'listings/property_detail.html', context)


def management_request(request):
    """Property management request form (GET → form, POST → save ManagementRequest)"""
    if request.method == 'POST':
        form = ManagementRequestForm(request.POST, request.FILES)
        if form.is_valid():
            # Create a property first
            property_obj = Property.objects.create(
                title=f"Property for Management - {form.cleaned_data['landlord_name']}",
                property_type=form.cleaned_data['property_type'],
                county=form.cleaned_data['county'],
                description=form.cleaned_data['service_terms'],
                price=form.cleaned_data['rent_amount']
            )
            
            # Create management request
            management_request = form.save(commit=False)
            management_request.property = property_obj
            management_request.save()
            
            # Handle uploaded images
            images = request.FILES.getlist('property_images')
            for i, image in enumerate(images):
                PropertyMedia.objects.create(
                    property=property_obj,
                    media_type='image',
                    file=image,
                    order=i,
                    is_primary=(i == 0)  # First image is primary
                )
            
            # Handle uploaded videos
            videos = request.FILES.getlist('property_videos')
            for i, video in enumerate(videos):
                PropertyMedia.objects.create(
                    property=property_obj,
                    media_type='video',
                    file=video,
                    order=i + len(images)
                )
            
            # Send email notification to admins
            try:
                mail_admins(
                    subject=f"New Property Management Request from {form.cleaned_data['landlord_name']}",
                    message=f"""
                    New property management request received:
                    
                    Landlord: {form.cleaned_data['landlord_name']}
                    Contact: {form.cleaned_data['landlord_contact']}
                    Property Type: {form.cleaned_data['property_type']}
                    County: {form.cleaned_data['county']}
                    Rent Amount: KSh {form.cleaned_data['rent_amount']:,.0f}
                    
                    Service Terms:
                    {form.cleaned_data['service_terms']}
                    """,
                    fail_silently=True
                )
            except Exception:
                pass
            
            messages.success(
                request, 
                'Your property management request has been submitted successfully! We will contact you within 24 hours.'
            )
            return redirect('listings:home')
    else:
        form = ManagementRequestForm()
    
    context = {
        'form': form,
        'year': timezone.now().year,
    }
    return render(request, 'listings/management_request.html', context)


def contact_view(request):
    """Contact form handling"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save inquiry
            inquiry = Inquiry.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                inquiry_type='general',
                message=f"Subject: {form.cleaned_data['subject']}\n\n{form.cleaned_data['message']}"
            )
            
            # Send email to admins
            try:
                mail_admins(
                    subject=f"Contact Form: {form.cleaned_data['subject']}",
                    message=f"""
                    New contact form submission:
                    
                    From: {form.cleaned_data['name']} ({form.cleaned_data['email']})
                    Phone: {form.cleaned_data['phone']}
                    Subject: {form.cleaned_data['subject']}
                    
                    Message:
                    {form.cleaned_data['message']}
                    """,
                    fail_silently=True
                )
            except Exception:
                pass
            
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('listings:contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'year': timezone.now().year,
    }
    return render(request, 'listings/contact.html', context)


def services_view(request):
    """Services page"""
    context = {
        'year': timezone.now().year,
    }
    return render(request, 'listings/services.html', context)


def about_view(request):
    """About page"""
    # Get team members (agents)
    team_members = Agent.objects.filter(is_active=True).select_related('user')[:6]
    
    # Get company stats
    total_properties = Property.objects.count()
    total_agents = Agent.objects.filter(is_active=True).count()
    counties_served = County.objects.filter(is_active=True).count()
    
    context = {
        'team_members': team_members,
        'total_properties': total_properties,
        'total_agents': total_agents,
        'counties_served': counties_served,
        'year': timezone.now().year,
    }
    return render(request, 'listings/about.html', context)


@staff_member_required
def management_requests_list(request):
    """Admin view of landlord management requests"""
    requests = ManagementRequest.objects.select_related('property__county').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(requests, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'year': timezone.now().year,
    }
    return render(request, 'listings/management_requests_list.html', context)


def agent_detail(request, pk):
    """Agent detail page"""
    agent = get_object_or_404(
        Agent.objects.select_related('user'),
        pk=pk,
        is_active=True
    )
    
    # Get agent's properties
    agent_properties = Property.objects.filter(
        agent=agent,
        published=True
    ).select_related('county').prefetch_related('media')[:6]
    
    context = {
        'agent': agent,
        'agent_properties': agent_properties,
        'year': timezone.now().year,
    }
    return render(request, 'listings/agent_detail.html', context)


@require_http_methods(["GET"])
def property_search_api(request):
    """AJAX property search endpoint"""
    query = request.GET.get('q', '')
    county = request.GET.get('county', '')
    property_type = request.GET.get('type', '')
    
    properties = Property.objects.filter(published=True, status='available')
    
    if query:
        properties = properties.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) | 
            Q(location__icontains=query)
        )
    
    if county:
        properties = properties.filter(county__slug=county)
    
    if property_type:
        properties = properties.filter(property_type=property_type)
    
    # Limit results and serialize
    properties = properties.select_related('county', 'agent__user').prefetch_related('media')[:10]
    
    results = []
    for prop in properties:
        main_image = prop.main_image
        results.append({
            'id': prop.id,
            'title': prop.title,
            'county': prop.county.name,
            'price': float(prop.price),
            'bedrooms': prop.bedrooms,
            'bathrooms': prop.bathrooms,
            'area': float(prop.area),
            'image_url': main_image.file.url if main_image else None,
            'url': prop.get_absolute_url() if hasattr(prop, 'get_absolute_url') else f'/property/{prop.id}/'
        })
    
    return JsonResponse({'properties': results})