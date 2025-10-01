from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import transaction
import os

from listings.models import County, Agent, Amenity, Property, PropertyMedia, Testimonial


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Starting database seeding...')
        
        with transaction.atomic():
            # Create counties
            self.create_counties()
            
            # Create agent user
            agent = self.create_agent()
            
            # Create amenities
            amenities = self.create_amenities()
            
            # Create properties
            properties = self.create_properties(agent, amenities)
            
            # Create testimonials
            self.create_testimonials(properties)
            
        self.stdout.write(
            self.style.SUCCESS('Database seeding completed successfully!')
        )

    def create_counties(self):
        """Create the six counties where Traca operates"""
        counties_data = [
            {'name': 'Nairobi', 'description': 'Kenya\'s capital and largest city'},
            {'name': 'Kiambu', 'description': 'Fast-growing county with prime residential areas'},
            {'name': 'Machakos', 'description': 'Emerging real estate market with great potential'},
            {'name': 'Murang\'a', 'description': 'Agricultural county with growing urban centers'},
            {'name': 'Kajiado', 'description': 'Gateway to the south with expanding developments'},
            {'name': 'Nyandarua', 'description': 'Highland county with scenic properties'},
        ]
        
        counties = []
        for data in counties_data:
            county, created = County.objects.get_or_create(
                name=data['name'],
                defaults={
                    'slug': data['name'].lower().replace(' ', '-').replace('\'', ''),
                    'description': data['description'],
                    'is_active': True
                }
            )
            counties.append(county)
            if created:
                self.stdout.write(f'Created county: {county.name}')
        
        return counties

    def create_agent(self):
        """Create a sample agent user"""
        # Create user
        user, created = User.objects.get_or_create(
            username='agent1',
            defaults={
                'email': 'agent@tracamanagement.co.ke',
                'first_name': 'John',
                'last_name': 'Mwangi',
                'is_staff': True,
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(f'Created user: {user.username}')
        
        # Create agent profile
        agent, created = Agent.objects.get_or_create(
            user=user,
            defaults={
                'phone': '+254 700 000 001',
                'bio': 'Experienced real estate agent with over 10 years in the Kenyan market.',
                'license_number': 'REA001',
                'is_active': True,
                'is_verified': True
            }
        )
        
        if created:
            self.stdout.write(f'Created agent: {agent.full_name}')
        
        return agent

    def create_amenities(self):
        """Create sample amenities"""
        amenities_data = [
            {'name': 'Swimming Pool', 'icon': 'fas fa-swimming-pool'},
            {'name': 'Gym', 'icon': 'fas fa-dumbbell'},
            {'name': 'Parking', 'icon': 'fas fa-car'},
            {'name': 'Security', 'icon': 'fas fa-shield-alt'},
            {'name': 'Garden', 'icon': 'fas fa-seedling'},
            {'name': 'Balcony', 'icon': 'fas fa-home'},
            {'name': 'Air Conditioning', 'icon': 'fas fa-snowflake'},
            {'name': 'WiFi', 'icon': 'fas fa-wifi'},
        ]
        
        amenities = []
        for data in amenities_data:
            amenity, created = Amenity.objects.get_or_create(
                name=data['name'],
                defaults={
                    'icon': data['icon'],
                    'description': f'Property includes {data["name"].lower()}',
                    'is_active': True
                }
            )
            amenities.append(amenity)
            if created:
                self.stdout.write(f'Created amenity: {amenity.name}')
        
        return amenities

    def create_properties(self, agent, amenities):
        """Create sample properties"""
        properties_data = [
            {
                'title': 'Modern 3-Bedroom Apartment in Westlands',
                'description': 'Beautiful modern apartment in the heart of Westlands with stunning city views.',
                'property_type': 'apartment',
                'price': 25000000,
                'area': 1200,
                'bedrooms': 3,
                'bathrooms': 2,
                'bathtubs': 1,
                'washrooms': 1,
                'parking_slots': 2,
                  'county': 'Nairobi',
                  'location': 'Westlands',
                  'address': 'Westlands Business District, Nairobi',
                  'is_featured': True,
                  'is_verified': True,
                  'is_furnished': True,
                  'pet_friendly': False,
                  'near_school': True,
                  'amenities': ['Swimming Pool', 'Gym', 'Parking', 'Security']
            },
            {
                'title': 'Luxury 4-Bedroom Villa in Karen',
                'description': 'Spacious family villa in the prestigious Karen area with large garden.',
                'property_type': 'house',
                'price': 45000000,
                'area': 2500,
                'bedrooms': 4,
                'bathrooms': 3,
                'bathtubs': 2,
                'washrooms': 1,
                'parking_slots': 3,
                  'county': 'Nairobi',
                  'location': 'Karen',
                  'address': 'Karen Road, Nairobi',
                  'is_featured': True,
                  'is_verified': True,
                  'is_furnished': False,
                  'pet_friendly': True,
                  'near_school': True,
                  'amenities': ['Garden', 'Parking', 'Security', 'Balcony']
            },
            {
                'title': 'Commercial Office Space in Kiambu',
                'description': 'Prime commercial office space in Kiambu town center.',
                'property_type': 'commercial',
                'price': 15000000,
                'area': 800,
                'bedrooms': 0,
                'bathrooms': 2,
                'bathtubs': 0,
                'washrooms': 2,
                'parking_slots': 5,
                  'county': 'Kiambu',
                  'location': 'Kiambu Town',
                  'address': 'Kiambu Town Center',
                  'is_featured': False,
                  'is_verified': True,
                  'is_furnished': True,
                  'pet_friendly': False,
                  'near_school': False,
                  'amenities': ['Parking', 'Security', 'WiFi']
            },
            {
                'title': '2-Bedroom Apartment in Machakos',
                'description': 'Affordable 2-bedroom apartment in growing Machakos area.',
                'property_type': 'apartment',
                'price': 8000000,
                'area': 900,
                'bedrooms': 2,
                'bathrooms': 2,
                'bathtubs': 1,
                'washrooms': 1,
                'parking_slots': 1,
                  'county': 'Machakos',
                  'location': 'Machakos Town',
                  'address': 'Machakos Town Center',
                  'is_featured': False,
                  'is_furnished': False,
                  'pet_friendly': True,
                  'near_school': True,
                  'amenities': ['Parking', 'Security']
            },
            {
                'title': 'Land for Sale in Murang\'a',
                'description': 'Prime land for residential development in Murang\'a.',
                'property_type': 'land',
                'price': 5000000,
                'area': 5000,
                'bedrooms': 0,
                'bathrooms': 0,
                'bathtubs': 0,
                'washrooms': 0,
                'parking_slots': 0,
                  'county': 'Murang\'a',
                  'location': 'Murang\'a Town',
                  'address': 'Murang\'a County',
                  'is_featured': False,
                  'is_furnished': False,
                  'pet_friendly': False,
                  'near_school': False,
                  'amenities': []
            },
            {
                'title': 'Office Space in Kajiado',
                'description': 'Modern office space in Kajiado town with great potential.',
                'property_type': 'office',
                'price': 12000000,
                'area': 600,
                'bedrooms': 0,
                'bathrooms': 1,
                'bathtubs': 0,
                'washrooms': 1,
                'parking_slots': 3,
                'county': 'Kajiado',
                'location': 'Kajiado Town',
                'address': 'Kajiado Town Center',
                'is_featured': False,
                'is_furnished': True,
                'pet_friendly': False,
                'near_school': False,
                'amenities': ['Parking', 'Security', 'WiFi']
            },
        ]
        
        properties = []
        for data in properties_data:
            county = County.objects.get(name=data['county'])
            property_obj, created = Property.objects.get_or_create(
                title=data['title'],
                defaults={
                    'description': data['description'],
                    'property_type': data['property_type'],
                    'price': data['price'],
                    'area': data['area'],
                    'bedrooms': data['bedrooms'],
                    'bathrooms': data['bathrooms'],
                    'bathtubs': data['bathtubs'],
                    'washrooms': data['washrooms'],
                    'parking_slots': data['parking_slots'],
                    'county': county,
                    'location': data['location'],
                    'address': data['address'],
                    'agent': agent,
                    'is_featured': data['is_featured'],
                    'is_verified': data.get('is_verified', False),
                    'is_furnished': data.get('is_furnished', False),
                    'pet_friendly': data.get('pet_friendly', False),
                    'near_school': data.get('near_school', False),
                    'published': True,
                }
            )
            
            if created:
                # Add amenities
                for amenity_name in data['amenities']:
                    try:
                        amenity = Amenity.objects.get(name=amenity_name)
                        property_obj.amenities.add(amenity)
                    except Amenity.DoesNotExist:
                        pass
                
                properties.append(property_obj)
                self.stdout.write(f'Created property: {property_obj.title}')
        
        return properties

    def create_testimonials(self, properties):
        """Create sample testimonials"""
        testimonials_data = [
            {
                'name': 'Sarah Mwangi',
                'role': 'Property Buyer',
                'content': 'Traca Management Services made finding my dream home in Nairobi effortless. Their team was professional, responsive, and truly understood my needs. Highly recommended!',
                'rating': 5,
                'property': properties[0] if properties else None,
                'is_featured': True,
                'is_approved': True,
            },
            {
                'name': 'James Kimani',
                'role': 'Property Seller',
                'content': 'Listing my commercial property with Traca was the best decision. They handled everything from marketing to negotiations, securing a great deal in record time.',
                'rating': 5,
                'property': properties[2] if len(properties) > 2 else None,
                'is_featured': True,
                'is_approved': True,
            },
            {
                'name': 'Grace Wanjiku',
                'role': 'Landlord',
                'content': 'Their property management services are top-notch. I no longer worry about my rental units; Traca ensures everything runs smoothly and tenants are happy.',
                'rating': 5,
                'property': properties[1] if len(properties) > 1 else None,
                'is_featured': False,
                'is_approved': True,
            },
        ]
        
        for data in testimonials_data:
            testimonial, created = Testimonial.objects.get_or_create(
                name=data['name'],
                content=data['content'],
                defaults={
                    'role': data['role'],
                    'rating': data['rating'],
                    'property': data['property'],
                    'is_featured': data['is_featured'],
                    'is_approved': data['is_approved'],
                }
            )
            
            if created:
                self.stdout.write(f'Created testimonial: {testimonial.name}')
