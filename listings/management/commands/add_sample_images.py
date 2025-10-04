from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from listings.models import Property, PropertyMedia
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Add sample images to properties for demonstration'

    def handle(self, *args, **options):
        self.stdout.write('Adding sample images to properties...')
        
        # Get properties that don't have images
        properties = Property.objects.filter(media__isnull=True)[:5]
        
        if not properties.exists():
            self.stdout.write('No properties without images found.')
            return
        
        # Create a simple placeholder image (1x1 pixel PNG)
        placeholder_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        
        for i, property_obj in enumerate(properties):
            # Create main image
            main_image = PropertyMedia.objects.create(
                property=property_obj,
                media_type='image',
                caption=f'Main view of {property_obj.title}',
                is_primary=True,
                order=1
            )
            main_image.file.save(
                f'property_{property_obj.id}_main.png',
                ContentFile(placeholder_png),
                save=True
            )
            
            # Create additional images
            for j in range(2, 4):  # Add 2 more images
                additional_image = PropertyMedia.objects.create(
                    property=property_obj,
                    media_type='image',
                    caption=f'Additional view {j-1} of {property_obj.title}',
                    is_primary=False,
                    order=j
                )
                additional_image.file.save(
                    f'property_{property_obj.id}_view_{j-1}.png',
                    ContentFile(placeholder_png),
                    save=True
                )
            
            self.stdout.write(f'Added images to property: {property_obj.title}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully added sample images to {properties.count()} properties!')
        )
