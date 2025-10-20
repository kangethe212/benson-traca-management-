from django.core.management.base import BaseCommand
from listings.models import Property, PropertyMedia
import os

class Command(BaseCommand):
    help = 'Associate photos with properties'

    def add_arguments(self, parser):
        parser.add_argument('--property-id', type=int, help='Property ID to associate photos with')
        parser.add_argument('--photo-path', type=str, help='Path to photo file')

    def handle(self, *args, **options):
        property_id = options.get('property_id')
        photo_path = options.get('photo_path')
        
        if not property_id or not photo_path:
            self.stdout.write(self.style.WARNING('Please provide both --property-id and --photo-path'))
            self.show_available_properties()
            return
        
        try:
            property_obj = Property.objects.get(id=property_id)
            
            # Create PropertyMedia entry
            media = PropertyMedia.objects.create(
                property=property_obj,
                media_type='image',
                file=photo_path,
                caption=f"Photo for {property_obj.title}",
                is_primary=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully associated photo with "{property_obj.title}"')
            )
            
        except Property.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Property with ID {property_id} not found'))
            self.show_available_properties()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))

    def show_available_properties(self):
        self.stdout.write('\n📋 Available Properties:')
        properties = Property.objects.all()
        for prop in properties:
            media_count = prop.media.count()
            status = "✅" if media_count > 0 else "❌"
            self.stdout.write(f'{status} ID: {prop.id} - {prop.title} ({media_count} photos)')
