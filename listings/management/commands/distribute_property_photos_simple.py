from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
import os
import random
from listings.models import Property

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
        
        # Assign random main image to each property
        media_count = 0
        for property in properties:
            # Select random image
            selected_image = random.choice(available_images)
            
            # Copy image to media folder
            image_path = os.path.join(static_path, selected_image)
            
            try:
                with open(image_path, 'rb') as f:
                    # Generate unique filename
                    file_extension = os.path.splitext(selected_image)[1]
                    new_filename = f"property_{property.id}_{random.randint(1000, 9999)}{file_extension}"
                    
                    # Save to main_image field
                    property.main_image.save(new_filename, File(f), save=True)
                    property.save()
                    
                    media_count += 1
                    self.stdout.write(f'  - Added {selected_image} to {property.title}')
                    
            except Exception as e:
                self.stdout.write(f'  - Error adding image to {property.title}: {str(e)}')
                continue
        
        self.stdout.write(self.style.SUCCESS(f'Successfully added {media_count} property photos to {properties.count()} properties!'))
        
        # Show statistics
        properties_with_media = Property.objects.exclude(main_image='').count()
        
        self.stdout.write(f'\n📊 Media Statistics:')
        self.stdout.write(f'   Properties with photos: {properties_with_media}/{properties.count()}')
        self.stdout.write(f'   Total photos: {media_count}')
