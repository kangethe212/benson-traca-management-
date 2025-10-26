from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Property, PropertyMedia, Inquiry, County, Amenity, ManagementRequest, PropertyViewing


class PropertyForm(forms.ModelForm):
    """Form for creating/editing properties"""
    images = forms.FileField(
        required=False,
        help_text="Upload images (JPG, PNG, max 5MB each)",
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'})
    )
    
    class Meta:
        model = Property
        fields = [
            'title', 'property_type', 'county', 'price', 'area',
            'bedrooms', 'bathrooms', 'bathtubs', 'washrooms', 'parking_slots',
            'is_verified', 'virtual_tour_url', 'video_tour', 'description'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'virtual_tour_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'video_tour': forms.FileInput(attrs={'class': 'form-control', 'accept': 'video/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            if field_name not in ['images', 'is_verified', 'description', 'virtual_tour_url', 'video_tour']:
                field.widget.attrs.update({'class': 'form-control'})
            elif field_name == 'is_verified':
                field.widget.attrs.update({'class': 'form-check-input'})
        
        # Configure county dropdown
        self.fields['county'].required = True
        self.fields['county'].queryset = County.objects.filter(is_active=True)
        self.fields['county'].widget.attrs.update({
            'class': 'form-select',
            'placeholder': 'Select County'
        })
        
        # Configure town field
        self.fields['town'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter town or area (e.g., Westlands, Karen, etc.)'
        })
        self.fields['town'].help_text = "Enter the specific town or area within the county"
        
        # Add help text
        self.fields['price'].help_text = "Price in Kenyan Shillings (KSh)"
        self.fields['area'].help_text = "Area in square feet"

    def clean_images(self):
        """Validate uploaded images"""
        images = self.files.getlist('images')
        if not images:
            return images
        
        for image in images:
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError(f"Image {image.name} is too large. Maximum size is 5MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
            if image.content_type not in allowed_types:
                raise ValidationError(f"Image {image.name} is not a valid image format. Use JPG or PNG.")
        
        return images

    def clean_price(self):
        """Validate price is positive"""
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise ValidationError("Price must be greater than zero.")
        return price

    def clean_area(self):
        """Validate area is positive"""
        area = self.cleaned_data.get('area')
        if area and area <= 0:
            raise ValidationError("Area must be greater than zero.")
        return area


class ManagementRequestForm(forms.ModelForm):
    """Form for landlords to submit property management requests"""
    property_type = forms.ChoiceField(
        choices=Property.PROPERTY_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    county = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type county name (e.g., Nairobi, Mombasa, Kisumu, etc.)',
            'autocomplete': 'off'
        }),
        help_text="Enter your county name"
    )
    town = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter town or area (e.g., Westlands, Karen, Nyali, etc.)'
        }),
        help_text="Specific town or area within the county"
    )
    property_images = forms.FileField(
        required=False,
        help_text="Upload property images (JPG, PNG, max 5MB each)",
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*', 'class': 'form-control'})
    )
    property_videos = forms.FileField(
        required=False,
        help_text="Upload property videos (MP4, AVI, max 50MB each)",
        widget=forms.ClearableFileInput(attrs={'accept': 'video/*', 'class': 'form-control'})
    )
    
    class Meta:
        model = ManagementRequest
        fields = [
            'landlord_name', 'landlord_contact', 'rent_amount', 'service_terms',
            'property_type', 'county', 'town', 'property_images', 'property_videos'
        ]
        widgets = {
            'landlord_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'landlord_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254 700 000 000'}),
            'rent_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monthly rent amount in KSh'}),
            'service_terms': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your property and management requirements...'}),
        }

    def clean_landlord_contact(self):
        """Basic phone validation"""
        contact = self.cleaned_data.get('landlord_contact')
        if contact:
            # Remove spaces and special characters for validation
            clean_contact = ''.join(filter(str.isdigit, contact))
            if len(clean_contact) < 9:
                raise ValidationError("Please enter a valid phone number.")
        return contact

    def clean_rent_amount(self):
        """Validate rent amount is positive"""
        rent_amount = self.cleaned_data.get('rent_amount')
        if rent_amount and rent_amount <= 0:
            raise ValidationError("Rent amount must be greater than zero.")
        return rent_amount

    def clean_property_images(self):
        """Validate uploaded property images"""
        images = self.files.getlist('property_images')
        if not images:
            return images
        
        for image in images:
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError(f"Image {image.name} is too large. Maximum size is 5MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
            if image.content_type not in allowed_types:
                raise ValidationError(f"Image {image.name} is not a valid image format. Use JPG or PNG.")
        
        return images

    def clean_property_videos(self):
        """Validate uploaded property videos"""
        videos = self.files.getlist('property_videos')
        if not videos:
            return videos
        
        for video in videos:
            # Check file size (50MB limit)
            if video.size > 50 * 1024 * 1024:
                raise ValidationError(f"Video {video.name} is too large. Maximum size is 50MB.")
            
            # Check file type
            allowed_types = ['video/mp4', 'video/avi', 'video/quicktime']
            if video.content_type not in allowed_types:
                raise ValidationError(f"Video {video.name} is not a valid video format. Use MP4, AVI, or MOV.")
        
        return videos


class InquiryForm(forms.ModelForm):
    """Form for property inquiries"""
    
    class Meta:
        model = Inquiry
        fields = ['name', 'email', 'phone', 'inquiry_type', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
            'inquiry_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Add placeholders
        self.fields['name'].widget.attrs['placeholder'] = 'Your full name'
        self.fields['email'].widget.attrs['placeholder'] = 'your.email@example.com'
        self.fields['phone'].widget.attrs['placeholder'] = '+254 700 000 000'
        self.fields['message'].widget.attrs['placeholder'] = 'Tell us about your inquiry...'

    def clean_phone(self):
        """Basic phone validation"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove spaces and special characters for validation
            clean_phone = ''.join(filter(str.isdigit, phone))
            if len(clean_phone) < 9:
                raise ValidationError("Please enter a valid phone number.")
        return phone


class PropertySearchForm(forms.Form):
    """Advanced property search form"""
    keyword = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title or description...'
        })
    )
    
    county = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type county name (e.g., Nairobi, Mombasa, Kisumu, etc.)',
            'autocomplete': 'off'
        })
    )
    
    property_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Property.PROPERTY_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price (KSh)'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price (KSh)'
        })
    )
    
    bedrooms = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Bedrooms'
        })
    )
    
    bathrooms = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Bathrooms'
        })
    )
    
    parking_slots = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Parking'
        })
    )
    
    is_furnished = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    pet_friendly = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise ValidationError("Minimum price cannot be greater than maximum price.")
        
        return cleaned_data


class ContactForm(forms.Form):
    """General contact form"""
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

    def clean_phone(self):
        """Basic phone validation"""
        phone = self.cleaned_data.get('phone')
        if phone:
            clean_phone = ''.join(filter(str.isdigit, phone))
            if len(clean_phone) < 9:
                raise ValidationError("Please enter a valid phone number.")
        return phone


class PropertyViewingForm(forms.ModelForm):
    """Form for booking property viewings - Daytime only (9 AM - 6 PM)"""
    
    class Meta:
        model = PropertyViewing
        fields = ['name', 'email', 'phone', 'viewing_date', 'viewing_time', 'number_of_people', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254 700 000 000'
            }),
            'viewing_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'viewing_time': forms.Select(attrs={
                'class': 'form-select'
            }),
            'number_of_people': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10',
                'value': '1'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requests or questions? (Optional)'
            })
        }
        help_texts = {
            'viewing_date': 'Select a date for your property viewing',
            'viewing_time': 'Choose a time slot (viewings available 9 AM - 6 PM)',
            'number_of_people': 'How many people will attend the viewing?'
        }
    
    def __init__(self, *args, **kwargs):
        self.property_item = kwargs.pop('property', None)
        super().__init__(*args, **kwargs)
        
        # Make message optional
        self.fields['message'].required = False
        
        # Set minimum date to today
        self.fields['viewing_date'].widget.attrs['min'] = date.today().isoformat()
    
    def clean_viewing_date(self):
        """Validate viewing date is in the future"""
        viewing_date = self.cleaned_data.get('viewing_date')
        
        if viewing_date:
            # Cannot book past dates
            if viewing_date < date.today():
                raise ValidationError("You cannot book viewings for past dates.")
            
            # Cannot book too far in advance (max 30 days)
            max_date = date.today() + timedelta(days=30)
            if viewing_date > max_date:
                raise ValidationError("Viewings can only be booked up to 30 days in advance.")
            
            # No viewings on Sundays (optional - remove if needed)
            # if viewing_date.weekday() == 6:
            #     raise ValidationError("Sorry, we don't schedule viewings on Sundays. Please choose a weekday or Saturday.")
        
        return viewing_date
    
    def clean_phone(self):
        """Validate phone number"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove spaces and special characters
            clean_phone = ''.join(filter(str.isdigit, phone))
            if len(clean_phone) < 9:
                raise ValidationError("Please enter a valid phone number with at least 9 digits.")
        return phone
    
    def clean_number_of_people(self):
        """Validate number of people"""
        number = self.cleaned_data.get('number_of_people')
        if number:
            if number < 1:
                raise ValidationError("At least one person must attend the viewing.")
            if number > 10:
                raise ValidationError("Maximum 10 people per viewing. For larger groups, please contact us directly.")
        return number
    
    def clean(self):
        """Check for time slot availability"""
        cleaned_data = super().clean()
        viewing_date = cleaned_data.get('viewing_date')
        viewing_time = cleaned_data.get('viewing_time')
        
        if self.property_item and viewing_date and viewing_time:
            # Check if this time slot is already booked
            existing_booking = PropertyViewing.objects.filter(
                property_item=self.property_item,
                viewing_date=viewing_date,
                viewing_time=viewing_time,
                status__in=['pending', 'confirmed']
            ).exists()
            
            if existing_booking:
                raise ValidationError(
                    "This time slot is already booked. Please choose another date or time."
                )
        
        return cleaned_data
