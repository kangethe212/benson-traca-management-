"""
Enhanced models with database indexes for optimal performance
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
from django.urls import reverse
from django.conf import settings
import uuid


class County(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    main_towns = models.TextField(help_text="Comma-separated list of main towns")
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


class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active', 'name']),
        ]

    def __str__(self):
        return self.name


class Landlord(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landlord_profile')
    phone = models.CharField(max_length=20, validators=[
        RegexValidator(r'^\+?1?\d{9,15}$', 'Phone number must be entered in the format: +254700000000')
    ])
    id_number = models.CharField(max_length=50, blank=True)
    kra_pin = models.CharField(max_length=50, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Banking details
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    
    # Company information
    company_name = models.CharField(max_length=200, blank=True)
    company_registration_number = models.CharField(max_length=50, blank=True)
    profile_image = models.ImageField(upload_to='landlord_profiles/', blank=True, null=True)
    
    # Verification and status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    verification_documents = models.FileField(upload_to='verification_docs/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_verified', 'is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['county']),
        ]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def total_properties(self):
        return self.properties.count()

    @property
    def total_tenants(self):
        from django.db.models import Count
        return Property.objects.filter(landlord=self).aggregate(
            total=Count('leases__tenant', distinct=True)
        )['total'] or 0


class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_profile')
    phone = models.CharField(max_length=20, validators=[
        RegexValidator(r'^\+?1?\d{9,15}$', 'Phone number must be entered in the format: +254700000000')
    ])
    id_number = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True)
    employer = models.CharField(max_length=200, blank=True)
    
    # Address
    address = models.TextField()
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    
    # Documents
    profile_picture = models.ImageField(upload_to='tenant_profiles/', blank=True, null=True)
    id_document = models.FileField(upload_to='tenant_docs/', blank=True, null=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'is_verified']),
            models.Index(fields=['county']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def active_lease(self):
        return self.leases.filter(status='active').first()


class Property(models.Model):
    PROPERTY_TYPES = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
    ]
    
    PROPERTY_CATEGORIES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('townhouse', 'Townhouse'),
        ('land', 'Land'),
        ('commercial', 'Commercial'),
        ('office', 'Office'),
        ('shop', 'Shop'),
        ('warehouse', 'Warehouse'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
        ('off_market', 'Off Market'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPES)
    category = models.CharField(max_length=20, choices=PROPERTY_CATEGORIES, default='apartment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Location
    county = models.ForeignKey(County, on_delete=models.PROTECT)
    town = models.CharField(max_length=100)
    address = models.TextField()
    coordinates = models.CharField(max_length=100, blank=True, help_text="GPS coordinates")
    
    # Pricing
    price = models.DecimalField(max_digits=15, decimal_places=2)
    price_type = models.CharField(max_length=10, choices=PROPERTY_TYPES, default=property_type)
    
    # Property Details
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.PositiveIntegerField(default=0)
    bathtubs = models.PositiveIntegerField(default=0)
    washrooms = models.PositiveIntegerField(default=0)
    square_feet = models.PositiveIntegerField(default=0)
    parking_slots = models.PositiveIntegerField(default=0)
    
    # Features
    is_furnished = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    virtual_tour_url = models.URLField(blank=True)
    video_tour = models.FileField(upload_to='property_videos/', blank=True, null=True)
    
    # Landlord
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE, related_name='properties')
    
    # Amenities
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='properties')
    
    # Media
    main_image = models.OneToOneField('PropertyMedia', on_delete=models.SET_NULL, null=True, blank=True, related_name='main_property')
    
    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    inquiry_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['price']),
            models.Index(fields=['county']),
            models.Index(fields=['property_type']),
            models.Index(fields=['status']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['created_at']),
            models.Index(fields=['featured']),
            models.Index(fields=['property_type', 'status', 'is_verified', 'price']),
            models.Index(fields=['county', 'town', 'status']),
            models.Index(fields=['price', 'property_type']),
            models.Index(fields=['status', 'is_verified', 'created_at']),
            models.Index(fields=['slug']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('listings:property_detail', kwargs={'pk': self.pk})

    @property
    def media_files(self):
        return self.media.all().order_by('order')

    @property
    def primary_image(self):
        return self.main_image or self.media.filter(is_primary=True).first() or self.media.first()


class PropertyMedia(models.Model):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to='property_media/')
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

    def __str__(self):
        return f"{self.property.title} - {self.media_type}"


class Lease(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
        ('pending', 'Pending'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='leases')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='leases')
    landlord = models.ForeignKey(Landlord, on_delete=models.CASCADE, related_name='leases')
    
    # Financial terms
    rent_amount = models.DecimalField(max_digits=15, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_frequency = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ], default='monthly')
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Terms
    terms_conditions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'property', 'tenant']),
            models.Index(fields=['start_date', 'end_date', 'status']),
        ]

    def __str__(self):
        return f"Lease for {self.property.title} - {self.tenant}"


class Payment(models.Model):
    PAYMENT_TYPES = [
        ('rent', 'Rent'),
        ('deposit', 'Deposit'),
        ('maintenance', 'Maintenance'),
        ('utility', 'Utility'),
        ('other', 'Other'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('card', 'Card'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('partial', 'Partial'),
        ('cancelled', 'Cancelled'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payments')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    
    # Payment details
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    # Dates
    payment_date = models.DateField()
    due_date = models.DateField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, blank=True)
    receipt_number = models.CharField(max_length=100, unique=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'payment_date']),
            models.Index(fields=['tenant', 'payment_date']),
            models.Index(fields=['property', 'payment_date']),
        ]
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment {self.receipt_number or self.id} - KES {self.amount}"


class MaintenanceRequest(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CATEGORY_CHOICES = [
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('hvac', 'HVAC'),
        ('structural', 'Structural'),
        ('pest_control', 'Pest Control'),
        ('landscaping', 'Landscaping'),
        ('cleaning', 'Cleaning'),
        ('other', 'Other'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='maintenance_requests')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='maintenance_requests')
    
    # Request details
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Resolution
    assigned_to = models.CharField(max_length=200, blank=True)
    resolution_notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'priority', 'created_at']),
            models.Index(fields=['property', 'status']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.property.title}"


class Message(models.Model):
    MESSAGE_TYPES = [
        ('inquiry', 'Inquiry'),
        ('notification', 'Notification'),
        ('alert', 'Alert'),
        ('reminder', 'Reminder'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    
    # Message content
    subject = models.CharField(max_length=200)
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    
    # Related objects
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['recipient', 'created_at', 'status']),
            models.Index(fields=['sender', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.recipient.get_full_name() if self.recipient else 'System'}"


class Inquiry(models.Model):
    INQUIRY_TYPES = [
        ('property', 'Property Inquiry'),
        ('general', 'General Inquiry'),
        ('maintenance', 'Maintenance Request'),
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Inquiry details
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES)
    message = models.TextField()
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries', null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_responded = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['property', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry from {self.name} - {self.inquiry_type}"


class PropertyViewing(models.Model):
    VIEWING_TIMES = [
        ('morning', 'Morning (9AM - 12PM)'),
        ('afternoon', 'Afternoon (12PM - 4PM)'),
        ('evening', 'Evening (4PM - 6PM)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='viewings')
    
    # Customer details
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Viewing details
    viewing_date = models.DateField()
    viewing_time = models.CharField(max_length=20, choices=VIEWING_TIMES)
    number_of_people = models.PositiveIntegerField(default=1)
    message = models.TextField(blank=True)
    
    # Status and notifications
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_notified = models.BooleanField(default=False)
    confirmation_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['property', 'viewing_date', 'status']),
            models.Index(fields=['viewing_date', 'status']),
        ]
        ordering = ['-viewing_date', '-viewing_time']

    def __str__(self):
        return f"Viewing for {self.property.title} on {self.viewing_date}"

    @property
    def is_today(self):
        return self.viewing_date == timezone.now().date()

    @property
    def is_upcoming(self):
        return self.viewing_date > timezone.now().date()
