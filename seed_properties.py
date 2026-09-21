import os
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django

django.setup()

from listings.models import County, Property

COUNTIES = [
    'Nairobi', 'Kiambu', 'Kajiado', 'Mombasa', 'Nakuru', 'Machakos',
    'Kisumu', 'Athi River', 'Naivasha', 'Thika', 'Kitengela', 'Nyeri'
]

for county_name in COUNTIES:
    base_slug = slugify(county_name) or 'county'
    slug = base_slug
    counter = 2
    while County.objects.filter(slug=slug).exclude(name=county_name).exists():
        slug = f'{base_slug}-{counter}'
        counter += 1

    county_obj, created = County.objects.get_or_create(
        name=county_name,
        defaults={'slug': slug}
    )
    if not created and county_obj.slug != slug:
        county_obj.slug = slug
        county_obj.save(update_fields=['slug'])

county_map = {county.name.lower(): county for county in County.objects.all()}

items = [
    ('3 Bedroom Family Home', 'Kiambu', 'sale', 9500000, 1800, 3, 2, 2, 'Secure family home in a quiet estate, close to schools, parks, and daily essentials.'),
    ('2 Bedroom Apartment', 'Nairobi', 'sale', 8800000, 1200, 2, 2, 1, 'Modern apartment in a central neighborhood with transport access and convenient shopping nearby.'),
    ('Studio Flat for Rent', 'Nairobi', 'rent', 35000, 500, 1, 1, 0, 'Compact studio with clean finishes, ideal for professionals wanting easy city access.'),
    ('4 Bedroom Villa', 'Kajiado', 'sale', 23500000, 2600, 4, 3, 3, 'Luxury villa with generous living space, outdoor greenery, and a secure family-friendly environment.'),
    ('2 Bedroom House', 'Machakos', 'rent', 28000, 900, 2, 1, 1, 'Neat home in a calm residential area suited to small families and working singles.'),
    ('3 Bedroom Bungalow', 'Mombasa', 'sale', 14500000, 2100, 3, 2, 2, 'Bright bungalow with airy rooms and a relaxed coastal feel near key amenities.'),
    ('1 Bedroom Apartment', 'Nairobi', 'rent', 30000, 650, 1, 1, 0, 'Well-kept apartment with practical living space and access to nearby shops and transport.'),
    ('5 Bedroom Mansion', 'Nakuru', 'sale', 30000000, 3400, 5, 4, 4, 'Statement home featuring spacious rooms, premium finishes, and commanding family living comfort.'),
    ('2 Bedroom Maisonette', 'Athi River', 'sale', 9750000, 1600, 2, 2, 1, 'Comfortable maisonette with a practical layout and strong access to Nairobi and county roads.'),
    ('4 Bedroom Home', 'Kitengela', 'rent', 65000, 2000, 4, 3, 2, 'Large family residence with secure surroundings and easy access to schools, shops, and clinics.'),
    ('3 Bedroom Townhouse', 'Kisumu', 'sale', 11200000, 1900, 3, 2, 2, 'Attractive townhouse that balances comfort, value, and convenient neighborhood access.'),
    ('2 Bedroom Apartment', 'Mombasa', 'rent', 42000, 850, 2, 2, 1, 'Fresh apartment near the city with good natural light and modern convenience for tenants.'),
    ('5 Bedroom Villa', 'Kiambu', 'sale', 28000000, 3600, 5, 4, 3, 'Premium villa with generous indoor and outdoor spaces, suited to a refined family lifestyle.'),
    ('1 Bedroom Studio', 'Nairobi', 'rent', 26000, 450, 1, 1, 0, 'Compact and stylish studio for single occupants seeking an easy urban living setup.'),
    ('4 Bedroom Family House', 'Nakuru', 'rent', 70000, 2200, 4, 3, 2, 'Comfortable family home with space for entertaining, working from home, and daily living.'),
    ('3 Bedroom Townhouse', 'Kajiado', 'sale', 13500000, 2000, 3, 2, 2, 'Modern townhouse in a growing suburb, offering both family comfort and future appreciation.'),
    ('2 Bedroom Flat', 'Thika', 'rent', 25000, 800, 2, 1, 1, 'Simple, clean flat with practical layout and close access to local services and transport.'),
    ('4 Bedroom Estate House', 'Machakos', 'sale', 16800000, 2500, 4, 3, 2, 'Spacious estate home with family-friendly design and room for comfortable everyday living.'),
    ('3 Bedroom Apartment', 'Mombasa', 'sale', 16000000, 1700, 3, 2, 1, 'Well-located apartment with practical space and strong value for both end-users and investors.'),
    ('2 Bedroom Bungalow', 'Naivasha', 'rent', 32000, 1000, 2, 2, 1, 'Calm bungalow in a peaceful setting, ideal for tenants wanting comfort and quiet.'),
    ('5 Bedroom Duplex', 'Nairobi', 'sale', 33000000, 4000, 5, 4, 3, 'Luxury duplex with generous layout, premium finishes, and excellent family living appeal.'),
    ('1 Bedroom Unit', 'Athi River', 'rent', 22000, 430, 1, 1, 0, 'Affordable and clean single-bedroom unit suited to couples or professionals seeking convenience.'),
    ('3 Bedroom Modern Home', 'Kitengela', 'sale', 14000000, 2100, 3, 2, 2, 'Contemporary home in a popular suburb that offers comfort, convenience, and strong market appeal.'),
    ('2 Bedroom Flat', 'Kisumu', 'rent', 24000, 760, 2, 1, 1, 'Comfortable flat with practical features and quick access to daily essentials and routes.'),
    ('4 Bedroom Family Villa', 'Kiambu', 'rent', 85000, 2400, 4, 3, 2, 'Spacious villa with bright rooms, outdoor space, and an easy family living setup.'),
    ('3 Bedroom Apartment', 'Nairobi', 'sale', 17800000, 1900, 3, 2, 1, 'Well-balanced apartment in a lively area with convenience, comfort, and long-term value.'),
    ('2 Bedroom Rental Home', 'Nakuru', 'rent', 31000, 900, 2, 2, 1, 'Neat home with open living areas and comfortable access to schools, shops, and transport.'),
    ('4 Bedroom Coastal Villa', 'Mombasa', 'rent', 95000, 2600, 4, 3, 2, 'Bright coastal villa with generous space and a relaxed environment for modern family living.'),
    ('3 Bedroom Home', 'Thika', 'sale', 11800000, 1950, 3, 2, 2, 'Practical and stylish home in a fast-growing area with good family appeal and lifestyle value.'),
    ('2 Bedroom Apartment', 'Machakos', 'rent', 22000, 700, 2, 1, 1, 'Affordable apartment with good room layout and easy access to commuter routes.'),
    ('3 Bedroom Residence', 'Nyeri', 'sale', 12700000, 2000, 3, 2, 2, 'Well-designed residence in a calm neighborhood, ideal for buyers seeking comfort and stability.'),
]

for idx, (title, county_name, property_type, price, area, bedrooms, bathrooms, parking_slots, description) in enumerate(items, start=1):
    county = county_map[county_name.lower()]
    property_obj, _ = Property.objects.get_or_create(
        title=title,
        county=county,
        property_type=property_type,
        defaults={
            'price': price,
            'area': area,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'parking_slots': parking_slots,
            'description': description,
            'is_verified': True,
        },
    )
    property_obj.is_verified = True
    property_obj.description = description
    property_obj.save(update_fields=['description', 'is_verified'])

    if property_obj.media.filter(media_type='image').exists():
        continue

    seed = f'traca-{idx}-{slugify(title)}-{slugify(county_name)}'
    image_url = f'https://picsum.photos/seed/{seed}/1200/800'
    request = Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        image_data = urlopen(request, timeout=30).read()
        filename = f'{slugify(title)}-{idx}.jpg'
        property_obj.media.create(
            media_type='image',
            file=ContentFile(image_data, name=filename),
            caption=title,
            is_primary=True,
            order=1,
        )
    except Exception:
        pass

print(f'Properties loaded: {Property.objects.count()}')
