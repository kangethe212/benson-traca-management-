from django.core.management.base import BaseCommand
from listings.models import County, Property, PropertyMedia
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Add sample properties for different counties to showcase the system'

    def handle(self, *args, **options):
        self.stdout.write('Adding sample properties for different counties...')
        
        # Get some counties to work with
        counties = County.objects.filter(is_active=True)[:10]  # Get first 10 counties
        
        if not counties:
            self.stdout.write(self.style.ERROR('No active counties found. Please run add_all_counties first.'))
            return
        
        # Sample property data for different counties
        property_data = [
            # Nairobi properties
            {
                'title': 'Modern 3-Bedroom Apartment in Westlands',
                'description': 'Beautiful modern apartment in the heart of Westlands with stunning city views. Features include granite countertops, modern appliances, and a private balcony.',
                'property_type': 'sale',
                'price': Decimal('8500000.00'),
                'bedrooms': 3,
                'bathrooms': 2,
                'area': Decimal('120.00'),
                'parking_slots': 1,
                'county_slug': 'nairobi'
            },
            {
                'title': 'Luxury Villa in Karen',
                'description': 'Spacious 5-bedroom villa in Karen with landscaped gardens, swimming pool, and modern amenities. Perfect for families seeking luxury living.',
                'property_type': 'sale',
                'price': Decimal('25000000.00'),
                'bedrooms': 5,
                'bathrooms': 4,
                'area': Decimal('450.00'),
                'parking_slots': 3,
                'county_slug': 'nairobi'
            },
            {
                'title': '2-Bedroom Apartment for Rent in Kilimani',
                'description': 'Furnished 2-bedroom apartment in Kilimani with modern amenities, 24/7 security, and close proximity to shopping centers and restaurants.',
                'property_type': 'rent',
                'price': Decimal('120000.00'),
                'bedrooms': 2,
                'bathrooms': 2,
                'area': Decimal('85.00'),
                'parking_slots': 1,
                'county_slug': 'nairobi'
            },
            
            # Kiambu properties
            {
                'title': '4-Bedroom House in Thika',
                'description': 'Spacious family home in Thika with a large compound, modern kitchen, and ample parking space. Close to schools and shopping centers.',
                'property_type': 'sale',
                'price': Decimal('12000000.00'),
                'bedrooms': 4,
                'bathrooms': 3,
                'area': Decimal('200.00'),
                'parking_slots': 2,
                'county_slug': 'kiambu'
            },
            {
                'title': '3-Bedroom Apartment in Ruiru',
                'description': 'Modern apartment in Ruiru with excellent connectivity to Nairobi. Features include fitted kitchen, modern bathrooms, and security.',
                'property_type': 'rent',
                'price': Decimal('45000.00'),
                'bedrooms': 3,
                'bathrooms': 2,
                'area': Decimal('110.00'),
                'parking_slots': 1,
                'county_slug': 'kiambu'
            },
            
            # Mombasa properties
            {
                'title': 'Beachfront Villa in Nyali',
                'description': 'Luxury beachfront villa in Nyali with direct beach access, infinity pool, and panoramic ocean views. Perfect for vacation rentals.',
                'property_type': 'sale',
                'price': Decimal('35000000.00'),
                'bedrooms': 6,
                'bathrooms': 5,
                'area': Decimal('600.00'),
                'parking_slots': 4,
                'county_slug': 'mombasa'
            },
            {
                'title': '2-Bedroom Apartment in Mombasa CBD',
                'description': 'Modern apartment in Mombasa CBD with city views, modern amenities, and close to business district and port.',
                'property_type': 'rent',
                'price': Decimal('80000.00'),
                'bedrooms': 2,
                'bathrooms': 2,
                'area': Decimal('90.00'),
                'parking_slots': 1,
                'county_slug': 'mombasa'
            },
            
            # Nakuru properties
            {
                'title': '3-Bedroom House in Nakuru Town',
                'description': 'Well-maintained family house in Nakuru with a garden, modern kitchen, and good security. Close to schools and hospitals.',
                'property_type': 'sale',
                'price': Decimal('6500000.00'),
                'bedrooms': 3,
                'bathrooms': 2,
                'area': Decimal('150.00'),
                'parking_slots': 2,
                'county_slug': 'nakuru'
            },
            {
                'title': 'Commercial Property in Naivasha',
                'description': 'Prime commercial property in Naivasha suitable for office space or retail business. High foot traffic area with good visibility.',
                'property_type': 'sale',
                'price': Decimal('15000000.00'),
                'bedrooms': 0,
                'bathrooms': 2,
                'area': Decimal('300.00'),
                'parking_slots': 5,
                'county_slug': 'nakuru'
            },
            
            # Kisumu properties
            {
                'title': '4-Bedroom House in Kisumu',
                'description': 'Spacious family home in Kisumu with lake views, modern amenities, and a large compound. Perfect for families.',
                'property_type': 'sale',
                'price': Decimal('8000000.00'),
                'bedrooms': 4,
                'bathrooms': 3,
                'area': Decimal('180.00'),
                'parking_slots': 2,
                'county_slug': 'kisumu'
            },
            {
                'title': '2-Bedroom Apartment in Kisumu CBD',
                'description': 'Modern apartment in Kisumu CBD with city views and modern amenities. Close to business district and shopping centers.',
                'property_type': 'rent',
                'price': Decimal('35000.00'),
                'bedrooms': 2,
                'bathrooms': 2,
                'area': Decimal('80.00'),
                'parking_slots': 1,
                'county_slug': 'kisumu'
            },
            
            # Eldoret properties
            {
                'title': '5-Bedroom House in Eldoret',
                'description': 'Large family house in Eldoret with a spacious compound, modern kitchen, and excellent security. Close to schools and hospitals.',
                'property_type': 'sale',
                'price': Decimal('9500000.00'),
                'bedrooms': 5,
                'bathrooms': 4,
                'area': Decimal('250.00'),
                'parking_slots': 3,
                'county_slug': 'uasin-gishu'
            },
            {
                'title': '3-Bedroom Apartment in Eldoret',
                'description': 'Modern apartment in Eldoret with excellent amenities and security. Close to university and business district.',
                'property_type': 'rent',
                'price': Decimal('40000.00'),
                'bedrooms': 3,
                'bathrooms': 2,
                'area': Decimal('100.00'),
                'parking_slots': 1,
                'county_slug': 'uasin-gishu'
            },
        ]
        
        created_count = 0
        
        for prop_data in property_data:
            try:
                county = County.objects.get(slug=prop_data['county_slug'])
                
                # Create the property
                property_obj = Property.objects.create(
                    title=prop_data['title'],
                    description=prop_data['description'],
                    property_type=prop_data['property_type'],
                    county=county,
                    price=prop_data['price'],
                    bedrooms=prop_data['bedrooms'],
                    bathrooms=prop_data['bathrooms'],
                    area=prop_data['area'],
                    parking_slots=prop_data['parking_slots'],
                    is_verified=True,  # Mark as verified for display
                )
                
                created_count += 1
                self.stdout.write(f'Created property: {property_obj.title} in {county.name}')
                
            except County.DoesNotExist:
                self.stdout.write(f'County with slug {prop_data["county_slug"]} not found, skipping property: {prop_data["title"]}')
                continue
            except Exception as e:
                self.stdout.write(f'Error creating property {prop_data["title"]}: {str(e)}')
                continue
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} properties!')
        )
        self.stdout.write(f'Total Properties: {Property.objects.count()}')
        self.stdout.write(f'Verified Properties: {Property.objects.filter(is_verified=True).count()}')
