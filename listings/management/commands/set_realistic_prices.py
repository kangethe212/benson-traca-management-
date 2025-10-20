from django.core.management.base import BaseCommand
from listings.models import Property
import random

class Command(BaseCommand):
    help = 'Set realistic market prices for properties based on Kenyan real estate market'

    def handle(self, *args, **options):
        # Kenyan real estate market price ranges (in KES)
        price_ranges = {
            'sale': {
                'apartment_2bed': (2500000, 4500000),  # 2.5M - 4.5M
                'apartment_3bed': (3500000, 6500000),  # 3.5M - 6.5M
                'house_2bed': (2000000, 3500000),      # 2M - 3.5M
                'house_3bed': (3000000, 5500000),      # 3M - 5.5M
                'house_4bed': (4500000, 8500000),      # 4.5M - 8.5M
                'house_5bed': (6500000, 12000000),     # 6.5M - 12M
                'house_6bed': (10000000, 20000000),    # 10M - 20M
                'commercial': (15000000, 50000000),    # 15M - 50M
                'land': (500000, 2000000),             # 500K - 2M per acre
                'villa': (8000000, 25000000),          # 8M - 25M
                'office': (12000000, 35000000),        # 12M - 35M
            },
            'rent': {
                'apartment_2bed': (25000, 45000),      # 25K - 45K per month
                'apartment_3bed': (35000, 65000),      # 35K - 65K per month
                'house_2bed': (20000, 35000),          # 20K - 35K per month
                'house_3bed': (30000, 55000),          # 30K - 55K per month
                'house_4bed': (45000, 85000),          # 45K - 85K per month
                'house_5bed': (65000, 120000),         # 65K - 120K per month
                'house_6bed': (100000, 200000),        # 100K - 200K per month
                'commercial': (150000, 500000),        # 150K - 500K per month
                'land': (5000, 20000),                 # 5K - 20K per month
                'villa': (80000, 250000),              # 80K - 250K per month
                'office': (120000, 350000),            # 120K - 350K per month
            }
        }

        def get_price_range(property_obj):
            title_lower = property_obj.title.lower()
            bedrooms = property_obj.bedrooms or 0
            
            # Determine property category
            if 'commercial' in title_lower or 'office' in title_lower:
                if 'office' in title_lower:
                    return 'office'
                return 'commercial'
            elif 'land' in title_lower:
                return 'land'
            elif 'villa' in title_lower or 'mansion' in title_lower:
                return 'villa'
            elif 'apartment' in title_lower:
                if bedrooms >= 3:
                    return 'apartment_3bed'
                else:
                    return 'apartment_2bed'
            else:  # House
                if bedrooms >= 6:
                    return 'house_6bed'
                elif bedrooms >= 5:
                    return 'house_5bed'
                elif bedrooms >= 4:
                    return 'house_4bed'
                elif bedrooms >= 3:
                    return 'house_3bed'
                else:
                    return 'house_2bed'

        updated_count = 0
        
        for prop in Property.objects.all():
            category = get_price_range(prop)
            prop_type = prop.property_type
            
            if category in price_ranges[prop_type]:
                min_price, max_price = price_ranges[prop_type][category]
                # Add some randomness within the range
                price = random.randint(min_price, max_price)
                prop.price = price
                prop.save()
                
                # Format price for display
                if prop_type == 'sale':
                    if price >= 1000000:
                        price_str = f"KES {price/1000000:.1f}M"
                    else:
                        price_str = f"KES {price:,}"
                else:  # rent
                    if price >= 100000:
                        price_str = f"KES {price/1000:.0f}K/month"
                    else:
                        price_str = f"KES {price:,}/month"
                
                self.stdout.write(f'💰 {prop.title} ({prop_type.upper()}) → {price_str}')
                updated_count += 1
            else:
                self.stdout.write(f'⚠️  {prop.title} → No price range defined for {category}')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully updated {updated_count} properties with realistic market prices!'))
        
        # Show summary by type
        sale_props = Property.objects.filter(property_type='sale')
        rent_props = Property.objects.filter(property_type='rent')
        
        self.stdout.write(f'\n📊 Price Summary:')
        self.stdout.write(f'🏡 FOR SALE Properties: {sale_props.count()}')
        for prop in sale_props[:5]:  # Show first 5
            price_str = f"KES {prop.price/1000000:.1f}M" if prop.price >= 1000000 else f"KES {prop.price:,}"
            self.stdout.write(f'   • {prop.title}: {price_str}')
        
        self.stdout.write(f'\n🏠 FOR RENT Properties: {rent_props.count()}')
        for prop in rent_props[:5]:  # Show first 5
            price_str = f"KES {prop.price/1000:.0f}K/month" if prop.price >= 100000 else f"KES {prop.price:,}/month"
            self.stdout.write(f'   • {prop.title}: {price_str}')
