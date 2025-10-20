"""
API Views for Notification System
Traca Management Services
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from .notifications import (
    NotificationService, 
    PropertyNotifications,
    send_email_notification,
    send_sms_notification,
    send_whatsapp_notification
)
from .models import Property
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_property_inquiry(request):
    """
    API endpoint to send property inquiry notification
    
    POST /api/notifications/property-inquiry/
    Body: {
        "property_id": 1,
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "customer_phone": "+254700000000",
        "message": "I'm interested in this property"
    }
    """
    try:
        property_id = request.data.get('property_id')
        customer_info = {
            'name': request.data.get('customer_name'),
            'email': request.data.get('customer_email'),
            'phone': request.data.get('customer_phone'),
            'message': request.data.get('message', '')
        }
        
        # Validate required fields
        if not all([property_id, customer_info['name']]):
            return Response(
                {'error': 'Property ID and customer name are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get property
        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response(
                {'error': 'Property not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Send notification
        PropertyNotifications.notify_new_inquiry(property_obj, customer_info)
        
        return Response({
            'success': True,
            'message': 'Inquiry sent successfully. We will contact you soon!'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error sending property inquiry: {str(e)}")
        return Response(
            {'error': 'Failed to send inquiry. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_maintenance_request(request):
    """
    API endpoint to send maintenance request notification
    
    POST /api/notifications/maintenance-request/
    Body: {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+254700000000",
        "description": "Plumbing issue in kitchen",
        "priority": "HIGH" or "NORMAL"
    }
    """
    try:
        # Create maintenance request object (mock for now)
        class MaintenanceRequest:
            def __init__(self, data):
                self.name = data.get('name')
                self.email = data.get('email')
                self.phone = data.get('phone')
                self.description = data.get('description')
                self.priority = data.get('priority', 'NORMAL')
            
            def get_priority_display(self):
                return self.priority
        
        request_obj = MaintenanceRequest(request.data)
        
        # Validate
        if not all([request_obj.name, request_obj.description]):
            return Response(
                {'error': 'Name and description are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Send notification
        PropertyNotifications.notify_maintenance_request(request_obj)
        
        return Response({
            'success': True,
            'message': 'Maintenance request submitted. We will contact you within 4-6 hours.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error sending maintenance request: {str(e)}")
        return Response(
            {'error': 'Failed to submit request. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_contact_message(request):
    """
    API endpoint to send general contact message
    
    POST /api/notifications/contact/
    Body: {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+254700000000",
        "subject": "General Inquiry",
        "message": "I have a question..."
    }
    """
    try:
        name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        subject = request.data.get('subject', 'Contact Form Message')
        message = request.data.get('message')
        
        if not all([name, message]):
            return Response(
                {'error': 'Name and message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare message
        full_message = f"""
        New contact form submission:
        
        Name: {name}
        Email: {email or 'Not provided'}
        Phone: {phone or 'Not provided'}
        
        Message:
        {message}
        """
        
        # Send to admin
        admin_recipient = {
            'email': settings.ADMINS[0][1]
        }
        
        NotificationService.send_notification(
            recipient=admin_recipient,
            subject=f"Contact Form: {subject}",
            message=full_message,
            channels=['email']
        )
        
        # Send confirmation to customer
        if email:
            confirmation = f"""
            Dear {name},
            
            Thank you for contacting Traca Management Services.
            
            We have received your message and will respond within 24 hours.
            
            Best regards,
            Traca Management Team
            """
            
            send_email_notification(
                subject="Message Received - Traca Management",
                message=confirmation,
                recipient_email=email
            )
        
        return Response({
            'success': True,
            'message': 'Message sent successfully. We will get back to you soon!'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error sending contact message: {str(e)}")
        return Response(
            {'error': 'Failed to send message. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_payment_notification(request):
    """
    API endpoint to send payment confirmation (Admin only)
    
    POST /api/notifications/payment/
    Body: {
        "tenant_name": "John Doe",
        "tenant_email": "john@example.com",
        "tenant_phone": "+254700000000",
        "amount": 50000,
        "property_name": "Apartment 5B",
        "payment_method": "M-Pesa",
        "reference": "ABC123456"
    }
    """
    try:
        payment_info = {
            'tenant_name': request.data.get('tenant_name'),
            'tenant_email': request.data.get('tenant_email'),
            'tenant_phone': request.data.get('tenant_phone'),
            'amount': request.data.get('amount'),
            'property_name': request.data.get('property_name'),
            'payment_method': request.data.get('payment_method'),
            'reference': request.data.get('reference')
        }
        
        if not all([payment_info['tenant_name'], payment_info['amount']]):
            return Response(
                {'error': 'Tenant name and amount are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Send notification
        PropertyNotifications.notify_rent_payment(payment_info)
        
        return Response({
            'success': True,
            'message': 'Payment notification sent successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error sending payment notification: {str(e)}")
        return Response(
            {'error': 'Failed to send notification. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def test_notification(request):
    """
    Test endpoint to verify notification system
    
    POST /api/notifications/test/
    Body: {
        "channel": "email" | "sms" | "whatsapp",
        "recipient": "email@example.com" or "+254700000000"
    }
    """
    try:
        channel = request.data.get('channel', 'email')
        recipient = request.data.get('recipient')
        
        if not recipient:
            return Response(
                {'error': 'Recipient is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        test_message = "This is a test notification from Traca Management Services."
        result = False
        
        if channel == 'email':
            result = send_email_notification(
                subject="Test Notification",
                message=test_message,
                recipient_email=recipient
            )
        elif channel == 'sms':
            result = send_sms_notification(
                phone_number=recipient,
                message=test_message
            )
        elif channel == 'whatsapp':
            result = send_whatsapp_notification(
                phone_number=recipient,
                message=test_message
            )
        else:
            return Response(
                {'error': 'Invalid channel. Use: email, sms, or whatsapp'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if result:
            return Response({
                'success': True,
                'message': f'Test {channel} notification sent successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': f'Failed to send {channel} notification. Check configuration.'
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in test notification: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])  # Changed to AllowAny for easy status checking
def notification_status(request):  # pylint: disable=unused-argument
    """
    Get status of notification channels
    
    GET /api/notifications/status/
    """
    return Response({
        'email': {
            'enabled': settings.ENABLE_EMAIL_NOTIFICATIONS,
            'configured': bool(settings.EMAIL_HOST_USER),
            'backend': settings.EMAIL_BACKEND
        },
        'sms': {
            'enabled': settings.ENABLE_SMS_NOTIFICATIONS,
            'configured': bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN)
        },
        'whatsapp': {
            'enabled': settings.ENABLE_WHATSAPP_NOTIFICATIONS,
            'configured': bool(settings.WHATSAPP_API_TOKEN)
        }
    }, status=status.HTTP_200_OK)

