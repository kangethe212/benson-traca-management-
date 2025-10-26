from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import mail_admins
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required

from .models import Property, County, Agent, Amenity, Testimonial, Inquiry, ManagementRequest, PropertyMedia, PropertyViewing, TeamMember
from .forms import PropertyForm, InquiryForm, ContactForm, PropertySearchForm, ManagementRequestForm, PropertyViewingForm
from .notifications import NotificationService
from datetime import date, timedelta


def home(request):
    """Homepage with featured properties and testimonials"""
    # Get featured properties (sale and rent) - show up to 12
    featured_properties = Property.objects.filter(
        property_type__in=['sale', 'rent']
    ).select_related('county').prefetch_related('media')[:12]
    
    # Get featured testimonials
    featured_testimonials = Testimonial.objects.filter(
        is_featured=True, 
        is_approved=True
    ).select_related('property')[:3]
    
    context = {
        'featured_properties': featured_properties,
        'featured_testimonials': featured_testimonials,
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
    
    # Check for county filter from URL parameter (from home page search)
    county_name = request.GET.get('county')
    if county_name:
        # Search by county name (case-insensitive)
        properties = properties.filter(county__name__icontains=county_name)
    
    # Apply filters if form is valid
    if search_form.is_valid():
        # Keyword search (title and description)
        keyword = search_form.cleaned_data.get('keyword')
        if keyword:
            properties = properties.filter(
                Q(title__icontains=keyword) | 
                Q(description__icontains=keyword) |
                Q(county__name__icontains=keyword) |
                Q(county__main_towns__icontains=keyword)
            )
        
        # County filter (text input)
        county = search_form.cleaned_data.get('county')
        if county:
            properties = properties.filter(county__name__icontains=county)
        
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
    from decimal import Decimal
    price_range = Decimal(str(property_obj.price)) * Decimal('0.2') if property_obj.price else Decimal('0')
    min_price = property_obj.price - price_range
    max_price = property_obj.price + price_range
    
    similar_properties = Property.objects.filter(
        property_type=property_obj.property_type,
        price__gte=min_price,
        price__lte=max_price
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
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        if form.is_valid():
            try:
                # Get or create county from the county name
                county_name = form.cleaned_data['county']
                print(f"Creating county: {county_name}")
                county_obj, created = County.objects.get_or_create(
                    name=county_name,
                    defaults={
                        'slug': county_name.lower().replace(' ', '-'),
                        'is_active': True
                    }
                )
                print(f"County created: {created}, County: {county_obj}")
                
                # Create a property first
                print("Creating property...")
                property_obj = Property.objects.create(
                    title=f"Property for Management - {form.cleaned_data['landlord_name']}",
                    property_type=form.cleaned_data['property_type'],
                    county=county_obj,
                    town=form.cleaned_data.get('town', ''),
                    description=form.cleaned_data['service_terms'],
                    price=form.cleaned_data['rent_amount']
                )
                print(f"Property created: {property_obj.id}")
                
                # Create management request
                print("Creating management request...")
                mgmt_request = form.save(commit=False)
                mgmt_request.property = property_obj
                mgmt_request.save()
                print(f"ManagementRequest created: {mgmt_request.id}")
                
                # Handle uploaded images
                images = request.FILES.getlist('property_images')
                print(f"Processing {len(images)} images...")
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
                print(f"Processing {len(videos)} videos...")
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
                except Exception as e:
                    print(f"Email error: {e}")
                
                messages.success(
                    request, 
                    'Your property management request has been submitted successfully! We will contact you within 24 hours.'
                )
                print("Redirecting to home...")
                return redirect('listings:home')
            except Exception as e:
                print(f"Error in management request processing: {e}")
                import traceback
                traceback.print_exc()
                messages.error(request, 'There was an error processing your request. Please try again.')
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
    # Get team members from TeamMember model
    team_members = TeamMember.objects.filter(is_active=True).order_by('order', 'name')
    
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


def property_compare(request):
    """Property comparison page"""
    # Get property IDs from query parameter
    ids_param = request.GET.get('ids', '')
    
    if not ids_param:
        messages.warning(request, 'No properties selected for comparison.')
        return redirect('listings:properties_list')
    
    # Parse property IDs
    try:
        property_ids = [int(id.strip()) for id in ids_param.split(',') if id.strip()]
    except ValueError:
        messages.error(request, 'Invalid property IDs.')
        return redirect('listings:properties_list')
    
    # Limit to 3 properties maximum
    if len(property_ids) > 3:
        property_ids = property_ids[:3]
        messages.info(request, 'Maximum 3 properties can be compared at once.')
    
    if len(property_ids) < 2:
        messages.warning(request, 'Please select at least 2 properties to compare.')
        return redirect('listings:properties_list')
    
    # Get properties
    properties = Property.objects.filter(
        id__in=property_ids,
        property_type__in=['sale', 'rent']
    ).select_related('county').prefetch_related('media')
    
    if properties.count() < 2:
        messages.error(request, 'Some properties could not be found.')
        return redirect('listings:properties_list')
    
    # Ensure properties are in the same order as requested
    properties_dict = {prop.id: prop for prop in properties}
    ordered_properties = [properties_dict[pid] for pid in property_ids if pid in properties_dict]
    
    # Calculate best values for highlighting
    prices = [p.price for p in ordered_properties]
    bedrooms = [p.bedrooms for p in ordered_properties if p.bedrooms]
    bathrooms = [p.bathrooms for p in ordered_properties if p.bathrooms]
    areas = [p.area for p in ordered_properties if p.area]
    parking = [p.parking_slots for p in ordered_properties if p.parking_slots]
    
    best_values = {
        'lowest_price': min(prices) if prices else None,
        'highest_price': max(prices) if prices else None,
        'most_bedrooms': max(bedrooms) if bedrooms else None,
        'most_bathrooms': max(bathrooms) if bathrooms else None,
        'largest_area': max(areas) if areas else None,
        'most_parking': max(parking) if parking else None,
    }
    
    context = {
        'properties': ordered_properties,
        'best_values': best_values,
        'property_count': len(ordered_properties),
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/property_compare.html', context)


def book_property_viewing(request, pk):
    """Book a property viewing - Daytime only (9 AM - 6 PM)"""
    property_obj = get_object_or_404(Property, pk=pk, property_type__in=['sale', 'rent'])
    
    # Get booked time slots for next 30 days to show availability
    today = date.today()
    end_date = today + timedelta(days=30)
    
    booked_slots = PropertyViewing.objects.filter(
        property_item=property_obj,
        viewing_date__gte=today,
        viewing_date__lte=end_date,
        status__in=['pending', 'confirmed']
    ).values('viewing_date', 'viewing_time')
    
    # Convert to dict for easier lookup in template
    booked_dict = {}
    for slot in booked_slots:
        date_key = slot['viewing_date'].isoformat()
        if date_key not in booked_dict:
            booked_dict[date_key] = []
        booked_dict[date_key].append(slot['viewing_time'])
    
    if request.method == 'POST':
        form = PropertyViewingForm(request.POST, property=property_obj)
        if form.is_valid():
            viewing = form.save(commit=False)
            viewing.property_item = property_obj
            viewing.save()
            
            # Send notifications
            send_viewing_notifications(viewing, property_obj)
            
            # Mark as notified
            viewing.is_notified = True
            viewing.confirmation_sent = True
            viewing.save()
            
            messages.success(
                request,
                f'Viewing booked successfully for {viewing.viewing_date} at {viewing.get_viewing_time_display()}! '
                'Check your email for confirmation.'
            )
            return redirect('listings:viewing_confirmation', pk=viewing.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PropertyViewingForm(property=property_obj)
    
    context = {
        'property': property_obj,
        'form': form,
        'booked_slots': booked_dict,
        'time_slots': PropertyViewing.TIME_SLOTS,
        'min_date': today.isoformat(),
        'max_date': end_date.isoformat(),
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/book_viewing.html', context)


def viewing_confirmation(request, pk):
    """Viewing confirmation page"""
    viewing = get_object_or_404(PropertyViewing, pk=pk)
    
    context = {
        'viewing': viewing,
        'property': viewing.property_item,
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/viewing_confirmation.html', context)


def send_viewing_notifications(viewing, property_obj):
    """Send notifications for new viewing booking"""
    from django.conf import settings
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    
    # Prepare data
    viewing_data = {
        'customer_name': viewing.name,
        'customer_email': viewing.email,
        'customer_phone': viewing.phone,
        'property_title': property_obj.title,
        'property_location': property_obj.county.name,
        'property_price': f"KSh {property_obj.price:,.0f}" if property_obj.price else "Contact us",
        'viewing_date': viewing.viewing_date.strftime('%A, %B %d, %Y'),
        'viewing_time': viewing.get_viewing_time_display(),
        'number_of_people': viewing.number_of_people,
        'special_requests': viewing.message or 'None',
        'contact_phone': '+254 700 000 000',
        'contact_email': 'info@tracamanagement.co.ke',
        'whatsapp_number': settings.WHATSAPP_PHONE_NUMBER,
        'current_year': timezone.now().year,
        'property_url': request.build_absolute_uri(property_obj.get_absolute_url()) if 'request' in locals() else '',
    }
    
    # Send confirmation email to customer
    try:
        html_message = render_to_string('emails/viewing_confirmation.html', viewing_data)
        plain_message = strip_tags(html_message)
        
        NotificationService.send_email(
            subject=f"Viewing Confirmed - {property_obj.title}",
            message=plain_message,
            recipient_list=[viewing.email],
            html_message=html_message
        )
    except Exception as e:
        print(f"Error sending customer confirmation: {e}")
    
    # Send notification to admin
    admin_message = f"""
New Property Viewing Booked!

Property: {property_obj.title}
Location: {property_obj.county.name}
Price: {viewing_data['property_price']}

Customer Details:
Name: {viewing.name}
Email: {viewing.email}
Phone: {viewing.phone}

Viewing Schedule:
Date: {viewing_data['viewing_date']}
Time: {viewing_data['viewing_time']}
Number of People: {viewing.number_of_people}

Special Requests: {viewing.message or 'None'}

Please prepare the property for viewing and contact the customer if needed.
    """
    
    try:
        admin_recipient = {'email': settings.ADMINS[0][1]}
        NotificationService.send_notification(
            recipient=admin_recipient,
            subject=f"🏠 New Viewing Booked - {property_obj.title}",
            message=admin_message,
            channels=['email']
        )
    except Exception as e:
        print(f"Error sending admin notification: {e}")
    
    # Send SMS if it's a same-day or next-day booking
    if settings.ENABLE_SMS_NOTIFICATIONS and viewing.viewing_date <= date.today() + timedelta(days=1):
        try:
            sms_message = f"URGENT: Viewing booked for {property_obj.title} on {viewing_data['viewing_date']} at {viewing_data['viewing_time']}. Customer: {viewing.name}, Phone: {viewing.phone}"
            NotificationService.send_sms(settings.WHATSAPP_PHONE_NUMBER, sms_message)
        except Exception as e:
            print(f"Error sending SMS: {e}")