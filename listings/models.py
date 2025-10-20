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


class Landlord(models.Model):
    """Property landlords/owners"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landlord_profile')
    phone = models.CharField(max_length=20)
    id_number = models.CharField(max_length=20, blank=True, verbose_name="ID/Passport Number")
    kra_pin = models.CharField(max_length=20, blank=True, verbose_name="KRA PIN")
    
    # Banking details
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account = models.CharField(max_length=50, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)
    
    # Contact details
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Profile
    profile_image = models.ImageField(upload_to='landlords/', blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True, help_text="If representing a company")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False, help_text="Admin must verify landlord")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Landlord"
        verbose_name_plural = "Landlords"
    
    def __str__(self):
        return f"{self.full_name} ({self.user.username})"
    
    @property
    def full_name(self):
        """Get landlord's full name"""
        if self.company_name:
            return f"{self.company_name} ({self.user.get_full_name()})"
        return self.user.get_full_name() or self.user.username
    
    @property
    def total_properties(self):
        """Count total properties owned"""
        return self.properties.count()
    
    @property
    def active_properties(self):
        """Count properties with active leases"""
        return self.properties.filter(leases__status='active').distinct().count()
    
    @property
    def total_tenants(self):
        """Count total tenants across all properties"""
        from listings.models import Tenant
        return Tenant.objects.filter(leases__property_item__landlord=self, leases__status='active').distinct().count()


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
    landlord = models.ForeignKey('Landlord', on_delete=models.CASCADE, related_name='properties', null=True, blank=True, help_text="Property owner/landlord")
    
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


class PropertyViewing(models.Model):
    """Property viewing bookings - Only during daytime hours"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
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


class Tenant(models.Model):
    """Tenant/Renter profile linked to Django User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_profile')
    phone = models.CharField(max_length=20)
    id_number = models.CharField(max_length=20, blank=True, help_text="National ID or Passport number")
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    employer = models.CharField(max_length=200, blank=True)
    
    # Profile
    profile_image = models.ImageField(upload_to='tenants/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False, help_text="KYC verified")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def active_lease(self):
        """Get current active lease"""
        return self.leases.filter(status='active').first()


class Lease(models.Model):
    """Lease/Tenancy agreement"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
    ]
    
    # Tenant and Property
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='leases')
    property_item = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='leases')
    
    # Lease Details
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Additional Charges
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monthly service/maintenance charge")
    utilities_included = models.BooleanField(default=False)
    
    # Documents
    lease_document = models.FileField(upload_to='leases/', blank=True, null=True, help_text="Signed lease agreement")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    deposit_paid = models.BooleanField(default=False)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = "Lease Agreement"
        verbose_name_plural = "Lease Agreements"
    
    def __str__(self):
        return f"{self.tenant.full_name} - {self.property_item.title} ({self.start_date} to {self.end_date})"
    
    @property
    def is_active(self):
        """Check if lease is currently active"""
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date
    
    @property
    def total_monthly_cost(self):
        """Calculate total monthly cost including service charges"""
        return self.monthly_rent + self.service_charge
    
    @property
    def days_remaining(self):
        """Calculate days remaining on lease"""
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return max(0, delta.days)
        return 0


class Payment(models.Model):
    """Rent and other payments"""
    PAYMENT_TYPES = [
        ('rent', 'Rent Payment'),
        ('deposit', 'Security Deposit'),
        ('service', 'Service Charge'),
        ('utility', 'Utility Payment'),
        ('other', 'Other'),
    ]
    
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('card', 'Card'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # Tenant and Lease
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payments')
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments')
    
    # Payment Details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='rent')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='mpesa')
    
    # Transaction Info
    transaction_ref = models.CharField(max_length=100, unique=True, help_text="M-Pesa code or bank ref")
    payment_date = models.DateField(default=timezone.now)
    
    # Period Covered (for rent)
    period_start = models.DateField(null=True, blank=True, help_text="For rent: month start")
    period_end = models.DateField(null=True, blank=True, help_text="For rent: month end")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    is_receipt_sent = models.BooleanField(default=False)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Receipt
    receipt_number = models.CharField(max_length=50, unique=True, editable=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
    
    def __str__(self):
        return f"{self.tenant.full_name} - {self.get_payment_type_display()} - KSh {self.amount}"
    
    def save(self, *args, **kwargs):
        # Generate receipt number if not exists
        if not self.receipt_number:
            import random
            import string
            year = timezone.now().year
            random_str = ''.join(random.choices(string.digits, k=6))
            self.receipt_number = f"TRACA-{year}-{random_str}"
        super().save(*args, **kwargs)
    
    @property
    def is_rent_payment(self):
        return self.payment_type == 'rent'


class MaintenanceRequest(models.Model):
    """Tenant maintenance requests"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Tenant and Property
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='maintenance_requests')
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='maintenance_requests')
    
    # Request Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    category = models.CharField(max_length=50, blank=True, help_text="e.g., Plumbing, Electrical, etc.")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_maintenance')
    
    # Dates
    reported_date = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Communication
    admin_notes = models.TextField(blank=True)
    tenant_feedback = models.TextField(blank=True)
    tenant_rating = models.PositiveIntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-reported_date']
        verbose_name = "Maintenance Request"
        verbose_name_plural = "Maintenance Requests"
    
    def __str__(self):
        return f"{self.title} - {self.tenant.full_name} ({self.get_status_display()})"
    
    @property
    def is_urgent(self):
        return self.priority in ['high', 'urgent']


class TenantDocument(models.Model):
    """Documents for tenants (lease agreements, receipts, etc.)"""
    DOCUMENT_TYPES = [
        ('lease', 'Lease Agreement'),
        ('id', 'ID Copy'),
        ('receipt', 'Payment Receipt'),
        ('utility', 'Utility Bill'),
        ('notice', 'Notice/Communication'),
        ('other', 'Other'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='documents')
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='tenant_documents/')
    description = models.TextField(blank=True)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_tenant_docs')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.tenant.full_name}"


class Message(models.Model):
    """Messages between tenant and admin"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Reply thread
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - From {self.sender.username} to {self.recipient.username}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class TenantService(models.Model):
    """Services offered to tenants by Traca Management"""
    SERVICE_CATEGORIES = [
        ('maintenance', 'Maintenance & Repairs'),
        ('cleaning', 'Cleaning Services'),
        ('utilities', 'Utility Management'),
        ('security', 'Security Services'),
        ('lifestyle', 'Lifestyle Services'),
        ('support', 'Support Services'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=SERVICE_CATEGORIES)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price in KSh (leave blank if free)")
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Featured services appear first")
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', 'category', 'name']
        verbose_name = "Tenant Service"
        verbose_name_plural = "Tenant Services"
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    @property
    def is_free(self):
        return self.price is None or self.price == 0
    
    @property
    def formatted_price(self):
        if self.is_free:
            return "Free"
        return f"KSh {self.price:,.0f}"