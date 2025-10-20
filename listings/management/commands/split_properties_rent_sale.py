from django.core.management.base import BaseCommand
from listings.models import Property
import random

class Command(BaseCommand):
    help = 'Split properties - half for rent, half for sale'

    def add_arguments(self, parser):
        parser.add_argument('--rent-percentage', type=int, default=50, help='Percentage of properties to mark as rent (default: 50)')

    def handle(self, *args, **options):
        rent_percentage = options['rent_percentage']
        
        # Get all properties
        all_properties = list(Property.objects.all())
        total_properties = len(all_properties)
        
        if total_properties == 0:
            self.stdout.write(self.style.WARNING('❌ No properties found'))
            return
        
        # Calculate how many should be for rent
        rent_count = int((rent_percentage / 100) * total_properties)
        sale_count = total_properties - rent_count
        
        self.stdout.write(f'📊 Total Properties: {total_properties}')
        self.stdout.write(f'🏠 Properties for Rent: {rent_count}')
        self.stdout.write(f'🏡 Properties for Sale: {sale_count}')
        
        # Shuffle properties randomly
        random.shuffle(all_properties)
        
        # Mark first portion as rent, rest as sale
        rent_properties = all_properties[:rent_count]
        sale_properties = all_properties[rent_count:]
        
        # Update rent properties
        for prop in rent_properties:
            prop.property_type = 'rent'
            prop.save()
            self.stdout.write(f'🏠 {prop.title} → FOR RENT')
        
        # Update sale properties
        for prop in sale_properties:
            prop.property_type = 'sale'
            prop.save()
            self.stdout.write(f'🏡 {prop.title} → FOR SALE')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully updated {total_properties} properties!'))
        
        # Show final summary
        rent_total = Property.objects.filter(property_type='rent').count()
        sale_total = Property.objects.filter(property_type='sale').count()
        
        self.stdout.write(f'\n📊 Final Summary:')
        self.stdout.write(f'🏠 Properties for Rent: {rent_total}')
        self.stdout.write(f'🏡 Properties for Sale: {sale_total}')
