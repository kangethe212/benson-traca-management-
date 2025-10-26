#!/usr/bin/env python
"""
Script to add more properties to ensure at least 12 properties are available
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from listings.models import Property, County, Amenity
from decimal import Decimal
import random

def add_properties():
    """Add more properties to reach at least 12 total"""
    
    # Check current count
    current_count = Property.objects.count()
    print(f"Current properties: {current_count}")
    
    if current_count >= 12:
        print("Already have 12+ properties!")
        return
    
    # Get or create counties
    counties_data = [
        {'name': 'Nairobi', 'slug': 'nairobi'},
        {'name': 'Mombasa', 'slug': 'mombasa'},
        {'name': 'Kisumu', 'slug': 'kisumu'},
        {'name': 'Nakuru', 'slug': 'nakuru'},
        {'name': 'Eldoret', 'slug': 'eldoret'},
        {'name': 'Thika', 'slug': 'thika'},
        {'name': 'Malindi', 'slug': 'malindi'},
        {'name': 'Kitale', 'slug': 'kitale'},
    ]
    
    counties = {}
    for county_data in counties_data:
        county, created = County.objects.get_or_create(
            name=county_data['name'],
            defaults={'slug': county_data['slug'], 'is_active': True}
        )
        counties[county_data['name']] = county
        if created:
            print(f"Created county: {county_data['name']}")
    
    # Property data
    properties_data = [
        {
            'title': 'Modern Apartment in Westlands',
            'property_type': 'apartment',
            'county': counties['Nairobi'],
            'price': Decimal('85000'),
            'bedrooms': 2,
            'bathrooms': 2,
            'parking_slots': 1,
            'description': 'Beautiful modern apartment in Westlands with great amenities and security.',
            'is_published': True,
            'is_featured': True
        },
        {
            'title': 'Spacious House in Karen',
            'property_type': 'house',
            'county': counties['Nairobi'],
            'price': Decimal('120000'),
            'bedrooms': 4,
            'bathrooms': 3,
            'parking_slots': 2,
            'description': 'Large family house in Karen with garden and swimming pool.',
            'is_published': True,
            'is_featured': True
        },
        {
            'title': 'Beachfront Villa in Diani',
            'property_type': 'villa',
            'county': counties['Mombasa'],
            'price': Decimal('200000'),
            'bedrooms': 5,
            'bathrooms': 4,
            'parking_slots': 3,
            'description': 'Luxury beachfront villa with stunning ocean views.',
            'is_published': True,
            'is_featured': True
        },
        {
            'title': 'Cozy Studio in Kilimani',
            'property_type': 'studio',
            'county': counties['Nairobi'],
            'price': Decimal('45000'),
            'bedrooms': 1,
            'bathrooms': 1,
            'parking_slots': 1,
            'description': 'Perfect studio apartment for young professionals in Kilimani.',
            'is_published': True,
            'is_featured': False
        },
        {
            'title': 'Townhouse in Runda',
            'property_type': 'townhouse',
            'county': counties['Nairobi'],
            'price': Decimal('95000'),
            'bedrooms': 3,
            'bathrooms': 2,
            'parking_slots': 2,
            'description': 'Modern townhouse in Runda with excellent security.',
            'is_published': True,
            'is_featured': True
        },
        {
            'title': 'Penthouse in Upper Hill',
            'property_type': 'penthouse',
            'county': counties['Nairobi'],
            'price': Decimal('180000'),
            'bedrooms': 4,
            'bathrooms': 3,
            'parking_slots': 2,
            'description': 'Luxury penthouse with city views in Upper Hill.',
            'is_published': True,
            'is_featured': True
        },
        {
            'title': 'Duplex in Lavington',
            'property_type': 'duplex',
            'county': counties['Nairobi'],
            'price': Decimal('110000'),
            'bedrooms': 3,
            'bathrooms': 3,
            'parking_slots': 2,
            'description': 'Beautiful duplex in Lavington with garden.',
            'is_published': True,
            'is_featured': False
        },
        {
            'title': 'Apartment in Nyali',
            'property_type': 'apartment',
            'county': counties['Mombasa'],
            'price': Decimal('75000'),
            'bedrooms': 2,
            'bathrooms': 2,
            'parking_slots': 1,
            'description': 'Modern apartment in Nyali near the beach.',
            'is_published': True,
            'is_featured': False
        },
        {
            'title': 'House in Kisumu CBD',
            'property_type': 'house',
            'county': counties['Kisumu'],
            'price': Decimal('65000'),
            'bedrooms': 3,
            'bathrooms': 2,
            'parking_slots': 2,
            'description': 'Comfortable house in Kisumu CBD with good access to amenities.',
            'is_published': True,
            'is_featured': False
        },
        {
            'title': 'Studio in Nakuru',
            'property_type': 'studio',
            'county': counties['Nakuru'],
            'price': Decimal('35000'),
            'bedrooms': 1,
            'bathrooms': 1,
            'parking_slots': 1,
            'description': 'Affordable studio apartment in Nakuru town.',
            'is_published': True,
            'is_featured': False
        },
        {
            'title': 'Villa in Eldoret',
            'property_type': 'villa',
            'county': counties['Eldoret'],
            'price': Decimal('85000'),
            'bedrooms': 4,
            'bathrooms': 3,
            'parking_slots': 2,
            'description': 'Spacious villa in Eldoret with garden.',
            'is_published': True,
            'is_featured': False
        },
        {
            'title': 'Apartment in Thika',
            'property_type': 'apartment',
            'county': counties['Thika'],
            'price': Decimal('55000'),
            'bedrooms': 2,
            'bathrooms': 2,
            'parking_slots': 1,
            'description': 'Modern apartment in Thika with good amenities.',
            'is_published': True,
            'is_featured': False
        }
    ]
    
    # Add properties
    added_count = 0
    for prop_data in properties_data:
        # Check if property already exists
        if Property.objects.filter(title=prop_data['title']).exists():
            print(f"Property '{prop_data['title']}' already exists, skipping...")
            continue
            
        try:
            property_obj = Property.objects.create(**prop_data)
            print(f"Added property: {property_obj.title}")
            added_count += 1
        except Exception as e:
            print(f"Error adding property '{prop_data['title']}': {e}")
    
    # Final count
    final_count = Property.objects.count()
    print(f"\nProperties added: {added_count}")
    print(f"Total properties now: {final_count}")
    
    if final_count >= 12:
        print("✅ Success! You now have 12+ properties available.")
    else:
        print(f"⚠️ Still need {12 - final_count} more properties to reach 12.")

if __name__ == '__main__':
    add_properties()
