from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.urls import reverse


class County(models.Model):
    """Kenyan counties where Traca operates"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Counties"
        ordering = ['name']

    def __str__(self):
        return self.name


class Agent(models.Model):
    """Real estate agents linked to Django User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    phone = models.CharField(max_length=20)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='agents/', blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username


class Amenity(models.Model):
    """Property amenities like pool, gym, etc."""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)  # FontAwesome icon class
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ['name']

    def __str__(self):
        return self.name


class Property(models.Model):
    """Main property model for sale, rent, and management"""
    PROPERTY_TYPES = [
        ('sale', 'Sale'),
        ('rent', 'Rent'),
        ('management', 'Management'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='properties')
    
    # Pricing and Details
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Room Details
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.PositiveIntegerField(null=True, blank=True)
    bathtubs = models.PositiveIntegerField(null=True, blank=True)
    washrooms = models.PositiveIntegerField(null=True, blank=True)
    parking_slots = models.PositiveIntegerField(null=True, blank=True)
    
    # Verification and Media
    is_verified = models.BooleanField(default=False)
    virtual_tour_url = models.URLField(blank=True, null=True)
    video_tour = models.FileField(upload_to='properties/videos/', blank=True, null=True)
    description = models.TextField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.county.name}"

    def get_absolute_url(self):
        return reverse('listings:property_detail', kwargs={'pk': self.pk})

    @property
    def main_image(self):
        """Get the first image as main image"""
        return self.media.filter(media_type='image').first()


class ManagementRequest(models.Model):
    """Property management requests from landlords"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='management_requests')
    landlord_name = models.CharField(max_length=100)
    landlord_contact = models.CharField(max_length=20)
    rent_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    service_terms = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.landlord_name} - {self.property.title}"


class PropertyMedia(models.Model):
    """Property images, videos, and virtual tours"""
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('virtual_tour', 'Virtual Tour'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    file = models.FileField(upload_to='properties/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = "Property Media"

    def __str__(self):
        return f"{self.property.title} - {self.media_type}"

    def save(self, *args, **kwargs):
        # Ensure only one primary image per property
        if self.is_primary and self.media_type == 'image':
            PropertyMedia.objects.filter(
                property=self.property, 
                media_type='image', 
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)


class Inquiry(models.Model):
    """Property inquiries from potential buyers/renters"""
    INQUIRY_TYPES = [
        ('general', 'General Inquiry'),
        ('viewing', 'Request Viewing'),
        ('price', 'Price Inquiry'),
        ('financing', 'Financing Inquiry'),
    ]

    # Contact Information
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Inquiry Details
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES, default='general')
    message = models.TextField()
    
    # Property (nullable for general inquiries)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True, related_name='inquiries')
    
    # Status
    is_read = models.BooleanField(default=False)
    is_responded = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Inquiries"
        ordering = ['-created_at']

    def __str__(self):
        property_name = self.property.title if self.property else "General"
        return f"{self.name} - {property_name}"


class Testimonial(models.Model):
    """Client testimonials"""
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)  # e.g., "Property Owner", "Buyer"
    content = models.TextField()
    rating = models.PositiveIntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='testimonials')
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating} stars"

