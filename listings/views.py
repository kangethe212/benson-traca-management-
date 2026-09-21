from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import mail_admins
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache

from .models import (
    Property, County, Agent, Amenity, Testimonial, Inquiry, PropertyMedia,
    PropertyViewing, TeamMember, HomepageHeroSettings
)
from .forms import PropertyForm, InquiryForm, ContactForm, PropertySearchForm, PropertyViewingForm
from .notifications_enhanced import NotificationService
from datetime import date, timedelta
import json
import time
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def _dbg(hypothesis_id, location, message, data=None):
    """Lightweight debug helper: logs only when DEBUG=True and uses Django logging.

    This avoids writing absolute-path files and prevents leaking data in production.
    """
    if not getattr(settings, 'DEBUG', False):
        return

    try:
        payload = {
            'sessionId': 'local',
            'timestamp': int(time.time() * 1000),
            'hypothesisId': hypothesis_id,
            'location': location,
            'message': message,
            'data': data or {},
            'runId': 'run-localhost',
        }
        logger.debug(json.dumps(payload))
    except Exception:
        # never raise from debug helper
        pass


def home(request):
    """Simple homepage with sample data"""
    # #region agent log
    _dbg('A', 'listings/views.py:home', 'home entered', {'path': request.path, 'method': request.method})
    # #endregion
    try:
        # Show active listings regardless of verification state, while the template
        # still highlights properties that are explicitly marked as verified.
        featured_properties = Property.objects.filter(
            property_type__in=['sale', 'rent']
        ).select_related('county').prefetch_related('media')[:14]
    except Exception as e:
        print(f"Error getting properties: {e}")
        featured_properties = []
        # #region agent log
        _dbg('A', 'listings/views.py:home', 'home featured query failed', {'error': str(e)})
        # #endregion
    
    hero_property = featured_properties[0] if featured_properties else None
    hero_settings = HomepageHeroSettings.get_or_create_singleton()
    if hero_settings.is_active and (hero_settings.hero_image or hero_settings.hero_image_url):
        hero_background_url = hero_settings.background_image
    elif hero_property and getattr(hero_property, 'main_image_url', None):
        hero_background_url = hero_property.main_image_url
    else:
        hero_background_url = getattr(settings, 'HERO_BACKGROUND_IMAGE', '/static/images/property2.jpg')

    popular_locations = [
        {'name': 'Nairobi', 'slug': 'nairobi', 'type': 'sale'},
        {'name': 'Kitengela', 'slug': 'kitengela', 'type': 'sale'},
        {'name': 'Kajiado', 'slug': 'kajiado', 'type': 'sale'},
        {'name': 'Mombasa', 'slug': 'mombasa', 'type': 'sale'},
        {'name': 'Nakuru', 'slug': 'nakuru', 'type': 'sale'},
        {'name': 'Machakos', 'slug': 'machakos', 'type': 'sale'},
        {'name': 'Athi River', 'slug': 'athi-river', 'type': 'sale'},
        {'name': 'Naivasha', 'slug': 'naivasha', 'type': 'sale'},
        {'name': 'Thika', 'slug': 'thika', 'type': 'sale'},
        {'name': 'Kisumu', 'slug': 'kisumu', 'type': 'sale'},
    ]

    context = {
        'featured_properties': featured_properties,
        'year': timezone.now().year,
        'hero_background_url': hero_background_url,
        'popular_locations': popular_locations,
    }
    # #region agent log
    _dbg('B', 'listings/views.py:home', 'home rendering', {
        'template': 'listings/home_simple_clean.html',
        'featured_count': len(list(featured_properties)) if featured_properties is not None else 0,
    })
    # #endregion
    return render(request, 'listings/home_simple_clean.html', context)


def properties_list(request):
    """Enhanced property listings page with advanced filters and professional features"""
    # Initialize search form
    search_form = PropertySearchForm(request.GET)
    # #region agent log
    _dbg('B', 'listings/views.py:properties_list', 'properties_list entered', {
        'query': dict(request.GET),
        'form_valid': search_form.is_valid(),
    })
    # #endregion
    
    # Start with base queryset - list active sale/rent properties, regardless of
    # verification state. The verified badge is displayed separately when set.
    properties = Property.objects.filter(
        property_type__in=['sale', 'rent']
    ).select_related('county').prefetch_related('media')
    # #region agent log
    _dbg('B', 'listings/views.py:properties_list', 'verified filter applied', {
        'verified_count': properties.count(),
        'all_count': Property.objects.filter(property_type__in=['sale', 'rent']).count(),
    })
    # #endregion
    
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
                Q(town__icontains=keyword) |
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
        
        near_school = search_form.cleaned_data.get('near_school')
        if near_school:
            properties = properties.filter(near_school=True)
    
    # Sort results
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'price_low':
        properties = properties.order_by('price')
    elif sort_by == 'price_high':
        properties = properties.order_by('-price')
    elif sort_by == 'bedrooms':
        properties = properties.order_by('-bedrooms')
    elif sort_by == 'area':
        properties = properties.order_by('-area')
    else:
        properties = properties.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(properties, 12)  # 12 properties per page
    page = request.GET.get('page')
    properties_page = paginator.get_page(page)
    
    context = {
        'properties': properties_page,
        'search_form': search_form,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': properties_page,
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/properties_list.html', context)


def property_detail(request, pk):
    """Enhanced property detail page with performance optimizations"""
    # #region agent log
    _dbg('D', 'listings/views.py:property_detail', 'property_detail entered', {
        'pk': pk,
        'method': request.method,
        'path': request.path,
        'has_post': bool(request.POST),
        'post_keys': list(request.POST.keys())[:12] if request.method == 'POST' else [],
    })
    # #endregion
    if request.method == 'POST':
        return property_inquiry(request, pk)
    # Fetch the current property state directly from the database; caching the
    # full instance here causes stale verification/badge data after updates.
    property = get_object_or_404(
        Property.objects.select_related('county').prefetch_related(
            'media', 'amenities', 'inquiries'
        ),
        pk=pk, property_type__in=['sale', 'rent']
    )
    
    # Increment view count (with optimization)
    increment_view_count(property)
    
    # Get similar properties (cache for 30 minutes)
    similar_cache_key = f'similar_properties_{pk}'
    similar_properties = cache.get(similar_cache_key)
    
    if similar_properties is None:
        similar_properties = Property.objects.filter(
            property_type__in=['sale', 'rent'],
            county=property.county,
            is_verified=True
        ).exclude(pk=pk).select_related('county').prefetch_related('media')[:6]
        
        cache.set(similar_cache_key, similar_properties, 1800)  # 30 minutes
    
    property_images = property.media.filter(
        media_type='image'
    ).exclude(file='').order_by('-is_primary', 'order', 'id')

    property_features = []
    if property.is_furnished:
        property_features.append('Furnished')
    if property.pet_friendly:
        property_features.append('Pet Friendly')
    if property.near_school:
        property_features.append('Near School')

    context = {
        'property': property,
        'property_images': property_images,
        'property_features': property_features,
        'similar_properties': similar_properties,
        'related_properties': similar_properties,
        'inquiry_form': InquiryForm(),
        'form': InquiryForm(),
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/property_detail.html', context)


def increment_view_count(property):
    """Optimized view count increment"""
    # Use cache to avoid frequent database writes
    cache_key = f'property_views_{property.id}'
    views = cache.get(cache_key, 0)
    
    if views >= 10:  # Write to database every 10 views
        property.view_count = property.view_count + views
        property.save(update_fields=['view_count'])
        cache.set(cache_key, 0, 3600)  # Reset counter
    else:
        cache.set(cache_key, views + 1, 3600)  # Increment counter


@require_http_methods(["GET"])
def property_search_api(request):
    """Public search suggestions used by the website search field."""
    query = (request.GET.get('q') or '').strip()
    county = (request.GET.get('county') or '').strip()
    property_type = (request.GET.get('type') or '').strip()
    # #region agent log
    _dbg('H1', 'listings/views.py:property_search_api', 'search api entered', {
        'query': query,
        'county': county,
        'property_type': property_type,
        'has_published': hasattr(Property, 'published'),
    })
    # #endregion
    if len(query) < 2 and not county and not property_type:
        return JsonResponse({'suggestions': [], 'properties': []})

    properties = Property.objects.filter(
        property_type__in=['sale', 'rent'],
        is_verified=True,
    ).select_related('county').prefetch_related('media')
    if query:
        properties = properties.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(town__icontains=query)
            | Q(county__name__icontains=query)
        )
    if county:
        properties = properties.filter(
            Q(county__name__icontains=county) | Q(county__slug__icontains=county)
        )
    if property_type:
        properties = properties.filter(property_type=property_type)

    suggestions = []
    for prop in properties[:10]:
        suggestions.append({
            'id': prop.id,
            'title': prop.title,
            'county': prop.county.name,
            'price': float(prop.price) if prop.price is not None else None,
            'bedrooms': prop.bedrooms,
            'bathrooms': prop.bathrooms,
            'area': float(prop.area) if prop.area is not None else None,
            'image_url': prop.main_image_url,
            'url': prop.get_absolute_url(),
            'type': 'property',
        })
    # #region agent log
    _dbg('H1', 'listings/views.py:property_search_api', 'search api success', {
        'count': len(suggestions),
        'sample_url': suggestions[0]['url'] if suggestions else None,
    })
    # #endregion
    return JsonResponse({'suggestions': suggestions, 'properties': suggestions})


@require_http_methods(["POST"])
def property_inquiry(request, pk):
    """Handle property inquiry with enhanced validation and notifications"""
    # #region agent log
    _dbg('D', 'listings/views.py:property_inquiry', 'property_inquiry entered', {
        'pk': pk,
        'post_keys': list(request.POST.keys())[:12],
    })
    # #endregion
    property = get_object_or_404(Property, pk=pk)
    
    form = InquiryForm(request.POST)
    if form.is_valid():
        inquiry = form.save(commit=False)
        inquiry.property = property
        inquiry.save()
        
        # Send notifications asynchronously
        try:
            NotificationService.send_property_inquiry_notification(inquiry)
            messages.success(
                request,
                'Thank you. We have received your enquiry and a colleague will be in touch shortly.'
            )
        except Exception as e:
            messages.warning(
                request,
                'We have received your enquiry. If you do not hear from us soon, please call or WhatsApp us.'
            )
        
        # #region agent log
        _dbg('D', 'listings/views.py:property_inquiry', 'inquiry saved', {'pk': pk, 'inquiry_id': inquiry.id})
        # #endregion
        return redirect('listings:property_detail', pk=pk)
    else:
        messages.error(request, 'Please check the highlighted fields and try again.')
    
    # Get similar properties
    similar_properties = Property.objects.filter(
        property_type__in=['sale', 'rent'],
        county=property.county,
        is_verified=True
    ).exclude(pk=pk)[:6]
    
    context = {
        'property': property,
        'similar_properties': similar_properties,
        'inquiry_form': form,
        'form': form,
        'year': timezone.now().year,
    }
    
    return render(request, 'listings/property_detail.html', context)


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
            
            messages.success(
                request,
                'Thank you for writing to us. We typically respond within one business day.'
            )
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


def services_view(request):
    """Services page showing all TRACA Management services"""
    context = {
        'year': timezone.now().year,
    }
    return render(request, 'listings/services_enhanced.html', context)


def about_view(request):
    """About page with company information"""
    context = {
        'year': timezone.now().year,
    }
    return render(request, 'listings/about_enhanced.html', context)


def contact_view(request):
    """Contact page with contact form"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Persist as an inquiry in the company inbox pipeline.
            inquiry = Inquiry.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data.get('phone', ''),
                inquiry_type='general',
                message=f"Subject: {form.cleaned_data['subject']}\n\n{form.cleaned_data['message']}"
            )

            try:
                NotificationService.send_contact_notification(form)
            except Exception as e:
                print(f"Error sending contact notification: {e}")

            messages.success(request, 'Your message has been sent successfully! We will contact you soon.')
            return redirect('listings:contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'year': timezone.now().year,
    }
    return render(request, 'listings/contact.html', context)