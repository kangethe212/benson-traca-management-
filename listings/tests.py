from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import County, Property, ManagementRequest


class PropertyViewsTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create a county
        self.county = County.objects.create(
            name="Nairobi",
            slug="nairobi",
            description="Capital city of Kenya"
        )
        
        # Create a property
        self.property = Property.objects.create(
            title="Test Property",
            property_type="sale",
            county=self.county,
            price=5000000,
            bedrooms=3,
            bathrooms=2,
            description="A beautiful test property"
        )
        
        # Create a superuser for admin tests
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        
        self.client = Client()

    def test_home_view(self):
        """Test that home view returns 200"""
        response = self.client.get(reverse('listings:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Traca Management Services')

    def test_properties_list_view(self):
        """Test that properties list view returns 200 and contains property"""
        response = self.client.get(reverse('listings:properties_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.property.title)

    def test_property_detail_view(self):
        """Test that property detail view returns 200 and contains property details"""
        response = self.client.get(reverse('listings:property_detail', kwargs={'pk': self.property.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.property.title)
        self.assertContains(response, str(self.property.price))

    def test_management_request_view_get(self):
        """Test that management request form loads correctly"""
        response = self.client.get(reverse('listings:management_request'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Property Management Request')

    def test_management_request_view_post(self):
        """Test that management request form submission works"""
        data = {
            'landlord_name': 'John Doe',
            'landlord_contact': '+254700000000',
            'property_type': 'rent',
            'county': self.county.id,
            'rent_amount': 50000,
            'service_terms': 'Need property management services'
        }
        response = self.client.post(reverse('listings:management_request'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        
        # Check that management request was created
        self.assertTrue(ManagementRequest.objects.filter(landlord_name='John Doe').exists())

    def test_verified_badge_display(self):
        """Test that verified badge appears for verified properties"""
        # Make property verified
        self.property.is_verified = True
        self.property.save()
        
        response = self.client.get(reverse('listings:property_detail', kwargs={'pk': self.property.pk}))
        self.assertContains(response, 'Verified Property')

    def test_property_search_filtering(self):
        """Test that property search filtering works"""
        # Create another property with different type
        Property.objects.create(
            title="Rental Property",
            property_type="rent",
            county=self.county,
            price=50000,
            description="A rental property"
        )
        
        # Test filtering by property type
        response = self.client.get(reverse('listings:properties_list') + '?property_type=sale')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Property')
        self.assertNotContains(response, 'Rental Property')

    def test_management_requests_list_admin_access(self):
        """Test that management requests list requires admin access"""
        # Test without login (should redirect)
        response = self.client.get(reverse('listings:management_requests_list'))
        self.assertEqual(response.status_code, 302)
        
        # Test with admin login
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('listings:management_requests_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Property Management Requests')


class PropertyModelTestCase(TestCase):
    def setUp(self):
        self.county = County.objects.create(
            name="Kiambu",
            slug="kiambu",
            description="Kiambu County"
        )

    def test_property_creation(self):
        """Test that property can be created with all required fields"""
        property_obj = Property.objects.create(
            title="Test Property",
            property_type="sale",
            county=self.county,
            price=10000000,
            bedrooms=4,
            bathrooms=3,
            description="A test property"
        )
        
        self.assertEqual(property_obj.title, "Test Property")
        self.assertEqual(property_obj.property_type, "sale")
        self.assertEqual(property_obj.county, self.county)
        self.assertEqual(property_obj.price, 10000000)
        self.assertFalse(property_obj.is_verified)  # Default should be False

    def test_property_str_representation(self):
        """Test property string representation"""
        property_obj = Property.objects.create(
            title="Test Property",
            property_type="sale",
            county=self.county,
            description="A test property"
        )
        
        expected_str = f"Test Property - {self.county.name}"
        self.assertEqual(str(property_obj), expected_str)

    def test_management_request_creation(self):
        """Test that management request can be created"""
        property_obj = Property.objects.create(
            title="Test Property",
            property_type="rent",
            county=self.county,
            description="A test property"
        )
        
        request_obj = ManagementRequest.objects.create(
            property=property_obj,
            landlord_name="Jane Doe",
            landlord_contact="+254700000001",
            rent_amount=75000,
            service_terms="Need property management"
        )
        
        self.assertEqual(request_obj.landlord_name, "Jane Doe")
        self.assertEqual(request_obj.property, property_obj)
        self.assertEqual(request_obj.status, "pending")  # Default status