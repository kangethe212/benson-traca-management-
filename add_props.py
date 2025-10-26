import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from listings.models import Property, County
from decimal import Decimal

# Get Nairobi county
nairobi, created = County.objects.get_or_create(
    name='Nairobi', 
    defaults={'slug': 'nairobi', 'is_active': True}
)

# Add properties
properties = [
    {
        'title': 'Modern Apartment for Sale in Westlands',
        'property_type': 'sale',
        'county': nairobi,
        'price': Decimal('8500000'),
        'bedrooms': 2,
        'bathrooms': 2,
        'parking_slots': 1,
        'description': 'Beautiful modern apartment in Westlands',
        'is_published': True,
        'is_featured': True
    },
    {
        'title': 'Spacious House for Sale in Karen',
        'property_type': 'sale',
        'county': nairobi,
        'price': Decimal('12000000'),
        'bedrooms': 4,
        'bathrooms': 3,
        'parking_slots': 2,
        'description': 'Large family house in Karen',
        'is_published': True,
        'is_featured': True
    },
    {
        'title': 'Cozy Studio for Rent in Kilimani',
        'property_type': 'rent',
        'county': nairobi,
        'price': Decimal('45000'),
        'bedrooms': 1,
        'bathrooms': 1,
        'parking_slots': 1,
        'description': 'Perfect studio apartment',
        'is_published': True,
        'is_featured': True
    },
    {
        'title': 'Duplex for Rent in Lavington',
        'property_type': 'rent',
        'county': nairobi,
        'price': Decimal('110000'),
        'bedrooms': 3,
        'bathrooms': 3,
        'parking_slots': 2,
        'description': 'Beautiful duplex in Lavington',
        'is_published': True,
        'is_featured': True
    },
    {
        'title': 'Townhouse for Sale in Runda',
        'property_type': 'sale',
        'county': nairobi,
        'price': Decimal('9500000'),
        'bedrooms': 3,
        'bathrooms': 2,
        'parking_slots': 2,
        'description': 'Modern townhouse in Runda',
        'is_published': True,
        'is_featured': True
    },
    {
        'title': 'Penthouse for Sale in Upper Hill',
        'property_type': 'sale',
        'county': nairobi,
        'price': Decimal('18000000'),
        'bedrooms': 4,
        'bathrooms': 3,
        'parking_slots': 2,
        'description': 'Luxury penthouse with city views',
        'is_published': True,
        'is_featured': True
    },
    {
        'title': 'Apartment for Rent in Nyali',
        'property_type': 'rent',
        'county': nairobi,
        'price': Decimal('75000'),
        'bedrooms': 2,
        'bathrooms': 2,
        'parking_slots': 1,
        'description': 'Modern apartment near the beach',
        'is_published': True,
        'is_featured': False
    },
    {
        'title': 'House for Sale in Kisumu',
        'property_type': 'sale',
        'county': nairobi,
        'price': Decimal('6500000'),
        'bedrooms': 3,
        'bathrooms': 2,
        'parking_slots': 2,
        'description': 'Comfortable house in Kisumu',
        'is_published': True,
        'is_featured': False
    },
    {
        'title': 'Studio for Rent in Nakuru',
        'property_type': 'rent',
        'county': nairobi,
        'price': Decimal('35000'),
        'bedrooms': 1,
        'bathrooms': 1,
        'parking_slots': 1,
        'description': 'Affordable studio apartment',
        'is_published': True,
        'is_featured': False
    },
    {
        'title': 'Villa for Rent in Eldoret',
        'property_type': 'rent',
        'county': nairobi,
        'price': Decimal('85000'),
        'bedrooms': 4,
        'bathrooms': 3,
        'parking_slots': 2,
        'description': 'Spacious villa with garden',
        'is_published': True,
        'is_featured': False
    },
    {
        'title': 'Apartment for Rent in Thika',
        'property_type': 'rent',
        'county': nairobi,
        'price': Decimal('55000'),
        'bedrooms': 2,
        'bathrooms': 2,
        'parking_slots': 1,
        'description': 'Modern apartment in Thika',
        'is_published': True,
        'is_featured': False
    },
    {
        'title': 'House for Rent in Westlands',
        'property_type': 'rent',
        'county': nairobi,
        'price': Decimal('95000'),
        'bedrooms': 3,
        'bathrooms': 2,
        'parking_slots': 2,
        'description': 'Comfortable house in Westlands',
        'is_published': True,
        'is_featured': False
    }
]

added = 0
for prop_data in properties:
    if not Property.objects.filter(title=prop_data['title']).exists():
        Property.objects.create(**prop_data)
        print(f'Added: {prop_data["title"]}')
        added += 1
    else:
        print(f'Exists: {prop_data["title"]}')

final = Property.objects.filter(property_type__in=['sale', 'rent']).count()
print(f'Added: {added}, Total sale/rent properties: {final}')
