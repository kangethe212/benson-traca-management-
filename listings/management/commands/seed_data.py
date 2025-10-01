from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import County, Property, ManagementRequest, PropertyMedia


class Command(BaseCommand):
    help = 'Seed the database with sample data for Traca Management Services'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with sample data...')
        
        # Create counties
        counties_data = [
            {'name': 'Nairobi', 'slug': 'nairobi', 'description': 'Capital city of Kenya'},
            {'name': 'Kiambu', 'slug': 'kiambu', 'description': 'Kiambu County'},
            {'name': 'Machakos', 'slug': 'machakos', 'description': 'Machakos County'},
            {'name': "Murang'a", 'slug': 'muranga', 'description': "Murang'a County"},
            {'name': 'Kajiado', 'slug': 'kajiado', 'description': 'Kajiado County'},
            {'name': 'Nyandarua', 'slug': 'nyandarua', 'description': 'Nyandarua County'},
        ]
        
        counties = {}
        for county_data in counties_data:
            county, created = County.objects.get_or_create(
                slug=county_data['slug'],
                defaults=county_data
            )
            counties[county.slug] = county
            if created:
                self.stdout.write(f'Created county: {county.name}')
        
        # Create sample properties
        properties_data = [
            {
                'title': 'Modern 3-Bedroom Apartment in Westlands',
                'property_type': 'sale',
                'county': counties['nairobi'],
                'price': 15000000,
                'bedrooms': 3,
                'bathrooms': 2,
                'parking_slots': 2,
                'area': 1200,
                'description': 'Beautiful modern apartment in the heart of Westlands with stunning city views.',
                'is_verified': True
            },
            {
                'title': 'Spacious 4-Bedroom House in Runda',
                'property_type': 'sale',
                'county': counties['nairobi'],
                'price': 25000000,
                'bedrooms': 4,
                'bathrooms': 3,
                'parking_slots': 3,
                'area': 2000,
                'description': 'Luxurious family home in exclusive Runda estate with garden and pool.',
                'is_verified': True
            },
            {
                'title': '2-Bedroom Apartment for Rent in Kilimani',
                'property_type': 'rent',
                'county': counties['nairobi'],
                'price': 80000,
                'bedrooms': 2,
                'bathrooms': 2,
                'parking_slots': 1,
                'area': 800,
                'description': 'Furnished apartment in Kilimani with modern amenities and security.',
                'is_verified': True
            },
            {
                'title': 'Commercial Office Space in CBD',
                'property_type': 'rent',
                'county': counties['nairobi'],
                'price': 120000,
                'bedrooms': 0,
                'bathrooms': 2,
                'parking_slots': 5,
                'area': 1500,
                'description': 'Prime office space in Nairobi CBD, perfect for business operations.',
                'is_verified': False
            },
            {
                'title': '3-Bedroom House in Thika',
                'property_type': 'sale',
                'county': counties['kiambu'],
                'price': 8000000,
                'bedrooms': 3,
                'bathrooms': 2,
                'parking_slots': 2,
                'area': 1000,
                'description': 'Affordable family home in Thika with good transport links.',
                'is_verified': True
            },
            {
                'title': 'Land for Sale in Machakos',
                'property_type': 'sale',
                'county': counties['machakos'],
                'price': 5000000,
                'bedrooms': 0,
                'bathrooms': 0,
                'parking_slots': 0,
                'area': 5000,
                'description': 'Prime land in Machakos town, perfect for residential or commercial development.',
                'is_verified': False
            }
        ]
        
        for prop_data in properties_data:
            property_obj, created = Property.objects.get_or_create(
                title=prop_data['title'],
                defaults=prop_data
            )
            if created:
                self.stdout.write(f'Created property: {property_obj.title}')
        
        # Create sample management requests
        management_requests_data = [
            {
                'property': Property.objects.filter(property_type='rent').first(),
                'landlord_name': 'John Mwangi',
                'landlord_contact': '+254700123456',
                'rent_amount': 80000,
                'service_terms': 'Need help managing my rental property in Kilimani. Looking for tenant screening, rent collection, and maintenance coordination.',
                'status': 'pending'
            },
            {
                'property': Property.objects.filter(property_type='rent').last(),
                'landlord_name': 'Mary Wanjiku',
                'landlord_contact': '+254700789012',
                'rent_amount': 120000,
                'service_terms': 'Commercial property management needed for office space in CBD. Require professional management services.',
                'status': 'approved'
            }
        ]
        
        for req_data in management_requests_data:
            if req_data['property']:  # Only create if property exists
                request_obj, created = ManagementRequest.objects.get_or_create(
                    landlord_name=req_data['landlord_name'],
                    property=req_data['property'],
                    defaults=req_data
                )
                if created:
                    self.stdout.write(f'Created management request: {request_obj.landlord_name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with sample data!')
        )
        self.stdout.write(f'Created {County.objects.count()} counties')
        self.stdout.write(f'Created {Property.objects.count()} properties')
        self.stdout.write(f'Created {ManagementRequest.objects.count()} management requests')
