from django.core.management.base import BaseCommand
from listings.models import TenantService
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populates the database with tenant services offered by Traca Management'

    def handle(self, *args, **kwargs):
        services_data = [
            # Maintenance & Repairs
            {
                'name': 'Emergency Plumbing Repair',
                'category': 'maintenance',
                'description': '24/7 emergency plumbing services for leaks, burst pipes, and drainage issues. Quick response time guaranteed.',
                'icon': 'fa-wrench',
                'price': Decimal('2500.00'),
                'contact_phone': '+254 700 123 456',
                'is_featured': True
            },
            {
                'name': 'Electrical Repairs',
                'category': 'maintenance',
                'description': 'Certified electricians for all electrical repairs, wiring issues, and installations.',
                'icon': 'fa-bolt',
                'price': Decimal('2000.00'),
                'contact_phone': '+254 700 123 456',
                'is_featured': True
            },
            {
                'name': 'AC Maintenance & Repair',
                'category': 'maintenance',
                'description': 'Air conditioning servicing, repairs, and maintenance. Regular check-ups available.',
                'icon': 'fa-fan',
                'price': Decimal('3500.00'),
                'contact_phone': '+254 700 123 456',
            },
            {
                'name': 'Painting Services',
                'category': 'maintenance',
                'description': 'Professional interior and exterior painting services with quality materials.',
                'icon': 'fa-paint-roller',
                'price': Decimal('15000.00'),
                'contact_phone': '+254 700 123 456',
            },
            {
                'name': 'Carpentry Services',
                'category': 'maintenance',
                'description': 'Door repairs, cabinet installations, and custom carpentry work.',
                'icon': 'fa-hammer',
                'price': Decimal('5000.00'),
                'contact_phone': '+254 700 123 456',
            },
            {
                'name': 'General Handyman',
                'category': 'maintenance',
                'description': 'General repairs and maintenance for minor issues around your property.',
                'icon': 'fa-tools',
                'price': Decimal('1500.00'),
                'contact_phone': '+254 700 123 456',
            },
            
            # Cleaning Services
            {
                'name': 'Deep Cleaning Service',
                'category': 'cleaning',
                'description': 'Comprehensive deep cleaning including carpets, windows, and hard-to-reach areas.',
                'icon': 'fa-broom',
                'price': Decimal('5000.00'),
                'contact_email': 'cleaning@traca.co.ke',
                'is_featured': True
            },
            {
                'name': 'Weekly Housekeeping',
                'category': 'cleaning',
                'description': 'Regular weekly cleaning services to keep your home spotless.',
                'icon': 'fa-home',
                'price': Decimal('8000.00'),
                'contact_email': 'cleaning@traca.co.ke',
            },
            {
                'name': 'Move-In/Move-Out Cleaning',
                'category': 'cleaning',
                'description': 'Thorough cleaning service when moving in or out of your property.',
                'icon': 'fa-box-open',
                'price': Decimal('7500.00'),
                'contact_email': 'cleaning@traca.co.ke',
            },
            {
                'name': 'Window Cleaning',
                'category': 'cleaning',
                'description': 'Professional window cleaning for crystal clear views.',
                'icon': 'fa-window-maximize',
                'price': Decimal('2000.00'),
                'contact_email': 'cleaning@traca.co.ke',
            },
            {
                'name': 'Carpet & Upholstery Cleaning',
                'category': 'cleaning',
                'description': 'Steam cleaning and stain removal for carpets and furniture.',
                'icon': 'fa-couch',
                'price': Decimal('4500.00'),
                'contact_email': 'cleaning@traca.co.ke',
            },
            
            # Utility Management
            {
                'name': 'Electricity Bill Payment',
                'category': 'utilities',
                'description': 'Convenient electricity bill payment and monitoring service.',
                'icon': 'fa-lightbulb',
                'price': None,  # Free service
                'contact_email': 'utilities@traca.co.ke',
                'is_featured': True
            },
            {
                'name': 'Water Bill Management',
                'category': 'utilities',
                'description': 'Water bill payment and usage tracking assistance.',
                'icon': 'fa-tint',
                'price': None,  # Free service
                'contact_email': 'utilities@traca.co.ke',
                'is_featured': True
            },
            {
                'name': 'Internet Installation',
                'category': 'utilities',
                'description': 'WiFi and internet connection setup with preferred providers.',
                'icon': 'fa-wifi',
                'price': Decimal('3000.00'),
                'contact_email': 'utilities@traca.co.ke',
            },
            {
                'name': 'DSTV Installation',
                'category': 'utilities',
                'description': 'Professional DSTV and satellite TV installation.',
                'icon': 'fa-satellite-dish',
                'price': Decimal('2500.00'),
                'contact_email': 'utilities@traca.co.ke',
            },
            
            # Security Services
            {
                'name': 'Additional Security Guard',
                'category': 'security',
                'description': 'Extra security personnel for enhanced protection.',
                'icon': 'fa-shield-alt',
                'price': Decimal('25000.00'),
                'contact_phone': '+254 700 123 456',
            },
            {
                'name': 'CCTV Installation',
                'category': 'security',
                'description': 'Installation of personal CCTV cameras in your unit.',
                'icon': 'fa-video',
                'price': Decimal('15000.00'),
                'contact_phone': '+254 700 123 456',
            },
            {
                'name': 'Smart Lock Installation',
                'category': 'security',
                'description': 'Modern smart lock systems for enhanced security.',
                'icon': 'fa-lock',
                'price': Decimal('12000.00'),
                'contact_phone': '+254 700 123 456',
            },
            {
                'name': 'Emergency Response',
                'category': 'security',
                'description': '24/7 emergency security response team on standby.',
                'icon': 'fa-exclamation-triangle',
                'price': None,  # Included
                'contact_phone': '+254 700 123 456',
                'is_featured': True
            },
            
            # Lifestyle Services
            {
                'name': 'Gym Membership',
                'category': 'lifestyle',
                'description': 'Access to on-site gym facilities with modern equipment.',
                'icon': 'fa-dumbbell',
                'price': Decimal('3000.00'),
                'contact_email': 'lifestyle@traca.co.ke',
                'is_featured': True
            },
            {
                'name': 'Swimming Pool Access',
                'category': 'lifestyle',
                'description': 'Monthly pass for pool facility usage.',
                'icon': 'fa-swimming-pool',
                'price': Decimal('2000.00'),
                'contact_email': 'lifestyle@traca.co.ke',
            },
            {
                'name': 'Event Space Booking',
                'category': 'lifestyle',
                'description': 'Reserve club house or common areas for private events.',
                'icon': 'fa-calendar-alt',
                'price': Decimal('10000.00'),
                'contact_email': 'lifestyle@traca.co.ke',
            },
            {
                'name': 'Pet Care Services',
                'category': 'lifestyle',
                'description': 'Pet grooming, walking, and sitting services.',
                'icon': 'fa-paw',
                'price': Decimal('4000.00'),
                'contact_email': 'lifestyle@traca.co.ke',
            },
            {
                'name': 'Laundry Service',
                'category': 'lifestyle',
                'description': 'Professional laundry pickup, wash, and delivery service.',
                'icon': 'fa-tshirt',
                'price': Decimal('1500.00'),
                'contact_email': 'lifestyle@traca.co.ke',
            },
            
            # Support Services
            {
                'name': 'Tenant Support Hotline',
                'category': 'support',
                'description': '24/7 dedicated support line for all tenant inquiries and issues.',
                'icon': 'fa-phone',
                'price': None,  # Free service
                'contact_phone': '+254 700 123 456',
                'is_featured': True
            },
            {
                'name': 'Document Processing',
                'category': 'support',
                'description': 'Assistance with lease renewals, good standing letters, and other documents.',
                'icon': 'fa-file-alt',
                'price': None,  # Free service
                'contact_email': 'support@traca.co.ke',
                'is_featured': True
            },
            {
                'name': 'Relocation Assistance',
                'category': 'support',
                'description': 'Help with moving services and unit transfer coordination.',
                'icon': 'fa-truck-moving',
                'price': Decimal('8000.00'),
                'contact_email': 'support@traca.co.ke',
            },
            {
                'name': 'Legal Consultation',
                'category': 'support',
                'description': 'Free initial consultation on tenancy-related legal matters.',
                'icon': 'fa-gavel',
                'price': None,  # Free consultation
                'contact_email': 'legal@traca.co.ke',
            },
            {
                'name': 'Property Insurance',
                'category': 'support',
                'description': 'Tenant contents insurance packages at discounted rates.',
                'icon': 'fa-shield-alt',
                'price': Decimal('5000.00'),
                'contact_email': 'insurance@traca.co.ke',
            },
            {
                'name': 'Furniture Rental',
                'category': 'support',
                'description': 'Rent quality furniture on monthly or yearly basis.',
                'icon': 'fa-couch',
                'price': Decimal('15000.00'),
                'contact_email': 'furniture@traca.co.ke',
            },
        ]

        created_count = 0
        updated_count = 0

        for service_data in services_data:
            service, created = TenantService.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            
            if created:
                created_count += 1
                price_str = f"KSh {service.price:,.0f}" if service.price else "FREE"
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created: {service.name} ({service.get_category_display()}) - {price_str}'
                    )
                )
            else:
                # Update existing service
                for key, value in service_data.items():
                    if key != 'name':  # Don't update the name (used as identifier)
                        setattr(service, key, value)
                service.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated: {service.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully processed {len(services_data)} services'))
        self.stdout.write(self.style.SUCCESS(f'   • Created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'   • Updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'\n📊 Service Categories:'))
        
        # Show count by category
        from django.db.models import Count
        categories = TenantService.objects.values('category').annotate(count=Count('id'))
        for cat in categories:
            cat_display = dict(TenantService.SERVICE_CATEGORIES).get(cat['category'], cat['category'])
            self.stdout.write(self.style.SUCCESS(f'   • {cat_display}: {cat["count"]} services'))

