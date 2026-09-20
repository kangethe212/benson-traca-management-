from django.core.management.base import BaseCommand
from listings.models import County, Property, Amenity, Landlord, Agent
from django.contrib.auth.models import User
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample data for TRACA Management System'

    def handle(self, *args, **options):
        # Create counties
        counties_data = [
            ('Nairobi', 'nairobi', 'Capital city of Kenya', 'Nairobi, Westlands, Karen, Kileleshwa'),
            ('Mombasa', 'mombasa', 'Coastal city', 'Mombasa Island, Diani, Nyali'),
            ('Kisumu', 'kisumu', 'Lake city', 'Kisumu Town, Milimani, Nyalenda'),
            ('Nakuru', 'nakuru', 'Rift Valley hub', 'Nakuru Town, Lanet, Kabarak'),
        ]
        
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
            if created:
                self.stdout.write(f'Created county: {name}')

        # Create amenities
        amenities_data = [
            'Swimming Pool', 'Gym', 'Security', 'Parking', 'Balcony', 
            'Garden', 'Air Conditioning', 'Elevator', 'Backup Generator',
            'Water Storage', 'Internet', 'Playground'
        ]
        
        for amenity_name in amenities_data:
            amenity, created = Amenity.objects.get_or_create(
                name=amenity_name,
                defaults={'is_active': True}
            )
            if created:
                self.stdout.write(f'Created amenity: {amenity_name}')

        # Create admin user if not exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@traca.co.ke',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user: admin/admin123')

        # Create sample landlord
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

        # Create sample properties
        properties_data = [
            {
                'title': 'Modern 3-Bedroom Apartment in Westlands',
                'property_type': 'rent',
                'county': County.objects.get(name='Nairobi'),
                'town': 'Westlands',
                'price': Decimal('85000.00'),
                'area': Decimal('120.50'),
                'bedrooms': 3,
                'bathrooms': 2,
                'parking_slots': 1,
                'is_furnished': True,
                'pet_friendly': False,
                'near_school': True,
                'landlord': landlord,
                'is_verified': True,
                'description': 'Beautiful modern apartment in the heart of Westlands with excellent amenities and proximity to shopping centers.'
            },
            {
                'title': 'Luxury 4-Bedroom Villa in Karen',
                'property_type': 'sale',
                'county': County.objects.get(name='Nairobi'),
                'town': 'Karen',
                'price': Decimal('25000000.00'),
                'area': Decimal('450.00'),
                'bedrooms': 4,
                'bathrooms': 3,
                'parking_slots': 2,
                'is_furnished': False,
                'pet_friendly': True,
                'near_school': True,
                'landlord': landlord,
                'is_verified': True,
                'description': 'Exclusive luxury villa in Karen with beautiful gardens, swimming pool, and 24-hour security.'
            },
            {
                'title': 'Beachfront 2-Bedroom Apartment in Diani',
                'property_type': 'rent',
                'county': County.objects.get(name='Mombasa'),
                'town': 'Diani',
                'price': Decimal('65000.00'),
                'area': Decimal('95.00'),
                'bedrooms': 2,
                'bathrooms': 1,
                'parking_slots': 1,
                'is_furnished': True,
                'pet_friendly': True,
                'near_school': False,
                'landlord': landlord,
                'is_verified': True,
                'description': 'Stunning beachfront apartment with ocean views, direct beach access, and modern amenities.'
            },
            {
                'title': 'Commercial Space in Nakuru Town',
                'property_type': 'sale',
                'county': County.objects.get(name='Nakuru'),
                'town': 'Nakuru Town',
                'price': Decimal('8500000.00'),
                'area': Decimal('200.00'),
                'bedrooms': 0,
                'bathrooms': 2,
                'parking_slots': 5,
                'is_furnished': False,
                'pet_friendly': False,
                'near_school': False,
                'landlord': landlord,
                'is_verified': True,
                'description': 'Prime commercial space in Nakuru Town center, ideal for office or retail business.'
            },
            {
                'title': 'Cozy 1-Bedroom Studio in Kisumu',
                'property_type': 'rent',
                'county': County.objects.get(name='Kisumu'),
                'town': 'Kisumu Town',
                'price': Decimal('25000.00'),
                'area': Decimal('45.00'),
                'bedrooms': 1,
                'bathrooms': 1,
                'parking_slots': 0,
                'is_furnished': True,
                'pet_friendly': False,
                'near_school': True,
                'landlord': landlord,
                'is_verified': True,
                'description': 'Compact and affordable studio apartment perfect for students or young professionals.'
            }
        ]

        for prop_data in properties_data:
            property_obj, created = Property.objects.get_or_create(
                title=prop_data['title'],
                defaults=prop_data
            )
            if created:
                # Add some amenities to the property
                amenities = Amenity.objects.all()[:5]  # Add first 5 amenities
                property_obj.amenities.add(*amenities)
                self.stdout.write(f'Created property: {property_obj.title}')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write('Admin login: admin/admin123')
