from django.core.management.base import BaseCommand
from listings.models import Property, County
from decimal import Decimal

class Command(BaseCommand):
    help = 'Add properties for sale and rent to ensure at least 12 properties on home page'

    def handle(self, *args, **options):
        # Check current count
        current_count = Property.objects.filter(property_type__in=['sale', 'rent']).count()
        self.stdout.write(f'Current sale/rent properties: {current_count}')
        
        if current_count >= 12:
            self.stdout.write(self.style.SUCCESS('Already have 12+ sale/rent properties!'))
            return
        
        # Get or create counties
        counties_data = [
            {'name': 'Nairobi', 'slug': 'nairobi'},
            {'name': 'Mombasa', 'slug': 'mombasa'},
            {'name': 'Kisumu', 'slug': 'kisumu'},
        ]
        
        counties = {}
        for county_data in counties_data:
            county, created = County.objects.get_or_create(
                name=county_data['name'],
                defaults={'slug': county_data['slug'], 'is_active': True}
            )
            counties[county_data['name']] = county
            if created:
                self.stdout.write(f'Created county: {county_data["name"]}')
        
        # Property data
        properties_data = [
            # Sale properties
            {'title': 'Modern Apartment for Sale in Westlands', 'property_type': 'sale', 'county': counties['Nairobi'], 'price': Decimal('8500000'), 'bedrooms': 2, 'bathrooms': 2, 'parking_slots': 1, 'description': 'Beautiful modern apartment in Westlands with great amenities and security.', 'is_published': True, 'is_featured': True},
            {'title': 'Spacious House for Sale in Karen', 'property_type': 'sale', 'county': counties['Nairobi'], 'price': Decimal('12000000'), 'bedrooms': 4, 'bathrooms': 3, 'parking_slots': 2, 'description': 'Large family house in Karen with garden and swimming pool.', 'is_published': True, 'is_featured': True},
            {'title': 'Beachfront Villa for Sale in Diani', 'property_type': 'sale', 'county': counties['Mombasa'], 'price': Decimal('20000000'), 'bedrooms': 5, 'bathrooms': 4, 'parking_slots': 3, 'description': 'Luxury beachfront villa with stunning ocean views.', 'is_published': True, 'is_featured': True},
            {'title': 'Townhouse for Sale in Runda', 'property_type': 'sale', 'county': counties['Nairobi'], 'price': Decimal('9500000'), 'bedrooms': 3, 'bathrooms': 2, 'parking_slots': 2, 'description': 'Modern townhouse in Runda with excellent security.', 'is_published': True, 'is_featured': True},
            {'title': 'Penthouse for Sale in Upper Hill', 'property_type': 'sale', 'county': counties['Nairobi'], 'price': Decimal('18000000'), 'bedrooms': 4, 'bathrooms': 3, 'parking_slots': 2, 'description': 'Luxury penthouse with city views in Upper Hill.', 'is_published': True, 'is_featured': True},
            {'title': 'House for Sale in Kisumu CBD', 'property_type': 'sale', 'county': counties['Kisumu'], 'price': Decimal('6500000'), 'bedrooms': 3, 'bathrooms': 2, 'parking_slots': 2, 'description': 'Comfortable house in Kisumu CBD with good access to amenities.', 'is_published': True, 'is_featured': False},
            # Rent properties
            {'title': 'Cozy Studio for Rent in Kilimani', 'property_type': 'rent', 'county': counties['Nairobi'], 'price': Decimal('45000'), 'bedrooms': 1, 'bathrooms': 1, 'parking_slots': 1, 'description': 'Perfect studio apartment for young professionals in Kilimani.', 'is_published': True, 'is_featured': True},
            {'title': 'Duplex for Rent in Lavington', 'property_type': 'rent', 'county': counties['Nairobi'], 'price': Decimal('110000'), 'bedrooms': 3, 'bathrooms': 3, 'parking_slots': 2, 'description': 'Beautiful duplex in Lavington with garden.', 'is_published': True, 'is_featured': True},
            {'title': 'Apartment for Rent in Nyali', 'property_type': 'rent', 'county': counties['Mombasa'], 'price': Decimal('75000'), 'bedrooms': 2, 'bathrooms': 2, 'parking_slots': 1, 'description': 'Modern apartment in Nyali near the beach.', 'is_published': True, 'is_featured': True},
            {'title': 'Studio for Rent in Nakuru', 'property_type': 'rent', 'county': counties['Nairobi'], 'price': Decimal('35000'), 'bedrooms': 1, 'bathrooms': 1, 'parking_slots': 1, 'description': 'Affordable studio apartment in Nakuru town.', 'is_published': True, 'is_featured': False},
            {'title': 'Villa for Rent in Eldoret', 'property_type': 'rent', 'county': counties['Nairobi'], 'price': Decimal('85000'), 'bedrooms': 4, 'bathrooms': 3, 'parking_slots': 2, 'description': 'Spacious villa in Eldoret with garden.', 'is_published': True, 'is_featured': False},
            {'title': 'Apartment for Rent in Thika', 'property_type': 'rent', 'county': counties['Nairobi'], 'price': Decimal('55000'), 'bedrooms': 2, 'bathrooms': 2, 'parking_slots': 1, 'description': 'Modern apartment in Thika with good amenities.', 'is_published': True, 'is_featured': False},
            {'title': 'House for Rent in Westlands', 'property_type': 'rent', 'county': counties['Nairobi'], 'price': Decimal('95000'), 'bedrooms': 3, 'bathrooms': 2, 'parking_slots': 2, 'description': 'Comfortable house in Westlands with garden.', 'is_published': True, 'is_featured': False},
            {'title': 'Penthouse for Rent in Kilimani', 'property_type': 'rent', 'county': counties['Nairobi'], 'price': Decimal('150000'), 'bedrooms': 3, 'bathrooms': 3, 'parking_slots': 2, 'description': 'Luxury penthouse in Kilimani with city views.', 'is_published': True, 'is_featured': True},
            {'title': 'Townhouse for Rent in Karen', 'property_type': 'rent', 'county': counties['Nairobi'], 'price': Decimal('120000'), 'bedrooms': 4, 'bathrooms': 3, 'parking_slots': 2, 'description': 'Spacious townhouse in Karen with garden.', 'is_published': True, 'is_featured': True},
        ]
        
        # Add properties
        added_count = 0
        for prop_data in properties_data:
            # Check if property already exists
            if Property.objects.filter(title=prop_data['title']).exists():
                self.stdout.write(f"Property '{prop_data['title']}' already exists, skipping...")
                continue
                
            try:
                property_obj = Property.objects.create(**prop_data)
                self.stdout.write(f"Added property: {property_obj.title} ({property_obj.property_type})")
                added_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error adding property '{prop_data['title']}': {e}"))
        
        # Final count
        final_count = Property.objects.filter(property_type__in=['sale', 'rent']).count()
        self.stdout.write(f"\nProperties added: {added_count}")
        self.stdout.write(f"Total sale/rent properties now: {final_count}")
        
        if final_count >= 12:
            self.stdout.write(self.style.SUCCESS('✅ Success! You now have 12+ properties available for the home page.'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️ Still need {12 - final_count} more properties to reach 12.'))
