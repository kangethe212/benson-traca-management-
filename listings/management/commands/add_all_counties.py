from django.core.management.base import BaseCommand
from listings.models import County


class Command(BaseCommand):
    help = 'Add all 47 counties in Kenya to the database'

    def handle(self, *args, **options):
        self.stdout.write('Adding all 47 counties in Kenya...')
        
        # All 47 counties in Kenya with their descriptions and main towns
        counties_data = [
            # Nairobi Metropolitan Area
            {'name': 'Nairobi', 'slug': 'nairobi', 'description': 'Kenya\'s capital city and commercial hub, home to major businesses, government offices, and international organizations.', 'main_towns': 'Nairobi CBD, Westlands, Karen, Runda, Kilimani, Lavington, Kileleshwa, Parklands, Eastleigh, South B, South C'},
            {'name': 'Kiambu', 'slug': 'kiambu', 'description': 'Fast-growing county with modern developments, excellent connectivity to Nairobi, and emerging real estate opportunities.', 'main_towns': 'Thika, Kiambu, Ruiru, Kikuyu, Limuru, Gatundu, Juja, Githunguri, Lari, Kabete'},
            {'name': 'Machakos', 'slug': 'machakos', 'description': 'Emerging real estate market with great potential, known for affordable housing and industrial development.', 'main_towns': 'Machakos, Athi River, Mlolongo, Tala, Kangundo, Matuu, Mavoko, Kathiani, Masinga, Yatta'},
            {'name': 'Kajiado', 'slug': 'kajiado', 'description': 'Prime location for luxury properties and wildlife conservancies, popular for high-end residential developments.', 'main_towns': 'Kajiado, Ongata Rongai, Kitengela, Kiserian, Ngong, Isinya, Loitokitok, Namanga, Mashuru, Magadi'},
            
            # Central Kenya
            {'name': 'Murang\'a', 'slug': 'muranga', 'description': 'Beautiful county with scenic properties, agricultural land, and growing residential developments.', 'main_towns': 'Murang\'a, Kenol, Maragua, Kandara, Kigumo, Kangema, Kiharu, Mathioya, Gatanga'},
            {'name': 'Nyeri', 'slug': 'nyeri', 'description': 'Historic county with agricultural properties, tea estates, and residential developments in the highlands.', 'main_towns': 'Nyeri, Karatina, Othaya, Mukurwe-ini, Tetu, Kieni, Mathira, Nyeri Town'},
            {'name': 'Kirinyaga', 'slug': 'kirinyaga', 'description': 'Agricultural county with rice farming, tea plantations, and emerging residential properties.', 'main_towns': 'Kerugoya, Wanguru, Sagana, Gichugu, Mwea, Ndia, Kirinyaga Central'},
            {'name': 'Nyandarua', 'slug': 'nyandarua', 'description': 'Highland county with agricultural properties, dairy farming, and scenic residential developments.', 'main_towns': 'Ol Kalou, Nyahururu, Ndaragwa, Kinangop, Kipipiri, Ol Joro Orok'},
            
            # Rift Valley
            {'name': 'Nakuru', 'slug': 'nakuru', 'description': 'Major town with diverse property options, industrial developments, and growing residential areas.', 'main_towns': 'Nakuru, Naivasha, Gilgil, Molo, Njoro, Rongai, Subukia, Bahati, Kuresoi'},
            {'name': 'Uasin Gishu', 'slug': 'uasin-gishu', 'description': 'Agricultural powerhouse with large-scale farming properties and growing urban centers.', 'main_towns': 'Eldoret, Burnt Forest, Kesses, Moiben, Soy, Turbo, Wareng, Ainabkoi'},
            {'name': 'Trans Nzoia', 'slug': 'trans-nzoia', 'description': 'Agricultural county with maize farming, wheat production, and rural residential properties.', 'main_towns': 'Kitale, Kiminini, Endebess, Saboti, Kwanza, Cherangany'},
            {'name': 'Elgeyo Marakwet', 'slug': 'elgeyo-marakwet', 'description': 'Highland county with agricultural properties, tourism potential, and scenic residential areas.', 'main_towns': 'Iten, Kapcherop, Kapsowar, Marakwet, Keiyo North, Keiyo South'},
            {'name': 'Nandi', 'slug': 'nandi', 'description': 'Agricultural county with tea farming, dairy production, and emerging residential developments.', 'main_towns': 'Kapsabet, Nandi Hills, Mosoriot, Aldai, Emgwen, Chesumei, Tinderet'},
            {'name': 'Baringo', 'slug': 'baringo', 'description': 'Diverse county with agricultural properties, tourism potential, and rural residential developments.', 'main_towns': 'Kabarnet, Marigat, Mogotio, Eldama Ravine, Baringo Central, Baringo North, Baringo South'},
            {'name': 'Laikipia', 'slug': 'laikipia', 'description': 'Wildlife conservation area with luxury properties, ranches, and high-end residential developments.', 'main_towns': 'Nanyuki, Rumuruti, Nyahururu, Laikipia East, Laikipia North, Laikipia West'},
            {'name': 'Narok', 'slug': 'narok', 'description': 'Tourism hub with wildlife conservancies, luxury lodges, and agricultural properties.', 'main_towns': 'Narok, Kilgoris, Emurua Dikirr, Narok North, Narok South, Narok East, Narok West'},
            {'name': 'Kericho', 'slug': 'kericho', 'description': 'Tea-growing county with agricultural properties, scenic landscapes, and residential developments.', 'main_towns': 'Kericho, Londiani, Kipkelion, Ainamoi, Belgut, Bureti, Sigowet'},
            {'name': 'Bomet', 'slug': 'bomet', 'description': 'Agricultural county with tea farming, dairy production, and rural residential properties.', 'main_towns': 'Bomet, Sotik, Chepalungu, Konoin, Bomet Central, Bomet East'},
            {'name': 'Kakamega', 'slug': 'kakamega', 'description': 'Agricultural county with sugarcane farming, maize production, and growing urban centers.', 'main_towns': 'Kakamega, Mumias, Malava, Lugari, Likuyani, Matungu, Butere, Khwisero'},
            {'name': 'Vihiga', 'slug': 'vihiga', 'description': 'Agricultural county with tea farming, dairy production, and rural residential developments.', 'main_towns': 'Vihiga, Hamisi, Sabatia, Emuhaya, Luanda'},
            {'name': 'Bungoma', 'slug': 'bungoma', 'description': 'Agricultural county with sugarcane farming, maize production, and emerging residential areas.', 'main_towns': 'Bungoma, Webuye, Kimilili, Tongaren, Kanduyi, Sirisia, Kabuchai'},
            {'name': 'Busia', 'slug': 'busia', 'description': 'Border county with agricultural properties, trade opportunities, and rural residential developments.', 'main_towns': 'Busia, Malaba, Nambale, Butula, Samia, Teso North, Teso South'},
            
            # Western Kenya
            {'name': 'Siaya', 'slug': 'siaya', 'description': 'Agricultural county with sugarcane farming, fishing, and rural residential properties.', 'main_towns': 'Siaya, Bondo, Ugenya, Ugunja, Alego Usonga, Gem, Rarieda'},
            {'name': 'Kisumu', 'slug': 'kisumu', 'description': 'Major city with diverse property options, industrial developments, and growing residential areas.', 'main_towns': 'Kisumu, Maseno, Muhoroni, Nyakach, Nyando, Kisumu Central, Kisumu East, Kisumu West'},
            {'name': 'Homa Bay', 'slug': 'homa-bay', 'description': 'Lakeside county with fishing properties, tourism potential, and rural residential developments.', 'main_towns': 'Homa Bay, Kendu Bay, Mbita, Ndhiwa, Rangwe, Suba, Homa Bay Town'},
            {'name': 'Migori', 'slug': 'migori', 'description': 'Agricultural county with sugarcane farming, gold mining, and rural residential properties.', 'main_towns': 'Migori, Awendo, Kuria East, Kuria West, Nyatike, Rongo, Suna East, Suna West'},
            {'name': 'Kisii', 'slug': 'kisii', 'description': 'Agricultural county with tea farming, dairy production, and growing urban centers.', 'main_towns': 'Kisii, Nyamira, Gucha, Gucha South, Marani, Masaba South, Nyaribari Chache, Nyaribari Masaba'},
            {'name': 'Nyamira', 'slug': 'nyamira', 'description': 'Agricultural county with tea farming, dairy production, and rural residential developments.', 'main_towns': 'Nyamira, Borabu, Manga, Masaba North, Nyamira North, Nyamira South'},
            
            # Coast
            {'name': 'Mombasa', 'slug': 'mombasa', 'description': 'Major port city with diverse property options, tourism developments, and growing residential areas.', 'main_towns': 'Mombasa, Changamwe, Jomvu, Kisauni, Likoni, Mvita, Nyali'},
            {'name': 'Kwale', 'slug': 'kwale', 'description': 'Coastal county with beach properties, tourism developments, and rural residential areas.', 'main_towns': 'Kwale, Kinango, Lunga Lunga, Matuga, Msambweni, Samburu'},
            {'name': 'Kilifi', 'slug': 'kilifi', 'description': 'Coastal county with beach properties, tourism potential, and growing residential developments.', 'main_towns': 'Kilifi, Malindi, Watamu, Mtwapa, Kilifi North, Kilifi South, Ganze, Kaloleni, Rabai'},
            {'name': 'Tana River', 'slug': 'tana-river', 'description': 'Agricultural county with irrigation projects, rural properties, and emerging developments.', 'main_towns': 'Hola, Garsen, Bura, Galole, Garsen'},
            {'name': 'Lamu', 'slug': 'lamu', 'description': 'Historic coastal county with heritage properties, tourism developments, and unique residential areas.', 'main_towns': 'Lamu, Mpeketoni, Faza, Kiunga, Lamu East, Lamu West'},
            {'name': 'Taita Taveta', 'slug': 'taita-taveta', 'description': 'Tourism county with wildlife conservancies, luxury lodges, and agricultural properties.', 'main_towns': 'Voi, Taveta, Mwatate, Wundanyi, Taita, Taveta'},
            
            # Eastern Kenya
            {'name': 'Garissa', 'slug': 'garissa', 'description': 'Border county with agricultural properties, trade opportunities, and rural residential developments.', 'main_towns': 'Garissa, Dadaab, Fafi, Ijara, Lagdera, Balambala'},
            {'name': 'Wajir', 'slug': 'wajir', 'description': 'Agricultural county with livestock farming, rural properties, and emerging developments.', 'main_towns': 'Wajir, Buna, Eldas, Habaswein, Tarbaj, Wajir East, Wajir North, Wajir South, Wajir West'},
            {'name': 'Mandera', 'slug': 'mandera', 'description': 'Border county with agricultural properties, trade opportunities, and rural residential areas.', 'main_towns': 'Mandera, Banissa, Lafey, Mandera East, Mandera North, Mandera South, Mandera West'},
            {'name': 'Marsabit', 'slug': 'marsabit', 'description': 'Diverse county with agricultural properties, tourism potential, and rural residential developments.', 'main_towns': 'Marsabit, Laisamis, Moyale, North Horr, Saku'},
            {'name': 'Isiolo', 'slug': 'isiolo', 'description': 'Agricultural county with livestock farming, rural properties, and emerging developments.', 'main_towns': 'Isiolo, Garbatulla, Merti, Isiolo North, Isiolo South'},
            {'name': 'Meru', 'slug': 'meru', 'description': 'Agricultural county with coffee farming, tea production, and growing residential areas.', 'main_towns': 'Meru, Maua, Chuka, Imenti North, Imenti South, Igembe Central, Igembe North, Igembe South, Tigania East, Tigania West'},
            {'name': 'Tharaka Nithi', 'slug': 'tharaka-nithi', 'description': 'Agricultural county with coffee farming, dairy production, and rural residential properties.', 'main_towns': 'Chuka, Maara, Tharaka, Tharaka North, Tharaka South'},
            {'name': 'Embu', 'slug': 'embu', 'description': 'Agricultural county with coffee farming, tea production, and growing residential developments.', 'main_towns': 'Embu, Manyatta, Mbeere North, Mbeere South, Runyenjes'},
            {'name': 'Kitui', 'slug': 'kitui', 'description': 'Agricultural county with livestock farming, rural properties, and emerging developments.', 'main_towns': 'Kitui, Mwingi, Kitui Central, Kitui East, Kitui Rural, Kitui South, Kitui West, Mwingi Central, Mwingi East, Mwingi North, Mwingi West'},
            {'name': 'Makueni', 'slug': 'makueni', 'description': 'Agricultural county with livestock farming, rural properties, and emerging residential areas.', 'main_towns': 'Wote, Makueni, Kibwezi, Kilome, Kaiti, Mbooni, Mukaa'},
        ]
        
        created_count = 0
        updated_count = 0
        
        for county_data in counties_data:
            county, created = County.objects.get_or_create(
                slug=county_data['slug'],
                defaults=county_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created county: {county.name}')
            else:
                # Update existing county with new description and main towns
                county.name = county_data['name']
                county.description = county_data['description']
                county.main_towns = county_data.get('main_towns', '')
                county.save()
                updated_count += 1
                self.stdout.write(f'Updated county: {county.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {len(counties_data)} counties!')
        )
        self.stdout.write(f'Created: {created_count} counties')
        self.stdout.write(f'Updated: {updated_count} counties')
        self.stdout.write(f'Total Counties: {County.objects.count()}')
