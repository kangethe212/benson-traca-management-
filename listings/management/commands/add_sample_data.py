from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Property, County, PropertyMedia, Testimonial
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Add sample data to showcase the property features'

    def handle(self, *args, **options):
        self.stdout.write('Adding sample data...')
        
        # Get or create counties
        counties_data = [
            {'name': 'Nairobi', 'slug': 'nairobi', 'description': 'Kenya\'s capital city and commercial hub'},
            {'name': 'Kiambu', 'slug': 'kiambu', 'description': 'Fast-growing county with modern developments'},
            {'name': 'Machakos', 'slug': 'machakos', 'description': 'Emerging real estate market with great potential'},
            {'name': 'Kajiado', 'slug': 'kajiado', 'description': 'Prime location for luxury properties'},
            {'name': 'Murang\'a', 'slug': 'muranga', 'description': 'Beautiful county with scenic properties'},
            {'name': 'Nakuru', 'slug': 'nakuru', 'description': 'Major town with diverse property options'},
        ]
        
        counties = {}
        for county_data in counties_data:
            county, created = County.objects.get_or_create(
                slug=county_data['slug'],
                defaults=county_data
            )
            counties[county_data['slug']] = county
            if created:
                self.stdout.write(f'Created county: {county.name}')

        # Sample properties data
        properties_data = [
            {
                'title': 'Luxury 4-Bedroom Villa in Karen',
                'property_type': 'sale',
                'county': counties['nairobi'],
                'price': Decimal('25000000'),
                'area': Decimal('5000'),
                'bedrooms': 4,
                'bathrooms': 3,
                'parking_slots': 2,
                'description': 'Stunning modern villa in the prestigious Karen area. Features include a swimming pool, landscaped garden, and modern finishes throughout.',
                'is_verified': True,
            },
            {
                'title': 'Modern 3-Bedroom Apartment in Westlands',
                'property_type': 'rent',
                'county': counties['nairobi'],
                'price': Decimal('120000'),
                'area': Decimal('1800'),
                'bedrooms': 3,
                'bathrooms': 2,
                'parking_slots': 1,
                'description': 'Contemporary apartment in the heart of Westlands. Close to shopping malls, restaurants, and business district.',
                'is_verified': True,
            },
            {
                'title': 'Spacious 5-Bedroom Family Home in Runda',
                'property_type': 'sale',
                'county': counties['nairobi'],
                'price': Decimal('35000000'),
                'area': Decimal('8000'),
                'bedrooms': 5,
                'bathrooms': 4,
                'parking_slots': 3,
                'description': 'Perfect family home in the exclusive Runda estate. Features a large garden, servant quarters, and modern amenities.',
                'is_verified': True,
            },
            {
                'title': 'Cozy 2-Bedroom Apartment in Kilimani',
                'property_type': 'rent',
                'county': counties['nairobi'],
                'price': Decimal('80000'),
                'area': Decimal('1200'),
                'bedrooms': 2,
                'bathrooms': 2,
                'parking_slots': 1,
                'description': 'Well-maintained apartment in Kilimani. Perfect for young professionals or small families.',
                'is_verified': False,
            },
            {
                'title': 'Executive Office Space in Upper Hill',
                'property_type': 'rent',
                'county': counties['nairobi'],
                'price': Decimal('200000'),
                'area': Decimal('3000'),
                'bedrooms': 0,
                'bathrooms': 2,
                'parking_slots': 4,
                'description': 'Premium office space in the business district. Fully furnished and ready for immediate occupation.',
                'is_verified': True,
            },
            {
                'title': 'Beautiful 3-Bedroom House in Thika',
                'property_type': 'sale',
                'county': counties['kiambu'],
                'price': Decimal('8500000'),
                'area': Decimal('3000'),
                'bedrooms': 3,
                'bathrooms': 2,
                'parking_slots': 2,
                'description': 'Charming house in Thika with a beautiful garden. Great investment opportunity in a growing area.',
                'is_verified': True,
            },
            {
                'title': 'Modern 4-Bedroom Villa in Athi River',
                'property_type': 'sale',
                'county': counties['machakos'],
                'price': Decimal('12000000'),
                'area': Decimal('4000'),
                'bedrooms': 4,
                'bathrooms': 3,
                'parking_slots': 2,
                'description': 'Contemporary villa in Athi River with modern amenities and great connectivity to Nairobi.',
                'is_verified': True,
            },
            {
                'title': 'Luxury 6-Bedroom Mansion in Kajiado',
                'property_type': 'sale',
                'county': counties['kajiado'],
                'price': Decimal('45000000'),
                'area': Decimal('10000'),
                'bedrooms': 6,
                'bathrooms': 5,
                'parking_slots': 4,
                'description': 'Magnificent mansion with panoramic views. Features include a tennis court, swimming pool, and guest house.',
                'is_verified': True,
            },
            {
                'title': 'Affordable 2-Bedroom House in Murang\'a',
                'property_type': 'sale',
                'county': counties['muranga'],
                'price': Decimal('3500000'),
                'area': Decimal('2000'),
                'bedrooms': 2,
                'bathrooms': 1,
                'parking_slots': 1,
                'description': 'Affordable starter home in a quiet neighborhood. Perfect for first-time buyers.',
                'is_verified': False,
            },
            {
                'title': 'Commercial Plot in Nakuru CBD',
                'property_type': 'sale',
                'county': counties['nakuru'],
                'price': Decimal('15000000'),
                'area': Decimal('5000'),
                'bedrooms': 0,
                'bathrooms': 0,
                'parking_slots': 0,
                'description': 'Prime commercial plot in Nakuru CBD. Ideal for office buildings, retail, or mixed-use development.',
                'is_verified': True,
            },
        ]

        # Create properties
        for prop_data in properties_data:
            property_obj, created = Property.objects.get_or_create(
                title=prop_data['title'],
                defaults=prop_data
            )
            if created:
                self.stdout.write(f'Created property: {property_obj.title}')

        # Add some testimonials
        testimonials_data = [
            {
                'name': 'Sarah Mwangi',
                'role': 'Property Buyer',
                'content': 'Traca Management Services made finding my dream home in Nairobi effortless. Their team was professional, responsive, and truly understood my needs.',
                'rating': 5,
                'is_featured': True,
                'is_approved': True,
            },
            {
                'name': 'James Kimani',
                'role': 'Property Seller',
                'content': 'Listing my commercial property with Traca was the best decision. They handled everything from marketing to negotiations, securing a great deal.',
                'rating': 5,
                'is_featured': True,
                'is_approved': True,
            },
            {
                'name': 'Grace Wanjiku',
                'role': 'Landlord',
                'content': 'Their property management services are top-notch. I no longer worry about my rental units; Traca ensures everything runs smoothly.',
                'rating': 5,
                'is_featured': True,
                'is_approved': True,
            },
            {
                'name': 'David Ochieng',
                'role': 'Investor',
                'content': 'Excellent investment advisory services. Traca helped me identify profitable opportunities and maximize my returns.',
                'rating': 4,
                'is_featured': False,
                'is_approved': True,
            },
            {
                'name': 'Mary Njeri',
                'role': 'Tenant',
                'content': 'Great experience finding my rental property. The team was helpful and the process was smooth and transparent.',
                'rating': 5,
                'is_featured': False,
                'is_approved': True,
            },
        ]

        for testimonial_data in testimonials_data:
            testimonial, created = Testimonial.objects.get_or_create(
                name=testimonial_data['name'],
                defaults=testimonial_data
            )
            if created:
                self.stdout.write(f'Created testimonial: {testimonial.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully added sample data!')
        )
        self.stdout.write(f'Total Counties: {County.objects.count()}')
        self.stdout.write(f'Total Properties: {Property.objects.count()}')
        self.stdout.write(f'Total Testimonials: {Testimonial.objects.count()}')
