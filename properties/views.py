from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Property
from datetime import datetime

def home(request):
    """Homepage view with featured properties and dummy data"""
    
    # Get featured properties (in real app, these would come from database)
    featured_properties = [
        {
            'id': 1,
            'title': 'Modern 3-Bedroom Home in Karen',
            'location': 'Karen, Nairobi',
            'county': 'Nairobi',
            'price': 25000000,
            'bedrooms': 3,
            'bathrooms': 3,
            'parking': 2,
            'area': 250.0,
            'property_type': 'home',
            'main_image': '/static/images/property1.jpg',
            'status': 'available'
        },
        {
            'id': 2,
            'title': 'Luxury Rental Apartment in Westlands',
            'location': 'Westlands, Nairobi',
            'county': 'Nairobi',
            'price': 18000000,
            'bedrooms': 2,
            'bathrooms': 2,
            'parking': 1,
            'area': 120.0,
            'property_type': 'rental',
            'main_image': '/static/images/property2.jpg',
            'status': 'available'
        },
        {
            'id': 3,
            'title': 'Executive Office Space in Mombasa CBD',
            'location': 'Mombasa CBD',
            'county': 'Mombasa',
            'price': 15000000,
            'bedrooms': 0,
            'bathrooms': 2,
            'parking': 5,
            'area': 200.0,
            'property_type': 'office',
            'main_image': '/static/images/property3.jpg',
            'status': 'available'
        },
        {
            'id': 4,
            'title': 'Premium Gated Community Villa in Kisumu',
            'location': 'Kisumu, Milimani',
            'county': 'Kisumu',
            'price': 22000000,
            'bedrooms': 4,
            'bathrooms': 3,
            'parking': 2,
            'area': 350.0,
            'property_type': 'gated_community',
            'main_image': '/static/images/property4.jpg',
            'status': 'available'
        },
        {
            'id': 5,
            'title': 'Spacious Family Home in Nakuru',
            'location': 'Nakuru Town',
            'county': 'Nakuru',
            'price': 12000000,
            'bedrooms': 3,
            'bathrooms': 2,
            'parking': 2,
            'area': 180.0,
            'property_type': 'home',
            'main_image': '/static/images/property5.jpg',
            'status': 'available'
        },
        {
            'id': 6,
            'title': 'Beachfront Rental Villa in Malindi',
            'location': 'Malindi Beach',
            'county': 'Kilifi',
            'price': 35000000,
            'bedrooms': 5,
            'bathrooms': 4,
            'parking': 3,
            'area': 400.0,
            'property_type': 'rental',
            'main_image': '/static/images/property6.jpg',
            'status': 'available'
        }
    ]
    
    # Testimonials data
    testimonials = [
        {
            'name': 'Sarah Wanjiku',
            'location': 'Nairobi',
            'text': 'Traca Management Services helped me find my dream home in Karen. Their agents were professional and the process was smooth.',
            'rating': 5
        },
        {
            'name': 'John Mwangi',
            'location': 'Mombasa',
            'text': 'Excellent service! They found me a perfect commercial property in Mombasa CBD. Highly recommended.',
            'rating': 5
        },
        {
            'name': 'Grace Akinyi',
            'location': 'Kisumu',
            'text': 'The team at Traca Management Services made selling my property stress-free. Great communication throughout.',
            'rating': 5
        }
    ]
    
    # Why choose us data
    why_choose_us = [
        {
            'icon': 'fas fa-shield-alt',
            'title': 'Trustworthy Agents',
            'description': 'Our certified real estate agents are committed to providing honest, transparent service.'
        },
        {
            'icon': 'fas fa-check-circle',
            'title': 'Verified Listings',
            'description': 'All our properties are thoroughly verified to ensure accuracy and authenticity.'
        },
        {
            'icon': 'fas fa-map-marker-alt',
            'title': 'County-wide Coverage',
            'description': 'We serve all 47 counties in Kenya with local expertise and knowledge.'
        },
        {
            'icon': 'fas fa-dollar-sign',
            'title': 'Affordable Deals',
            'description': 'Competitive pricing and flexible payment options to suit your budget.'
        }
    ]
    
    # Kenyan counties for search dropdown
    counties = [
        'Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Thika', 'Malindi', 'Kitale',
        'Garissa', 'Kakamega', 'Meru', 'Nyeri', 'Machakos', 'Kiambu', 'Muranga', 'Nyeri',
        'Kirinyaga', 'Embu', 'Kitui', 'Makueni', 'Taita Taveta', 'Tana River', 'Lamu',
        'Kilifi', 'Kwale', 'Taita Taveta', 'Kajiado', 'Narok', 'Bomet', 'Kericho',
        'Nandi', 'Uasin Gishu', 'Elgeyo Marakwet', 'West Pokot', 'Samburu', 'Turkana',
        'Marsabit', 'Isiolo', 'Mandera', 'Wajir', 'Baringo', 'Laikipia', 'Nakuru',
        'Trans Nzoia', 'Bungoma', 'Busia', 'Vihiga', 'Siaya', 'Homa Bay', 'Migori',
        'Kisii', 'Nyamira', 'Nyandarua'
    ]
    
    context = {
        'properties': featured_properties,
        'testimonials': testimonials,
        'why_choose_us': why_choose_us,
        'counties': counties,
        'year': datetime.now().year,
    }
    
    return render(request, 'properties/home.html', context)

def property_search(request):
    """Handle property search form submission"""
    if request.method == 'GET':
        county = request.GET.get('county', '')
        property_type = request.GET.get('type', '')
        bedrooms = request.GET.get('bedrooms', '')
        price = request.GET.get('price', '')
        
        # Property type mapping for display
        property_type_display = {
            'home': 'Home',
            'rental': 'Rental',
            'office': 'Office',
            'gated_community': 'Gated Community'
        }
        
        # In a real application, you would filter the database here
        # For now, return a simple response with better formatting
        return JsonResponse({
            'message': 'Search functionality will be implemented',
            'search_criteria': {
                'county': county if county else 'All Counties',
                'property_type': property_type_display.get(property_type, 'All Types'),
                'bedrooms': bedrooms if bedrooms else 'Any',
                'price_range': price if price else 'Any'
            },
            'filters': {
                'county': county,
                'type': property_type,
                'bedrooms': bedrooms,
                'price': price
            }
        })
    
    return JsonResponse({'error': 'Invalid request method'})

def properties_list(request):
    """Properties listing page with filtering and pagination"""
    
    # Get all properties (in real app, these would come from database with filtering)
    all_properties = [
        {
            'id': 1,
            'title': 'Modern 3-Bedroom Home in Karen',
            'location': 'Karen, Nairobi',
            'county': 'Nairobi',
            'price': 25000000,
            'bedrooms': 3,
            'bathrooms': 3,
            'parking': 2,
            'area': 250.0,
            'property_type': 'home',
            'main_image': '/static/images/property1.jpg',
            'status': 'available'
        },
        {
            'id': 2,
            'title': 'Luxury Rental Apartment in Westlands',
            'location': 'Westlands, Nairobi',
            'county': 'Nairobi',
            'price': 18000000,
            'bedrooms': 2,
            'bathrooms': 2,
            'parking': 1,
            'area': 120.0,
            'property_type': 'rental',
            'main_image': '/static/images/property2.jpg',
            'status': 'available'
        },
        {
            'id': 3,
            'title': 'Executive Office Space in Mombasa CBD',
            'location': 'Mombasa CBD',
            'county': 'Mombasa',
            'price': 15000000,
            'bedrooms': 0,
            'bathrooms': 2,
            'parking': 5,
            'area': 200.0,
            'property_type': 'office',
            'main_image': '/static/images/property3.jpg',
            'status': 'available'
        },
        {
            'id': 4,
            'title': 'Premium Gated Community Villa in Kisumu',
            'location': 'Kisumu, Milimani',
            'county': 'Kisumu',
            'price': 22000000,
            'bedrooms': 4,
            'bathrooms': 3,
            'parking': 2,
            'area': 350.0,
            'property_type': 'gated_community',
            'main_image': '/static/images/property4.jpg',
            'status': 'available'
        },
        {
            'id': 5,
            'title': 'Spacious Family Home in Nakuru',
            'location': 'Nakuru Town',
            'county': 'Nakuru',
            'price': 12000000,
            'bedrooms': 3,
            'bathrooms': 2,
            'parking': 2,
            'area': 180.0,
            'property_type': 'home',
            'main_image': '/static/images/property5.jpg',
            'status': 'available'
        },
        {
            'id': 6,
            'title': 'Beachfront Rental Villa in Malindi',
            'location': 'Malindi Beach',
            'county': 'Kilifi',
            'price': 35000000,
            'bedrooms': 5,
            'bathrooms': 4,
            'parking': 3,
            'area': 400.0,
            'property_type': 'rental',
            'main_image': '/static/images/property6.jpg',
            'status': 'available'
        },
        {
            'id': 7,
            'title': 'Commercial Land in Kiambu',
            'location': 'Kiambu Town',
            'county': 'Kiambu',
            'price': 8000000,
            'bedrooms': 0,
            'bathrooms': 0,
            'parking': 0,
            'area': 500.0,
            'property_type': 'land',
            'main_image': '/static/images/property1.jpg',
            'status': 'available'
        },
        {
            'id': 8,
            'title': 'Modern Apartment in Machakos',
            'location': 'Machakos Town',
            'county': 'Machakos',
            'price': 9500000,
            'bedrooms': 2,
            'bathrooms': 2,
            'parking': 1,
            'area': 100.0,
            'property_type': 'apartment',
            'main_image': '/static/images/property2.jpg',
            'status': 'available'
        },
        {
            'id': 9,
            'title': 'Family House in Murang\'a',
            'location': 'Murang\'a Town',
            'county': 'Murang\'a',
            'price': 11000000,
            'bedrooms': 3,
            'bathrooms': 2,
            'parking': 2,
            'area': 200.0,
            'property_type': 'house',
            'main_image': '/static/images/property3.jpg',
            'status': 'available'
        }
    ]
    
    # Apply filters based on request parameters
    filtered_properties = all_properties
    
    county = request.GET.get('county', '')
    property_type = request.GET.get('type', '')
    bedrooms = request.GET.get('bedrooms', '')
    price = request.GET.get('price', '')
    
    if county:
        filtered_properties = [p for p in filtered_properties if p['county'].lower() == county.lower()]
    
    if property_type:
        filtered_properties = [p for p in filtered_properties if p['property_type'] == property_type]
    
    if bedrooms:
        if bedrooms == '4':
            filtered_properties = [p for p in filtered_properties if p['bedrooms'] >= 4]
        else:
            filtered_properties = [p for p in filtered_properties if p['bedrooms'] == int(bedrooms)]
    
    if price:
        if price == 'below_5m':
            filtered_properties = [p for p in filtered_properties if p['price'] < 5000000]
        elif price == '5m_10m':
            filtered_properties = [p for p in filtered_properties if 5000000 <= p['price'] <= 10000000]
        elif price == 'above_10m':
            filtered_properties = [p for p in filtered_properties if p['price'] > 10000000]
    
    context = {
        'properties': filtered_properties,
        'year': datetime.now().year,
        'filters': {
            'county': county,
            'type': property_type,
            'bedrooms': bedrooms,
            'price': price
        }
    }
    
    return render(request, 'properties/properties_list.html', context)

def property_detail(request, property_id):
    """Property detail page"""
    # In a real app, this would fetch from database
    property_data = {
        'id': property_id,
        'title': 'Modern 3-Bedroom Home in Karen',
        'location': 'Karen, Nairobi',
        'county': 'Nairobi',
        'price': 25000000,
        'bedrooms': 3,
        'bathrooms': 3,
        'parking': 2,
        'area': 250.0,
        'property_type': 'home',
        'main_image': '/static/images/property1.jpg',
        'status': 'available',
        'description': 'This stunning modern home in Karen offers the perfect blend of luxury and comfort. Featuring spacious rooms, modern amenities, and a prime location in one of Nairobi\'s most prestigious neighborhoods.'
    }
    
    context = {
        'property': property_data,
        'year': datetime.now().year
    }
    
    return render(request, 'properties/property_detail.html', context)

def services(request):
    """Services page view"""
    context = {
        'year': datetime.now().year,
    }
    return render(request, 'properties/services.html', context)

def about(request):
    """About page view"""
    context = {
        'year': datetime.now().year,
    }
    return render(request, 'properties/about.html', context)

def list_property(request):
    """List property page view"""
    if request.method == 'POST':
        # Handle form submission
        # This would typically save to database
        # For now, we'll just show a success message
        messages.success(request, 'Your property has been submitted successfully! We will contact you within 24 hours.')
        return redirect('properties:home')
    
    context = {
        'year': datetime.now().year,
    }
    return render(request, 'properties/list_property.html', context)