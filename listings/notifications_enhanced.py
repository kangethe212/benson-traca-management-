"""
Enhanced Notification System for TRACA Management
Property alerts, email notifications, SMS notifications
"""

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.cache import cache
from django.core.management.base import BaseCommand
import logging
import json
from datetime import timedelta

logger = logging.getLogger(__name__)


class NotificationService:
    """Enhanced notification service"""

    @staticmethod
    def get_company_recipients():
        """Return active company staff recipients with email addresses."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.filter(is_staff=True, is_active=True).exclude(email='')
    
    @staticmethod
    def send_property_inquiry_notification(inquiry):
        """Send notification for new property inquiry"""
        from django.urls import reverse
        
        # Get company recipients to notify
        admin_users = NotificationService.get_company_recipients()
        
        # Prepare context
        context = {
            'inquiry': inquiry,
            'property': inquiry.property,
            'admin_url': f"{settings.SITE_URL}/admin/listings/inquiry/{inquiry.id}/change/",
            'property_url': f"{settings.SITE_URL}/property/{inquiry.property.pk}/" if inquiry.property else None,
        }
        
        # Render email templates
        subject = f"New Property Inquiry: {inquiry.name}"
        
        html_message = render_to_string('emails/property_inquiry.html', context)
        text_message = render_to_string('emails/property_inquiry.txt', context)
        
        # Send to all admin users
        success_count = 0
        for admin in admin_users:
            try:
                send_mail(
                    subject,
                    text_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                success_count += 1
                logger.info(f"Property inquiry notification sent to {admin.email}")
            except Exception as e:
                logger.error(f"Failed to send inquiry notification to {admin.email}: {e}")
        
        return success_count > 0
    
    @staticmethod
    def send_viewing_confirmation(viewing):
        """Send viewing confirmation email"""
        context = {
            'viewing': viewing,
            'property': viewing.property,
            'viewing_url': f"{settings.SITE_URL}/viewing-confirmation/{viewing.id}/",
            'cancel_url': f"{settings.SITE_URL}/cancel-viewing/{viewing.id}/",
        }
        
        subject = f"Property Viewing Confirmed: {viewing.property.title}"
        
        html_message = render_to_string('emails/viewing_confirmation.html', context)
        text_message = render_to_string('emails/viewing_confirmation.txt', context)
        
        try:
            send_mail(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [viewing.email],
                html_message=html_message,
                fail_silily=False,
            )
            logger.info(f"Viewing confirmation sent to {viewing.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send viewing confirmation: {e}")
            return False
    
    @staticmethod
    def send_payment_confirmation(payment):
        """Send payment confirmation email"""
        context = {
            'payment': payment,
            'property': payment.property,
            'tenant': payment.tenant,
            'receipt_url': f"{settings.SITE_URL}/receipt/{payment.id}/",
        }
        
        subject = f"Payment Confirmation: {payment.receipt_number or 'Payment Received'}"
        
        html_message = render_to_string('emails/payment_confirmation.html', context)
        text_message = render_to_string('emails/payment_confirmation.txt', context)
        
        # Send to tenant
        try:
            send_mail(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [payment.tenant.user.email],
                html_message=html_message,
                fail_silily=False,
            )
            logger.info(f"Payment confirmation sent to tenant {payment.tenant.user.email}")
        except Exception as e:
            logger.error(f"Failed to send payment confirmation to tenant: {e}")
        
        # Send to landlord
        if payment.property and payment.property.landlord:
            try:
                landlord_context = context.copy()
                landlord_context['is_landlord'] = True
                
                landlord_html = render_to_string('emails/payment_confirmation_landlord.html', landlord_context)
                landlord_text = render_to_string('emails/payment_confirmation_landlord.txt', landlord_context)
                
                send_mail(
                    f"Payment Received: {payment.property.title}",
                    landlord_text,
                    settings.DEFAULT_FROM_EMAIL,
                    [payment.property.landlord.user.email],
                    html_message=landlord_html,
                    fail_silily=False,
                )
                logger.info(f"Payment confirmation sent to landlord {payment.property.landlord.user.email}")
            except Exception as e:
                logger.error(f"Failed to send payment confirmation to landlord: {e}")
        
        return True
    
    @staticmethod
    def send_maintenance_notification(maintenance_request):
        """Send maintenance request notification"""
        property_obj = maintenance_request.lease.property_item if maintenance_request.lease_id else None
        context = {
            'request': maintenance_request,
            'property': property_obj,
            'tenant': maintenance_request.tenant,
            'admin_url': f"{settings.SITE_URL}/admin/listings/maintenancerequest/{maintenance_request.id}/change/",
        }
        
        subject = f"Maintenance Request: {maintenance_request.title}"
        
        html_message = render_to_string('emails/maintenance_request.html', context)
        text_message = render_to_string('emails/maintenance_request.txt', context)
        
        # Send to admin users
        admin_users = NotificationService.get_company_recipients()
        success_count = 0
        
        for admin in admin_users:
            try:
                send_mail(
                    subject,
                    text_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin.email],
                    html_message=html_message,
                    fail_silily=False,
                )
                success_count += 1
                logger.info(f"Maintenance notification sent to admin {admin.email}")
            except Exception as e:
                logger.error(f"Failed to send maintenance notification to admin {admin.email}: {e}")
        
        return success_count > 0
    
    @staticmethod
    def send_lease_expiration_reminders():
        """Send lease expiration reminders"""
        from listings.models_enhanced import Lease
        
        # Find leases expiring in the next 30 days
        expiration_date = timezone.now().date() + timedelta(days=30)
        
        expiring_leases = Lease.objects.filter(
            end_date__lte=expiration_date,
            end_date__gt=timezone.now().date(),
            status='active'
        ).select_related('property', 'tenant', 'landlord')
        
        reminders_sent = 0
        
        for lease in expiring_leases:
            context = {
                'lease': lease,
                'property': lease.property,
                'tenant': lease.tenant,
                'landlord': lease.landlord,
                'days_until_expiry': (lease.end_date - timezone.now().date()).days,
                'renewal_url': f"{settings.SITE_URL}/renew-lease/{lease.id}/",
            }
            
            # Send to tenant
            subject = f"Lease Expiring Soon: {lease.property.title}"
            
            html_message = render_to_string('emails/lease_expiration_tenant.html', context)
            text_message = render_to_string('emails/lease_expiration_tenant.txt', context)
            
            try:
                send_mail(
                    subject,
                    text_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [lease.tenant.user.email],
                    html_message=html_message,
                    fail_silily=False,
                )
                reminders_sent += 1
                logger.info(f"Lease expiration reminder sent to tenant {lease.tenant.user.email}")
            except Exception as e:
                logger.error(f"Failed to send lease expiration reminder to tenant: {e}")
            
            # Send to landlord
            try:
                landlord_context = context.copy()
                landlord_context['is_landlord'] = True
                
                landlord_html = render_to_string('emails/lease_expiration_landlord.html', landlord_context)
                landlord_text = render_to_string('emails/lease_expiration_landlord.txt', landlord_context)
                
                send_mail(
                    f"Lease Expiring Soon: {lease.property.title}",
                    landlord_text,
                    settings.DEFAULT_FROM_EMAIL,
                    [lease.landlord.user.email],
                    html_message=landlord_html,
                    fail_silily=False,
                )
                reminders_sent += 1
                logger.info(f"Lease expiration reminder sent to landlord {lease.landlord.user.email}")
            except Exception as e:
                logger.error(f"Failed to send lease expiration reminder to landlord: {e}")
        
        return reminders_sent
    
    @staticmethod
    def send_payment_reminders():
        """Send payment reminders for overdue payments"""
        from listings.models_enhanced import Payment
        
        # Find overdue payments
        overdue_date = timezone.now().date() - timedelta(days=7)
        
        overdue_payments = Payment.objects.filter(
            due_date__lt=timezone.now().date(),
            status__in=['pending', 'partial'],
        ).select_related('tenant', 'property', 'lease')
        
        reminders_sent = 0
        
        for payment in overdue_payments:
            context = {
                'payment': payment,
                'property': payment.property,
                'tenant': payment.tenant,
                'lease': payment.lease,
                'days_overdue': (timezone.now().date() - payment.due_date).days,
                'payment_url': f"{settings.SITE_URL}/make-payment/{payment.id}/",
            }
            
            subject = f"Payment Reminder: {payment.property.title if payment.property else 'Payment Due'}"
            
            html_message = render_to_string('emails/payment_reminder.html', context)
            text_message = render_to_string('emails/payment_reminder.txt', context)
            
            try:
                send_mail(
                    subject,
                    text_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [payment.tenant.user.email],
                    html_message=html_message,
                    fail_silily=False,
                )
                reminders_sent += 1
                logger.info(f"Payment reminder sent to tenant {payment.tenant.user.email}")
            except Exception as e:
                logger.error(f"Failed to send payment reminder to tenant: {e}")
        
        return reminders_sent
    
    @staticmethod
    def send_new_property_alerts(property):
        """Send alerts for new properties matching saved searches"""
        from listings.advanced_search import SavedSearch
        
        # Find saved searches that match this property
        matching_searches = []
        
        all_searches = SavedSearch.objects.filter(
            is_active=True,
            email_alerts=True
        )
        
        for search in all_searches:
            if search.matches_property(property):
                matching_searches.append(search)
        
        alerts_sent = 0
        
        for search in matching_searches:
            context = {
                'search': search,
                'property': property,
                'search_url': f"{settings.SITE_URL}/properties/?saved_search={search.id}",
                'property_url': f"{settings.SITE_URL}/property/{property.pk}/",
            }
            
            subject = f"New Property Matches Your Search: {search.name}"
            
            html_message = render_to_string('emails/new_property_alert.html', context)
            text_message = render_to_string('emails/new_property_alert.txt', context)
            
            try:
                send_mail(
                    subject,
                    text_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [search.user.email],
                    html_message=html_message,
                    fail_silily=False,
                )
                alerts_sent += 1
                
                # Update last alert sent
                search.last_alert_sent = timezone.now()
                search.save()
                
                logger.info(f"New property alert sent to {search.user.email}")
            except Exception as e:
                logger.error(f"Failed to send new property alert: {e}")
        
        return alerts_sent
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email to new users"""
        context = {
            'user': user,
            'login_url': f"{settings.SITE_URL}/login/",
            'properties_url': f"{settings.SITE_URL}/properties/",
        }
        
        subject = "Welcome to TRACA Management"
        
        html_message = render_to_string('emails/welcome.html', context)
        text_message = render_to_string('emails/welcome.txt', context)
        
        try:
            send_mail(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silily=False,
            )
            logger.info(f"Welcome email sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            return False
    
    @staticmethod
    def send_password_reset_email(user, token):
        """Send password reset email"""
        context = {
            'user': user,
            'reset_url': f"{settings.SITE_URL}/reset-password/{token}/",
            'expiry_hours': 24,  # Token expires in 24 hours
        }
        
        subject = "Reset Your TRACA Management Password"
        
        html_message = render_to_string('emails/password_reset.html', context)
        text_message = render_to_string('emails/password_reset.txt', context)
        
        try:
            send_mail(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silily=False,
            )
            logger.info(f"Password reset email sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False
    
    @staticmethod
    def send_management_request_notification(management_request):
        """Send notification for new property management request"""
        context = {
            'request': management_request,
            'admin_url': f"{settings.SITE_URL}/admin/listings/managementrequest/{management_request.id}/change/",
        }
        
        subject = f"New Property Management Request: {management_request.landlord_name}"
        
        html_message = render_to_string('emails/management_request.html', context)
        text_message = render_to_string('emails/management_request.txt', context)
        
        # Send to admin users
        admin_users = NotificationService.get_company_recipients()
        success_count = 0
        
        for admin in admin_users:
            try:
                send_mail(
                    subject,
                    text_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin.email],
                    html_message=html_message,
                    fail_silily=False,
                )
                success_count += 1
                logger.info(f"Management request notification sent to admin {admin.email}")
            except Exception as e:
                logger.error(f"Failed to send management request notification to admin {admin.email}: {e}")
        
        return success_count > 0
    
    @staticmethod
    def send_contact_notification(contact_form):
        """Send notification for contact form submission"""
        context = {
            'contact': contact_form,
            'admin_url': f"{settings.SITE_URL}/admin/",
        }
        
        subject = f"Contact Form Submission: {contact_form.cleaned_data['name']}"
        
        html_message = render_to_string('emails/contact_notification.html', context)
        text_message = render_to_string('emails/contact_notification.txt', context)
        
        # Send to admin users
        admin_users = NotificationService.get_company_recipients()
        success_count = 0
        
        for admin in admin_users:
            try:
                send_mail(
                    subject,
                    text_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin.email],
                    html_message=html_message,
                    fail_silily=False,
                )
                success_count += 1
                logger.info(f"Contact notification sent to admin {admin.email}")
            except Exception as e:
                logger.error(f"Failed to send contact notification to admin {admin.email}: {e}")
        
        return success_count > 0
    
    @staticmethod
    def send_monthly_newsletter(user):
        """Send monthly newsletter to users"""
        from listings.models_enhanced import Property
        
        # Get featured properties
        featured_properties = Property.objects.filter(
            featured=True,
            status='available'
        ).select_related('county').prefetch_related('media')[:6]
        
        # Get market statistics
        total_properties = Property.objects.filter(status='available').count()
        new_properties = Property.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30),
            status='available'
        ).count()
        
        context = {
            'user': user,
            'featured_properties': featured_properties,
            'total_properties': total_properties,
            'new_properties': new_properties,
            'newsletter_date': timezone.now().strftime('%B %Y'),
        }
        
        subject = f"TRACA Management Newsletter - {context['newsletter_date']}"
        
        html_message = render_to_string('emails/monthly_newsletter.html', context)
        text_message = render_to_string('emails/monthly_newsletter.txt', context)
        
        try:
            send_mail(
                subject,
                text_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silily=False,
            )
            logger.info(f"Monthly newsletter sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send monthly newsletter: {e}")
            return False
    
    @staticmethod
    def get_notification_stats(user=None):
        """Get notification statistics"""
        from django.db.models import Count
        
        if user:
            # Stats for specific user
            stats = {
                'total_sent': 0,  # Would be tracked in a notification log table
                'property_alerts': 0,
                'payment_reminders': 0,
                'lease_reminders': 0,
            }
        else:
            # Global stats
            stats = {
                'total_sent': 0,  # Would be tracked in a notification log table
                'property_inquiries': 0,
                'viewing_confirmations': 0,
                'payment_confirmations': 0,
                'maintenance_requests': 0,
            }
        
        return stats


class SMSNotificationService:
    """SMS notification service (placeholder for integration)"""
    
    @staticmethod
    def send_sms(phone_number, message):
        """Send SMS notification"""
        # This would integrate with an SMS service like Twilio, Africa's Talking, etc.
        # For now, just log the message
        logger.info(f"SMS would be sent to {phone_number}: {message}")
        return True
    
    @staticmethod
    def send_otp(phone_number, otp):
        """Send OTP via SMS"""
        message = f"Your TRACA Management verification code is: {otp}. This code will expire in 10 minutes."
        return SMSNotificationService.send_sms(phone_number, message)
    
    @staticmethod
    def send_payment_reminder_sms(payment):
        """Send payment reminder via SMS"""
        message = f"Payment reminder: Your payment of KES {payment.amount:,.0f} for {payment.property.title if payment.property else 'rent'} is overdue. Please pay immediately."
        return SMSNotificationService.send_sms(payment.tenant.phone, message)
    
    @staticmethod
    def send_viewing_reminder_sms(viewing):
        """Send viewing reminder via SMS"""
        message = f"Reminder: Your property viewing for {viewing.property.title} is scheduled for {viewing.viewing_date} at {viewing.get_viewing_time_display()}. We look forward to seeing you!"
        return SMSNotificationService.send_sms(viewing.phone, message)


class PushNotificationService:
    """Push notification service for mobile apps"""
    
    @staticmethod
    def send_push_notification(user, title, message, data=None):
        """Send push notification to user"""
        # This would integrate with Firebase Cloud Messaging or similar
        # For now, just log the notification
        logger.info(f"Push notification would be sent to {user.username}: {title} - {message}")
        return True
    
    @staticmethod
    def send_property_alert_push(user, property):
        """Send property alert push notification"""
        title = "New Property Alert"
        message = f"A new property matching your search is available: {property.title}"
        data = {
            'type': 'property_alert',
            'property_id': property.id,
            'url': f'/property/{property.id}/'
        }
        return PushNotificationService.send_push_notification(user, title, message, data)
    
    @staticmethod
    def send_payment_reminder_push(user, payment):
        """Send payment reminder push notification"""
        title = "Payment Reminder"
        message = f"Your payment of KES {payment.amount:,.0f} is due soon."
        data = {
            'type': 'payment_reminder',
            'payment_id': payment.id,
            'url': f'/payments/{payment.id}/'
        }
        return PushNotificationService.send_push_notification(user, title, message, data)


# Django management command for sending scheduled notifications
class SendScheduledNotificationsCommand(BaseCommand):
    help = 'Send scheduled notifications (payment reminders, lease expirations, etc.)'
    
    def handle(self, *args, **options):
        notifications_sent = 0
        
        # Send lease expiration reminders
        lease_reminders = NotificationService.send_lease_expiration_reminders()
        notifications_sent += lease_reminders
        self.stdout.write(f"Sent {lease_reminders} lease expiration reminders")
        
        # Send payment reminders
        payment_reminders = NotificationService.send_payment_reminders()
        notifications_sent += payment_reminders
        self.stdout.write(f"Sent {payment_reminders} payment reminders")
        
        # Send property alerts for saved searches
        from listings.advanced_search import AdvancedSearchService
        property_alerts = AdvancedSearchService.send_property_alerts()
        notifications_sent += property_alerts
        self.stdout.write(f"Sent {property_alerts} property alerts")
        
        self.stdout.write(self.style.SUCCESS(f"Total notifications sent: {notifications_sent}"))
