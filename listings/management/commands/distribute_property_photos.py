from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
import os
import random
from listings.models import Property, PropertyMedia

class Command(BaseCommand):
    help = 'Randomly distribute property photos to properties'

    def handle(self, *args, **options):
        # Get available property images
        static_path = os.path.join(settings.BASE_DIR, 'static', 'images')
        
        # List of available property images
        property_images = [
            'traca 1.jpg', 'traca 2.jpg', 'traca 3.jpg', 'traca 4.jpeg',
            'traca 5.jpeg', 'traca 6.jpeg', 'traca 7.jpeg', 'traca 8.jpeg',
            'traca 9.jpeg', 'property1.jpg', 'property2.jpg', 'property3.jpg',
            'property4.jpg', 'property5.jpg', 'property6.jpg'
        ]
        
        # Verify images exist
        available_images = []
        for img in property_images:
            img_path = os.path.join(static_path, img)
            if os.path.exists(img_path):
                available_images.append(img)
        
        if not available_images:
            self.stdout.write(self.style.ERROR('No property images found!'))
            return
        
        self.stdout.write(f'Found {len(available_images)} available images')
        
        # Get all properties
        properties = Property.objects.all()
        
        if not properties.exists():
            self.stdout.write(self.style.ERROR('No properties found!'))
            return
        
        self.stdout.write(f'Processing {properties.count()} properties...')
        
        # Clear existing media
        PropertyMedia.objects.all().delete()
        self.stdout.write('Cleared existing property media')
        
        # Assign random images to properties
        media_count = 0
        for property in properties:
            # Assign 1-3 random images per property
            num_images = random.randint(1, 3)
            selected_images = random.sample(available_images, min(num_images, len(available_images)))
            
            for i, image_name in enumerate(selected_images):
                # Create PropertyMedia object
                property_media = PropertyMedia.objects.create(
                    property=property,
                    media_type='image',
                    is_primary=(i == 0),  # First image is primary
                    caption=f"{property.title} - Image {i+1}",
                    order=i
                )
                
                # Copy image file
                image_path = os.path.join(static_path, image_name)
                with open(image_path, 'rb') as f:
                    upload_name = f'properties/property_{property.id}_{i + 1}{os.path.splitext(image_name)[1]}'
                    property_media.file.save(upload_name, File(f), save=True)
                
                media_count += 1
                self.stdout.write(f'  - Added {image_name} to {property.title}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully added {media_count} property photos to {properties.count()} properties!'))
        
        # Show statistics
        properties_with_media = Property.objects.filter(media__isnull=False).distinct().count()
        total_media = PropertyMedia.objects.count()
        
        self.stdout.write(f'\n📊 Media Statistics:')
        self.stdout.write(f'   Properties with photos: {properties_with_media}/{properties.count()}')
        self.stdout.write(f'   Total photos: {total_media}')
        self.stdout.write(f'   Average photos per property: {total_media/properties.count():.1f}')
