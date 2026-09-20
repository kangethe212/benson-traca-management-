from django.core.management.base import BaseCommand
from decimal import Decimal
from django.utils import timezone
from listings.models import County, Property, Amenity, Landlord
from django.contrib.auth.models import User
import random

class Command(BaseCommand):
    help = 'Create extensive sample data for TRACA Management System'

    def handle(self, *args, **options):
        # Get or create counties
        counties_data = [
            ('Nairobi', 'nairobi', 'Capital city of Kenya', 'Nairobi, Westlands, Karen, Kileleshwa, Lavington, Parklands, Eastlands, South B, South C, Donholm, Umoja, Buruburu, Embakasi'),
            ('Mombasa', 'mombasa', 'Coastal city', 'Mombasa Island, Diani, Nyali, Bamburi, Kisauni, Changamwe, Likoni'),
            ('Kisumu', 'kisumu', 'Lake city', 'Kisumu Town, Milimani, Nyalenda, Manyatta, Kondele'),
            ('Nakuru', 'nakuru', 'Rift Valley hub', 'Nakuru Town, Lanet, Kabarak, Naivasha, Gilgil'),
            ('Kiambu', 'kiambu', 'Nairobi satellite', 'Thika, Ruiru, Kikuyu, Limuru, Juja'),
            ('Kajiado', 'kajiado', 'Southern county', 'Kitengela, Ongata Rongai, Kajiado Town, Ngong'),
            ('Machakos', 'machakos', 'Eastern county', 'Machakos Town, Athi River, Mavoko'),
            ('Uasin Gishu', 'uasin_gishu', 'Agricultural hub', 'Eldoret, Moiben, Turbo, Soy'),
        ]
        
        counties = {}
        for name, slug, desc, towns in counties_data:
            county, created = County.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slug,
                    'description': desc,
                    'main_towns': towns,
                    'is_active': True
                }
            )
            counties[name] = county
            if created:
                self.stdout.write(f'Created county: {name}')

        # Get or create amenities
        amenities_data = [
            'Swimming Pool', 'Gym', 'Security', 'Parking', 'Balcony', 
            'Garden', 'Air Conditioning', 'Elevator', 'Backup Generator',
            'Water Storage', 'Internet', 'Playground', 'Tennis Court',
            'Clubhouse', 'Jogging Track', 'BBQ Area', 'Solar Panels',
            'Borehole', 'Perimeter Fence', 'CCTV', 'Intercom',
            'Fire Safety', 'Servant Quarters', 'Study Room', 'Dining Area'
        ]
        
        amenities = {}
        for amenity_name in amenities_data:
            amenity, created = Amenity.objects.get_or_create(
                name=amenity_name,
                defaults={'is_active': True}
            )
            amenities[amenity_name] = amenity
            if created:
                self.stdout.write(f'Created amenity: {amenity_name}')

        # Get or create landlord
        landlord_user, created = User.objects.get_or_create(
            username='landlord1',
            defaults={
                'email': 'landlord@traca.co.ke',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        if created:
            landlord_user.set_password('landlord123')
            landlord_user.save()
        
        landlord, created = Landlord.objects.get_or_create(
            user=landlord_user,
            defaults={
                'phone': '+254712345678',
                'is_verified': True,
                'is_active': True
            }
        )
        if created:
            self.stdout.write('Created landlord: John Doe')

        # Property titles and descriptions
        property_templates = [
            # Nairobi Properties
            {
                'county': 'Nairobi',
                'properties': [
                    ('Modern 3-Bedroom Apartment in Westlands', 'Beautiful modern apartment in the heart of Westlands with excellent amenities and proximity to shopping centers.'),
                    ('Luxury 4-Bedroom Villa in Karen', 'Exclusive luxury villa in Karen with beautiful gardens, swimming pool, and 24-hour security.'),
                    ('Cozy 1-Bedroom Studio in Kilimani', 'Compact and affordable studio apartment perfect for students or young professionals.'),
                    ('Spacious 5-Bedroom House in Lavington', 'Elegant family home in prestigious Lavington with modern finishes and ample parking.'),
                    ('Penthouse Apartment in Kileleshwa', 'Stunning penthouse with panoramic city views and premium finishes throughout.'),
                    ('Townhouse Complex in Parklands', 'Modern townhouse complex with communal facilities and secure parking.'),
                    ('Office Space in CBD', 'Prime commercial space in Nairobi CBD perfect for businesses and startups.'),
                    ('2-Bedroom Apartment in South B', 'Affordable apartment in South B with easy access to main roads and amenities.'),
                    ('Family Home in Donholm', 'Spacious family home with large garden and modern amenities.'),
                    ('Apartment in Embakasi', 'Modern apartment near Jomo Kenyatta International Airport with great connectivity.'),
                ]
            },
            # Mombasa Properties
            {
                'county': 'Mombasa',
                'properties': [
                    ('Beachfront 2-Bedroom Apartment in Diani', 'Stunning beachfront apartment with ocean views, direct beach access, and modern amenities.'),
                    ('3-Bedroom Villa in Nyali', 'Beautiful villa in Nyali with private pool, garden, and proximity to beaches.'),
                    ('Holiday Apartment in Bamburi', 'Perfect holiday apartment with great views and access to tourist attractions.'),
                    ('Commercial Space in Mombasa Town', 'Prime commercial space in Mombasa Town center ideal for retail business.'),
                    ('Beach House in Kisauni', 'Traditional beach house with modern amenities and stunning ocean views.'),
                    ('Apartment in Likoni', 'Affordable apartment with ferry access to Mombasa Island.'),
                ]
            },
            # Kisumu Properties
            {
                'county': 'Kisumu',
                'properties': [
                    ('Lakeside 3-Bedroom House', 'Beautiful house overlooking Lake Victoria with stunning sunset views.'),
                    ('Modern Apartment in Milimani', 'Contemporary apartment in upscale Milimani neighborhood.'),
                    ('Commercial Building in Kisumu Town', 'Prime commercial space in Kisumu Town center.'),
                    ('Family Home in Manyatta', 'Spacious family home in quiet Manyatta neighborhood.'),
                    ('Student Housing near Maseno', 'Affordable student housing with easy access to universities.'),
                ]
            },
            # Nakuru Properties
            {
                'county': 'Nakuru',
                'properties': [
                    ('Farmhouse in Naivasha', 'Beautiful farmhouse with large land and stunning views of Lake Naivasha.'),
                    ('Modern House in Nakuru Town', 'Contemporary family home in Nakuru Town with modern amenities.'),
                    ('Commercial Space in Gilgil', 'Strategic commercial space along Nairobi-Nakuru highway.'),
                    ('Vacation Home in Elementaita', 'Peaceful vacation home near Lake Elementaita with beautiful gardens.'),
                    ('Apartment Complex in Kabarak', 'Modern apartment complex near Kabarak University.'),
                ]
            },
            # Kiambu Properties
            {
                'county': 'Kiambu',
                'properties': [
                    ('Modern Townhouse in Thika', 'Contemporary townhouse in Thika with modern amenities.'),
                    ('Family Home in Ruiru', 'Spacious family home in Ruiru with large compound.'),
                    ('Apartment in Limuru', 'Modern apartment in serene Limuru environment.'),
                    ('Commercial Space in Juja', 'Prime commercial space near Juja Farm and universities.'),
                    ('Luxury Villa in Kikuyu', 'Exclusive villa in Kikuyu with premium finishes and amenities.'),
                ]
            },
            # Kajiado Properties
            {
                'county': 'Kajiado',
                'properties': [
                    ('Modern House in Kitengela', 'Contemporary family home in Kitengela with modern amenities.'),
                    ('Apartment in Ongata Rongai', 'Modern apartment complex in fast-growing Ongata Rongai.'),
                    ('Villa in Ngong', 'Beautiful villa in Ngong with stunning views and modern amenities.'),
                    ('Commercial Space in Kajiado Town', 'Prime commercial space in Kajiado Town center.'),
                ]
            },
            # Machakos Properties
            {
                'county': 'Machakos',
                'properties': [
                    ('Modern House in Machakos Town', 'Contemporary family home in Machakos Town.'),
                    ('Apartment in Athi River', 'Modern apartment in Athi River industrial area.'),
                    ('Commercial Space in Mavoko', 'Strategic commercial space along Mombasa Road.'),
                    ('Family Home in Mwala', 'Spacious family home in peaceful Mwala area.'),
                ]
            },
            # Uasin Gishu Properties
            {
                'county': 'Uasin Gishu',
                'properties': [
                    ('Modern House in Eldoret', 'Contemporary family home in Eldoret with modern amenities.'),
                    ('Commercial Building in Moiben', 'Prime commercial space in growing Moiben area.'),
                    ('Farm House in Turbo', 'Beautiful farmhouse with large agricultural land.'),
                    ('Apartment Complex in Soy', 'Modern apartments near universities and colleges.'),
                ]
            },
        ]

        # Create properties
        property_count = 0
        for county_data in property_templates:
            county = counties[county_data['county']]
            for title, description in county_data['properties']:
                # Random property details
                property_type = random.choice(['sale', 'rent'])
                
                # Price based on property type and county
                if property_type == 'sale':
                    if county.name in ['Nairobi', 'Kiambu']:
                        price = random.randint(5000000, 50000000)
                    elif county.name in ['Mombasa']:
                        price = random.randint(3000000, 30000000)
                    else:
                        price = random.randint(2000000, 15000000)
                else:
                    if county.name in ['Nairobi', 'Kiambu']:
                        price = random.randint(25000, 200000)
                    elif county.name in ['Mombasa']:
                        price = random.randint(15000, 120000)
                    else:
                        price = random.randint(10000, 80000)

                # Random property details
                bedrooms = random.choice([1, 2, 3, 4, 5])
                bathrooms = random.choice([1, 2, 3, 4])
                parking_slots = random.choice([0, 1, 2, 3, 4])
                area = round(random.uniform(45, 500), 1)
                
                # Create property
                property_obj, created = Property.objects.get_or_create(
                    title=title,
                    defaults={
                        'county': county,
                        'property_type': property_type,
                        'price': Decimal(str(price)),
                        'area': Decimal(str(area)),
                        'bedrooms': bedrooms,
                        'bathrooms': bathrooms,
                        'parking_slots': parking_slots,
                        'is_furnished': random.choice([True, False]),
                        'pet_friendly': random.choice([True, False]),
                        'near_school': random.choice([True, False]),
                        'landlord': landlord,
                        'is_verified': True,
                        'description': description,
                        'town': random.choice(county.main_towns.split(', ')),
                    }
                )
                
                if created:
                    # Add random amenities (3-8 per property)
                    property_amenities = random.sample(list(amenities.values()), random.randint(3, 8))
                    property_obj.amenities.add(*property_amenities)
                    
                    property_count += 1
                    self.stdout.write(f'Created property: {title}')

        self.stdout.write(self.style.SUCCESS(f'Successfully created {property_count} properties!'))
        self.stdout.write(f'Total properties in database: {Property.objects.count()}')
        
        # Show statistics
        total_properties = Property.objects.count()
        sale_properties = Property.objects.filter(property_type='sale').count()
        rent_properties = Property.objects.filter(property_type='rent').count()
        
        self.stdout.write(f'\n📊 Property Statistics:')
        self.stdout.write(f'   Total Properties: {total_properties}')
        self.stdout.write(f'   For Sale: {sale_properties}')
        self.stdout.write(f'   For Rent: {rent_properties}')
        self.stdout.write(f'   Counties Covered: {County.objects.count()}')
        self.stdout.write(f'   Amenities Available: {Amenity.objects.count()}')
