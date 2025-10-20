from django.core.management.base import BaseCommand
from django.db import transaction
from listings.models import Property, PropertyMedia

class Command(BaseCommand):
    help = 'Fix photo associations - link orphaned media files to properties'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Checking media files...'))
        
        # Get all media files
        all_media = PropertyMedia.objects.all()
        self.stdout.write(f"Total media files: {all_media.count()}")
        
        # Get all properties
        properties = Property.objects.all()
        self.stdout.write(f"Total properties: {properties.count()}")
        
        # Show current associations
        for prop in properties:
            media_count = prop.media.count()
            if media_count > 0:
                self.stdout.write(f"✅ Property: {prop.title} - Media: {media_count}")
            else:
                self.stdout.write(f"❌ Property: {prop.title} - Media: {media_count}")
        
        # Check for orphaned media
        orphaned_media = PropertyMedia.objects.filter(property__isnull=True)
        self.stdout.write(f"\nOrphaned media files: {orphaned_media.count()}")
        
        if orphaned_media.exists():
            self.stdout.write(self.style.WARNING('🔧 Found orphaned media files!'))
            
            # Show orphaned files
            for media in orphaned_media:
                self.stdout.write(f"  - {media.file.name} (Type: {media.media_type})")
            
            # Ask for confirmation
            response = input('\nDo you want to associate orphaned media with the first property? (y/n): ')
            
            if response.lower() == 'y':
                with transaction.atomic():
                    first_property = properties.first()
                    if first_property:
                        for media in orphaned_media:
                            media.property = first_property
                            media.save()
                            self.stdout.write(
                                self.style.SUCCESS(f"✅ Associated {media.file.name} with {first_property.title}")
                            )
                        self.stdout.write(self.style.SUCCESS('✅ Photo association fix completed!'))
                    else:
                        self.stdout.write(self.style.ERROR('❌ No properties found!'))
            else:
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ No orphaned media files found!'))
        
        # Final check
        self.stdout.write('\n📊 Final status:')
        for prop in properties:
            media_count = prop.media.count()
            if media_count > 0:
                self.stdout.write(f"✅ {prop.title}: {media_count} media files")
            else:
                self.stdout.write(f"❌ {prop.title}: No media files")
