from django.core.management.base import BaseCommand
from listings.models import Property, PropertyMedia
import os
import random

class Command(BaseCommand):
    help = 'Randomly assign photos from media/properties/ to properties without photos'

    def handle(self, *args, **options):
        # Get all properties without photos
        properties_without_photos = Property.objects.filter(media__isnull=True).distinct()
        
        # Get all available photo files from media/properties/
        media_dir = 'media/properties/'
        if os.path.exists(media_dir):
            photo_files = []
            for filename in os.listdir(media_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    photo_files.append(filename)
            
            self.stdout.write(f'📸 Found {len(photo_files)} photos in media/properties/')
            self.stdout.write(f'🏠 Found {properties_without_photos.count()} properties without photos')
            
            if not photo_files:
                self.stdout.write(self.style.WARNING('❌ No photos found in media/properties/ directory'))
                return
            
            # Randomly assign photos to properties
            assigned_count = 0
            for i, property_obj in enumerate(properties_without_photos):
                if i < len(photo_files):
                    # Select a random photo
                    photo_file = random.choice(photo_files)
                    photo_path = f'properties/{photo_file}'
                    
                    # Create PropertyMedia entry
                    media = PropertyMedia.objects.create(
                        property=property_obj,
                        media_type='image',
                        file=photo_path,
                        caption=f"Photo of {property_obj.title}",
                        is_primary=True,
                        order=1
                    )
                    
                    self.stdout.write(f'✅ Assigned "{photo_file}" to "{property_obj.title}"')
                    assigned_count += 1
                    
                    # Remove used photo from list to avoid duplicates
                    photo_files.remove(photo_file)
            
            self.stdout.write(self.style.SUCCESS(f'\n🎉 Successfully assigned {assigned_count} photos to properties!'))
            
            # Show final status
            self.stdout.write('\n📊 Final Status:')
            for prop in Property.objects.all():
                media_count = prop.media.count()
                status = "✅" if media_count > 0 else "❌"
                self.stdout.write(f'{status} {prop.title}: {media_count} photos')
                
        else:
            self.stdout.write(self.style.ERROR('❌ media/properties/ directory not found'))
