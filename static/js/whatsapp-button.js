// WhatsApp Integration JavaScript
class WhatsAppIntegration {
    constructor() {
        // Load configuration
        this.config = window.WhatsAppConfig || {
            phoneNumber: '254700000000',
            messages: {
                default: 'Hello! I am interested in your property management services.',
                propertyInquiry: 'Hi! I\'m interested in this property. Could you provide more details?',
                maintenanceRequest: 'Hi! I need to report a maintenance issue. Please contact me to arrange a visit.',
                rentPayment: 'Hi! I have a question about my rent payment. Could you please help me?',
                generalInquiry: 'Hello! I have a question about your services.'
            }
        };
        
        this.phoneNumber = this.config.phoneNumber;
        this.defaultMessage = this.config.messages.default;
        this.init();
    }

    init() {
        this.createWhatsAppButton();
        this.createMessageForm();
        this.bindEvents();
    }

    createWhatsAppButton() {
        const whatsappButton = document.createElement('a');
        whatsappButton.href = '#';
        whatsappButton.className = 'whatsapp-float';
        whatsappButton.id = 'whatsapp-float';
        whatsappButton.innerHTML = `
            <i class="fab fa-whatsapp"></i>
            <div class="whatsapp-tooltip">Chat with us on WhatsApp</div>
        `;
        
        document.body.appendChild(whatsappButton);
    }

    createMessageForm() {
        const messageForm = document.createElement('div');
        messageForm.className = 'whatsapp-message-form';
        messageForm.id = 'whatsapp-message-form';
        messageForm.innerHTML = `
            <button class="close-btn" onclick="whatsappIntegration.closeForm()">&times;</button>
            <h4>Send us a message</h4>
            <form id="whatsapp-form">
                <input type="text" id="whatsapp-name" placeholder="Your name" required>
                <input type="tel" id="whatsapp-phone" placeholder="Your phone number" required>
                <textarea id="whatsapp-message" placeholder="Your message" required>${this.defaultMessage}</textarea>
                <button type="submit">Send via WhatsApp</button>
            </form>
        `;
        
        document.body.appendChild(messageForm);
    }

    bindEvents() {
        const whatsappButton = document.getElementById('whatsapp-float');
        const whatsappForm = document.getElementById('whatsapp-form');

        // Button click events
        whatsappButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleForm();
        });

        // Form submission
        whatsappForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Close form when clicking outside
        document.addEventListener('click', (e) => {
            const form = document.getElementById('whatsapp-message-form');
            const button = document.getElementById('whatsapp-float');
            
            if (!form.contains(e.target) && !button.contains(e.target)) {
                this.closeForm();
            }
        });

        // Auto-hide form after 30 seconds of inactivity
        this.setAutoHideTimer();
    }

    toggleForm() {
        const form = document.getElementById('whatsapp-message-form');
        const button = document.getElementById('whatsapp-float');
        
        if (form.classList.contains('show')) {
            this.closeForm();
        } else {
            this.openForm();
        }
    }

    openForm() {
        const form = document.getElementById('whatsapp-message-form');
        const button = document.getElementById('whatsapp-float');
        
        form.classList.add('show');
        button.classList.add('pulse');
        
        // Focus on name field
        setTimeout(() => {
            document.getElementById('whatsapp-name').focus();
        }, 300);
        
        this.setAutoHideTimer();
    }

    closeForm() {
        const form = document.getElementById('whatsapp-message-form');
        const button = document.getElementById('whatsapp-float');
        
        form.classList.remove('show');
        button.classList.remove('pulse');
    }

    sendMessage() {
        const name = document.getElementById('whatsapp-name').value.trim();
        const phone = document.getElementById('whatsapp-phone').value.trim();
        const message = document.getElementById('whatsapp-message').value.trim();

        if (!name || !phone || !message) {
            alert('Please fill in all fields');
            return;
        }

        // Format phone number (remove spaces, add country code if needed)
        const formattedPhone = this.formatPhoneNumber(phone);
        
        // Create WhatsApp URL
        const encodedMessage = encodeURIComponent(
            `Hello! My name is ${name}.\n\n${message}\n\nContact me at: ${phone}`
        );
        
        const whatsappUrl = `https://wa.me/${formattedPhone}?text=${encodedMessage}`;
        
        // Open WhatsApp
        window.open(whatsappUrl, '_blank');
        
        // Close form and show success message
        this.closeForm();
        this.showSuccessMessage();
        
        // Reset form
        document.getElementById('whatsapp-form').reset();
        document.getElementById('whatsapp-message').value = this.defaultMessage;
    }

    formatPhoneNumber(phone) {
        // Remove all non-digit characters
        let cleaned = phone.replace(/\D/g, '');
        
        // Add country code if not present
        if (cleaned.startsWith('0')) {
            cleaned = '254' + cleaned.substring(1);
        } else if (!cleaned.startsWith('254')) {
            cleaned = '254' + cleaned;
        }
        
        return cleaned;
    }

    showSuccessMessage() {
        const button = document.getElementById('whatsapp-float');
        const originalTooltip = button.querySelector('.whatsapp-tooltip');
        
        // Change tooltip text temporarily
        originalTooltip.textContent = 'Message sent! Check WhatsApp';
        originalTooltip.style.backgroundColor = '#25d366';
        
        // Reset after 3 seconds
        setTimeout(() => {
            originalTooltip.textContent = 'Chat with us on WhatsApp';
            originalTooltip.style.backgroundColor = '#333';
        }, 3000);
    }

    setAutoHideTimer() {
        // Clear existing timer
        if (this.autoHideTimer) {
            clearTimeout(this.autoHideTimer);
        }
        
        // Set new timer
        this.autoHideTimer = setTimeout(() => {
            this.closeForm();
        }, 30000); // 30 seconds
    }

    // Method to send quick message (for property inquiries)
    sendQuickMessage(propertyTitle = '', propertyPrice = '') {
        const message = propertyTitle && propertyPrice 
            ? `Hi! I'm interested in the property "${propertyTitle}" (${propertyPrice}). Could you provide more details?`
            : this.defaultMessage;
            
        const encodedMessage = encodeURIComponent(message);
        const whatsappUrl = `https://wa.me/${this.phoneNumber}?text=${encodedMessage}`;
        
        window.open(whatsappUrl, '_blank');
    }

    // Method to send maintenance request
    sendMaintenanceRequest(propertyAddress = '') {
        const message = propertyAddress 
            ? `Hi! I need to report a maintenance issue at ${propertyAddress}. Please contact me to arrange a visit.`
            : 'Hi! I need to report a maintenance issue. Please contact me to arrange a visit.';
            
        const encodedMessage = encodeURIComponent(message);
        const whatsappUrl = `https://wa.me/${this.phoneNumber}?text=${encodedMessage}`;
        
        window.open(whatsappUrl, '_blank');
    }

    // Method to send rent payment inquiry
    sendRentPaymentInquiry() {
        const message = 'Hi! I have a question about my rent payment. Could you please help me?';
        const encodedMessage = encodeURIComponent(message);
        const whatsappUrl = `https://wa.me/${this.phoneNumber}?text=${encodedMessage}`;
        
        window.open(whatsappUrl, '_blank');
    }
}

// Initialize WhatsApp integration when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.whatsappIntegration = new WhatsAppIntegration();
});

// Global functions for easy access
function openWhatsApp() {
    window.whatsappIntegration.toggleForm();
}

function sendPropertyInquiry(propertyTitle, propertyPrice) {
    window.whatsappIntegration.sendQuickMessage(propertyTitle, propertyPrice);
}

function sendMaintenanceRequest(propertyAddress) {
    window.whatsappIntegration.sendMaintenanceRequest(propertyAddress);
}

function sendRentPaymentInquiry() {
    window.whatsappIntegration.sendRentPaymentInquiry();
}
