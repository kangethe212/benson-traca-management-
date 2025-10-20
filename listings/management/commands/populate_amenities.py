from django.core.management.base import BaseCommand
from listings.models import Amenity


class Command(BaseCommand):
    help = 'Populates the database with common property amenities'

    def handle(self, *args, **kwargs):
        amenities_data = [
            # Security & Safety
            {
                'name': '24/7 Security',
                'icon': 'fa-shield-alt',
                'description': 'Round-the-clock security personnel and surveillance'
            },
            {
                'name': 'CCTV Surveillance',
                'icon': 'fa-video',
                'description': 'Comprehensive CCTV camera coverage'
            },
            {
                'name': 'Secure Parking',
                'icon': 'fa-car',
                'description': 'Gated and monitored parking facility'
            },
            {
                'name': 'Electric Fence',
                'icon': 'fa-bolt',
                'description': 'Perimeter electric fencing for added security'
            },
            {
                'name': 'Fire Safety System',
                'icon': 'fa-fire-extinguisher',
                'description': 'Fire alarms, extinguishers, and emergency exits'
            },
            
            # Utilities & Infrastructure
            {
                'name': 'High-Speed WiFi',
                'icon': 'fa-wifi',
                'description': 'High-speed internet connectivity throughout the property'
            },
            {
                'name': 'Backup Generator',
                'icon': 'fa-plug',
                'description': 'Automatic backup power during outages'
            },
            {
                'name': 'Water Supply',
                'icon': 'fa-tint',
                'description': 'Reliable 24/7 water supply'
            },
            {
                'name': 'Borehole',
                'icon': 'fa-water',
                'description': 'On-site borehole for consistent water availability'
            },
            {
                'name': 'Solar Panels',
                'icon': 'fa-solar-panel',
                'description': 'Solar power for energy efficiency'
            },
            
            # Fitness & Recreation
            {
                'name': 'Swimming Pool',
                'icon': 'fa-swimming-pool',
                'description': 'Well-maintained swimming pool facility'
            },
            {
                'name': 'Gym/Fitness Center',
                'icon': 'fa-dumbbell',
                'description': 'Fully equipped fitness center'
            },
            {
                'name': 'Children\'s Playground',
                'icon': 'fa-child',
                'description': 'Safe and fun play area for children'
            },
            {
                'name': 'Sports Court',
                'icon': 'fa-basketball-ball',
                'description': 'Basketball/tennis court for sports activities'
            },
            {
                'name': 'Jogging Track',
                'icon': 'fa-running',
                'description': 'Dedicated jogging and walking paths'
            },
            
            # Appliances & Fittings
            {
                'name': 'Air Conditioning',
                'icon': 'fa-snowflake',
                'description': 'Central or split AC units'
            },
            {
                'name': 'Built-in Wardrobes',
                'icon': 'fa-door-closed',
                'description': 'Spacious built-in closet storage'
            },
            {
                'name': 'Modern Kitchen',
                'icon': 'fa-utensils',
                'description': 'Fully fitted kitchen with modern appliances'
            },
            {
                'name': 'Washing Machine',
                'icon': 'fa-soap',
                'description': 'In-unit washing machine'
            },
            {
                'name': 'Dishwasher',
                'icon': 'fa-glass-martini',
                'description': 'Built-in dishwasher'
            },
            
            # Community & Lifestyle
            {
                'name': 'Club House',
                'icon': 'fa-home',
                'description': 'Community club house for events and gatherings'
            },
            {
                'name': 'BBQ Area',
                'icon': 'fa-fire',
                'description': 'Outdoor barbecue and entertainment area'
            },
            {
                'name': 'Rooftop Terrace',
                'icon': 'fa-building',
                'description': 'Shared rooftop terrace with city views'
            },
            {
                'name': 'Garden/Green Space',
                'icon': 'fa-tree',
                'description': 'Well-maintained gardens and green areas'
            },
            {
                'name': 'Pet Friendly',
                'icon': 'fa-paw',
                'description': 'Pets allowed with proper management'
            },
            
            # Services
            {
                'name': 'Concierge Service',
                'icon': 'fa-concierge-bell',
                'description': 'Professional concierge assistance'
            },
            {
                'name': 'Cleaning Service',
                'icon': 'fa-broom',
                'description': 'Regular cleaning and maintenance service'
            },
            {
                'name': 'Laundry Service',
                'icon': 'fa-tshirt',
                'description': 'On-site laundry facilities'
            },
            {
                'name': 'Package Delivery',
                'icon': 'fa-box',
                'description': 'Secure package receiving and storage'
            },
            {
                'name': 'Elevator',
                'icon': 'fa-elevator',
                'description': 'Modern elevator access'
            },
            
            # Location & Access
            {
                'name': 'Near Shopping Center',
                'icon': 'fa-shopping-cart',
                'description': 'Close proximity to shopping facilities'
            },
            {
                'name': 'Near School',
                'icon': 'fa-school',
                'description': 'Walking distance to schools'
            },
            {
                'name': 'Near Hospital',
                'icon': 'fa-hospital',
                'description': 'Close to medical facilities'
            },
            {
                'name': 'Public Transport',
                'icon': 'fa-bus',
                'description': 'Easy access to public transportation'
            },
            {
                'name': 'Furnished',
                'icon': 'fa-couch',
                'description': 'Fully furnished units available'
            },
        ]

        created_count = 0
        updated_count = 0

        for amenity_data in amenities_data:
            amenity, created = Amenity.objects.get_or_create(
                name=amenity_data['name'],
                defaults={
                    'icon': amenity_data['icon'],
                    'description': amenity_data['description'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {amenity.name}'))
            else:
                # Update existing amenity
                amenity.icon = amenity_data['icon']
                amenity.description = amenity_data['description']
                amenity.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated: {amenity.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully processed {len(amenities_data)} amenities'))
        self.stdout.write(self.style.SUCCESS(f'   • Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'   • Updated: {updated_count}'))

