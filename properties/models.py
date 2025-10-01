from django.db import models
from django.urls import reverse

class Property(models.Model):
    """Property model for Traca Management Services Ltd"""
    
    # Basic Information
    title = models.CharField(max_length=200, help_text="Property title")
    description = models.TextField(blank=True, help_text="Property description")
    
    # Location
    location = models.CharField(max_length=100, help_text="Specific location/area")
    county = models.CharField(max_length=50, help_text="County in Kenya")
    
    # Property Details
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Property price in KES")
    bedrooms = models.PositiveIntegerField(help_text="Number of bedrooms")
    bathrooms = models.PositiveIntegerField(help_text="Number of bathrooms")
    parking = models.PositiveIntegerField(default=0, help_text="Number of parking spaces")
    area = models.DecimalField(max_digits=8, decimal_places=2, help_text="Area in square meters")
    
    # Property Type
    PROPERTY_TYPES = [
        ('home', 'Home'),
        ('rental', 'Rental'),
        ('office', 'Office'),
        ('gated_community', 'Gated Community'),
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('land', 'Land'),
        ('commercial', 'Commercial'),
    ]
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='home')
    
    # Images
    main_image = models.ImageField(upload_to='properties/', help_text="Main property image")
    image_2 = models.ImageField(upload_to='properties/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='properties/', blank=True, null=True)
    
    # Status
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
        ('pending', 'Pending'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Featured property
    is_featured = models.BooleanField(default=False, help_text="Show on homepage")
    
    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.county}"
    
    def get_absolute_url(self):
        return reverse('property_detail', kwargs={'pk': self.pk})
    
    def formatted_price(self):
        """Format price with commas"""
        return f"KES {self.price:,.0f}"
    
    def get_property_type_display_name(self):
        """Get display name for property type"""
        return dict(self.PROPERTY_TYPES)[self.property_type]