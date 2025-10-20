// WhatsApp Configuration
// Update this file with your actual WhatsApp number and customize messages

window.WhatsAppConfig = {
    // Your WhatsApp number (without + sign, with country code)
    // Example: '254700000000' for Kenya
    phoneNumber: '254796465104',
    
    // Default messages for different scenarios
    messages: {
        default: 'Hello! I am interested in your property management services.',
        propertyInquiry: 'Hi! I\'m interested in this property. Could you provide more details?',
        maintenanceRequest: 'Hi! I need to report a maintenance issue. Please contact me to arrange a visit.',
        rentPayment: 'Hi! I have a question about my rent payment. Could you please help me?',
        generalInquiry: 'Hello! I have a question about your services.'
    },
    
    // Business hours (optional - for showing availability)
    businessHours: {
        enabled: false,
        timezone: 'Africa/Nairobi',
        hours: {
            monday: '8:00-17:00',
            tuesday: '8:00-17:00',
            wednesday: '8:00-17:00',
            thursday: '8:00-17:00',
            friday: '8:00-17:00',
            saturday: '9:00-13:00',
            sunday: 'closed'
        }
    },
    
    // Auto-reply settings (optional)
    autoReply: {
        enabled: false,
        message: 'Thank you for contacting Traca Management Services. We will get back to you shortly.'
    }
};
