"""
Unified Notification Service for Traca Management Services
Handles Email, SMS, and WhatsApp notifications
"""

import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import requests

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Unified notification service that sends messages via Email, SMS, and WhatsApp
    """
    
    @staticmethod
    def send_email(subject, message, recipient_list, html_message=None, from_email=None):
        """
        Send email notification
        
        Args:
            subject: Email subject
            message: Plain text message
            recipient_list: List of recipient email addresses
            html_message: Optional HTML version of message
            from_email: Optional sender email (defaults to DEFAULT_FROM_EMAIL)
        
        Returns:
            Boolean indicating success
        """
        if not settings.ENABLE_EMAIL_NOTIFICATIONS:
            logger.info("Email notifications are disabled")
            return False
            
        try:
            from_email = from_email or settings.DEFAULT_FROM_EMAIL
            
            if html_message:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=from_email,
                    to=recipient_list
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
            else:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=recipient_list,
                    fail_silently=False,
                )
            
            logger.info(f"Email sent successfully to {recipient_list}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    @staticmethod
    def send_sms(phone_number, message):
        """
        Send SMS notification via Twilio
        
        Args:
            phone_number: Recipient phone number (with country code)
            message: SMS message content
        
        Returns:
            Boolean indicating success
        """
        if not settings.ENABLE_SMS_NOTIFICATIONS:
            logger.info("SMS notifications are disabled")
            return False
            
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            logger.warning("Twilio credentials not configured")
            return False
        
        try:
            from twilio.rest import Client
            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            message = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            logger.info(f"SMS sent successfully to {phone_number}. SID: {message.sid}")
            return True
            
        except ImportError:
            logger.error("Twilio library not installed. Run: pip install twilio")
            return False
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False
    
    @staticmethod
    def send_whatsapp(phone_number, message, template_name=None):
        """
        Send WhatsApp message via WhatsApp Business API
        
        Args:
            phone_number: Recipient phone number (with country code)
            message: WhatsApp message content
            template_name: Optional WhatsApp template name
        
        Returns:
            Boolean indicating success
        """
        if not settings.ENABLE_WHATSAPP_NOTIFICATIONS:
            logger.info("WhatsApp notifications are disabled")
            return False
            
        if not settings.WHATSAPP_API_TOKEN:
            logger.warning("WhatsApp API token not configured")
            return False
        
        try:
            url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER}/messages"
            
            headers = {
                "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            logger.info(f"WhatsApp message sent successfully to {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            return False
    
    @classmethod
    def send_notification(cls, recipient, subject, message, channels=['email'], **kwargs):
        """
        Send notification across multiple channels
        
        Args:
            recipient: Dict with contact info {'email': '', 'phone': ''}
            subject: Notification subject/title
            message: Notification message
            channels: List of channels to use ['email', 'sms', 'whatsapp']
            **kwargs: Additional parameters (html_message, template_name, etc.)
        
        Returns:
            Dict with status for each channel
        """
        results = {}
        
        if 'email' in channels and recipient.get('email'):
            results['email'] = cls.send_email(
                subject=subject,
                message=message,
                recipient_list=[recipient['email']],
                html_message=kwargs.get('html_message')
            )
        
        if 'sms' in channels and recipient.get('phone'):
            results['sms'] = cls.send_sms(
                phone_number=recipient['phone'],
                message=f"{subject}\n\n{message}"
            )
        
        if 'whatsapp' in channels and recipient.get('phone'):
            results['whatsapp'] = cls.send_whatsapp(
                phone_number=recipient['phone'],
                message=f"*{subject}*\n\n{message}",
                template_name=kwargs.get('template_name')
            )
        
        return results


class PropertyNotifications:
    """
    Property-specific notification templates
    """
    
    @staticmethod
    def notify_new_inquiry(property_obj, customer_info):
        """Send notification for new property inquiry"""
        subject = f"New Inquiry: {property_obj.title}"
        
        message = f"""
        New property inquiry received!
        
        Property: {property_obj.title}
        Customer: {customer_info.get('name', 'N/A')}
        Phone: {customer_info.get('phone', 'N/A')}
        Email: {customer_info.get('email', 'N/A')}
        Message: {customer_info.get('message', 'N/A')}
        """
        
        # Send to admin
        admin_recipient = {
            'email': settings.ADMINS[0][1],
            'phone': settings.WHATSAPP_PHONE_NUMBER
        }
        
        NotificationService.send_notification(
            recipient=admin_recipient,
            subject=subject,
            message=message,
            channels=['email']
        )
        
        # Send confirmation to customer
        if customer_info.get('email'):
            customer_message = f"""
            Dear {customer_info.get('name', 'Customer')},
            
            Thank you for your inquiry about {property_obj.title}.
            
            We have received your request and will get back to you within 24 hours.
            
            Best regards,
            Traca Management Services
            """
            
            NotificationService.send_email(
                subject=f"Inquiry Confirmation - {property_obj.title}",
                message=customer_message,
                recipient_list=[customer_info['email']]
            )
    
    @staticmethod
    def notify_maintenance_request(request_obj):
        """Send notification for maintenance request"""
        subject = "New Maintenance Request"
        
        message = f"""
        New maintenance request received!
        
        Requester: {request_obj.name}
        Phone: {request_obj.phone}
        Email: {request_obj.email}
        Issue: {request_obj.description}
        Priority: {request_obj.get_priority_display() if hasattr(request_obj, 'get_priority_display') else 'Normal'}
        """
        
        admin_recipient = {
            'email': settings.ADMINS[0][1],
            'phone': settings.WHATSAPP_PHONE_NUMBER
        }
        
        NotificationService.send_notification(
            recipient=admin_recipient,
            subject=subject,
            message=message,
            channels=['email', 'sms']
        )
    
    @staticmethod
    def notify_rent_payment(payment_info):
        """Send notification for rent payment"""
        subject = f"Rent Payment Received - {payment_info.get('tenant_name')}"
        
        message = f"""
        Rent payment confirmation
        
        Tenant: {payment_info.get('tenant_name')}
        Amount: KES {payment_info.get('amount', 0):,.2f}
        Property: {payment_info.get('property_name')}
        Payment Method: {payment_info.get('payment_method', 'N/A')}
        Reference: {payment_info.get('reference', 'N/A')}
        """
        
        # Send to tenant
        if payment_info.get('tenant_email'):
            tenant_recipient = {
                'email': payment_info['tenant_email'],
                'phone': payment_info.get('tenant_phone')
            }
            
            NotificationService.send_notification(
                recipient=tenant_recipient,
                subject="Payment Confirmation",
                message=message,
                channels=['email', 'sms']
            )


# Convenience functions for common notifications
def send_email_notification(subject, message, recipient_email, html_message=None):
    """Quick function to send email"""
    return NotificationService.send_email(subject, message, [recipient_email], html_message)


def send_sms_notification(phone_number, message):
    """Quick function to send SMS"""
    return NotificationService.send_sms(phone_number, message)


def send_whatsapp_notification(phone_number, message):
    """Quick function to send WhatsApp"""
    return NotificationService.send_whatsapp(phone_number, message)

