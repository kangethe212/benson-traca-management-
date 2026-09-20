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
    main_towns = models.TextField(blank=True, help_text="Comma-separated list of main towns in this county")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Counties"
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active', 'name']),
            models.Index(fields=['slug']),
        ]

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
        indexes = [
            models.Index(fields=['is_active', 'is_verified']),
            models.Index(fields=['created_at']),
        ]

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
        indexes = [
            models.Index(fields=['is_active', 'name']),
        ]
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
    town = models.CharField(max_length=100, blank=True, help_text="Specific town or area within the county")
    
    # Pricing and Details
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Room Details
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.PositiveIntegerField(null=True, blank=True)
    bathtubs = models.PositiveIntegerField(null=True, blank=True)
    washrooms = models.PositiveIntegerField(null=True, blank=True)
    parking_slots = models.PositiveIntegerField(null=True, blank=True)
    
    # Property Features
    is_furnished = models.BooleanField(default=False, help_text="Is the property furnished?")
    pet_friendly = models.BooleanField(default=False, help_text="Are pets allowed?")
    near_school = models.BooleanField(default=False, help_text="Is property near a school?")
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='properties')
    
    # Verification and Media
    is_verified = models.BooleanField(default=False)
    virtual_tour_url = models.URLField(blank=True, null=True)
    video_tour = models.FileField(upload_to='properties/videos/', blank=True, null=True)
    description = models.TextField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['price']),
            models.Index(fields=['county']),
            models.Index(fields=['property_type']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['created_at']),
        ]
        verbose_name_plural = "Properties"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.county.name}"

    def get_absolute_url(self):
        return reverse('listings:property_detail', kwargs={'pk': self.pk})

    @property
    def main_image(self):
        """Get the first image with an actual file as main image"""
        for media in self.media.filter(media_type='image').order_by('-is_primary', 'order', 'id'):
            if media.file and media.file.name:
                return media
        return None

    @property
    def main_image_url(self):
        """Return a usable image URL for the main property image, with a default fallback."""
        media = self.main_image
        if media and media.file and media.file.name:
            return media.file.url
        return '/static/images/default_property.jpg'

    @property
    def has_media(self):
        """Whether the listing has at least one image available."""
        return bool(self.main_image and self.main_image.file and self.main_image.file.name)


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
        indexes = [
            models.Index(fields=['property', 'media_type', 'is_primary']),
            models.Index(fields=['property', 'order']),
        ]
        ordering = ['order']
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
        indexes = [
            models.Index(fields=['is_read', 'created_at']),
            models.Index(fields=['property', 'created_at']),
        ]
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
        indexes = [
            models.Index(fields=['is_approved', 'is_featured']),
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating} stars"


class PropertyViewing(models.Model):
    """Property viewing bookings - Only during daytime hours"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    TIME_SLOTS = [
        ('09:00', '9:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('12:00', '12:00 PM'),
        ('13:00', '1:00 PM'),
        ('14:00', '2:00 PM'),
        ('15:00', '3:00 PM'),
        ('16:00', '4:00 PM'),
        ('17:00', '5:00 PM'),
        ('18:00', '6:00 PM'),
    ]
    
    # Property and User Information
    property_item = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='viewings')
    
    # Customer Details
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Viewing Details
    viewing_date = models.DateField()
    viewing_time = models.CharField(max_length=5, choices=TIME_SLOTS, help_text="Viewings only during daytime (9 AM - 6 PM)")
    
    # Additional Information
    message = models.TextField(blank=True, help_text="Any special requests or questions")
    number_of_people = models.PositiveIntegerField(default=1, help_text="How many people will attend the viewing")
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_notified = models.BooleanField(default=False, help_text="Has admin been notified?")
    confirmation_sent = models.BooleanField(default=False, help_text="Has confirmation been sent to customer?")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['property_item', 'viewing_date', 'status']),
            models.Index(fields=['viewing_date', 'status']),
        ]
        verbose_name = "Property Viewing"
        verbose_name_plural = "Property Viewings"
        ordering = ['viewing_date', 'viewing_time']
        unique_together = ['property_item', 'viewing_date', 'viewing_time']  # Prevent double-booking
    
    def __str__(self):
        return f"{self.property_item.title} - {self.name} on {self.viewing_date} at {self.get_viewing_time_display()}"
    
    @property
    def is_upcoming(self):
        """Check if viewing is in the future"""
        from datetime import datetime, time
        viewing_datetime = datetime.combine(self.viewing_date, time.fromisoformat(self.viewing_time))
        # Make viewing_datetime timezone-aware
        viewing_datetime = timezone.make_aware(viewing_datetime)
        return viewing_datetime > timezone.now()
    
    @property
    def is_today(self):
        """Check if viewing is today"""
        return self.viewing_date == timezone.now().date()
    
    def get_absolute_url(self):
        return reverse('listings:viewing_detail', kwargs={'pk': self.pk})


class TeamMember(models.Model):
    """Team members for the about page"""
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='team/', help_text="Upload team member photo (120x120px recommended)")
    order = models.PositiveIntegerField(default=0, help_text="Display order (0 = first)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.name} - {self.title}"