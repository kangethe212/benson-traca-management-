"""
Two-Factor Authentication for TRACA Management
Enhanced security for admin and user accounts
"""

import pyotp
import qrcode
import io
import base64
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class TwoFactorAuth:
    """Two-Factor Authentication Manager"""
    
    @staticmethod
    def generate_secret_key():
        """Generate a new secret key for TOTP"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(user, secret_key):
        """Generate QR code for Google Authenticator"""
        totp_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
            name=user.email,
            issuer_name="TRACA Management"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def verify_totp_token(secret_key, token):
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret_key)
        return totp.verify(token, valid_window=1)  # Allow 1 step tolerance
    
    @staticmethod
    def generate_backup_codes(count=10):
        """Generate backup codes for account recovery"""
        import secrets
        import string
        
        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            codes.append(code)
        
        return codes
    
    @staticmethod
    def send_email_code(user):
        """Send 2FA code via email"""
        import random
        import string
        
        # Generate 6-digit code
        code = ''.join(random.choices(string.digits, k=6))
        
        # Cache the code for 10 minutes
        cache_key = f'2fa_email_code_{user.id}'
        cache.set(cache_key, code, 600)  # 10 minutes
        
        # Send email
        subject = "TRACA Management - Two-Factor Authentication Code"
        message = f"""
Hello {user.get_full_name() or user.username},

Your two-factor authentication code is: {code}

This code will expire in 10 minutes. Do not share this code with anyone.

If you didn't request this code, please contact our support team immediately.

Best regards,
TRACA Management Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            logger.info(f"2FA email code sent to user: {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send 2FA email: {e}")
            return False
    
    @staticmethod
    def verify_email_code(user, code):
        """Verify email-based 2FA code"""
        cache_key = f'2fa_email_code_{user.id}'
        cached_code = cache.get(cache_key)
        
        if cached_code and str(cached_code) == str(code):
            # Delete the code after successful verification
            cache.delete(cache_key)
            return True
        
        return False


class TwoFactorAuthModel(models.Model):
    """Two-Factor Authentication settings for users"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='twofactor'
    )
    
    secret_key = models.CharField(max_length=32, blank=True)
    enabled = models.BooleanField(default=False)
    backup_codes = models.TextField(blank=True)  # JSON string of backup codes
    email_2fa_enabled = models.BooleanField(default=False)
    sms_2fa_enabled = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_twofactor'
        indexes = [
            models.Index(fields=['user', 'enabled']),
        ]
    
    def __str__(self):
        return f"2FA for {self.user.username}"
    
    def enable_2fa(self):
        """Enable 2FA for the user"""
        if not self.secret_key:
            self.secret_key = TwoFactorAuth.generate_secret_key()
        
        self.enabled = True
        self.backup_codes = str(TwoFactorAuth.generate_backup_codes())
        self.save()
        
        logger.info(f"2FA enabled for user: {self.user.username}")
    
    def disable_2fa(self):
        """Disable 2FA for the user"""
        self.enabled = False
        self.secret_key = ''
        self.backup_codes = ''
        self.save()
        
        logger.info(f"2FA disabled for user: {self.user.username}")
    
    def verify_token(self, token):
        """Verify TOTP token"""
        if not self.enabled or not self.secret_key:
            return False
        
        return TwoFactorAuth.verify_totp_token(self.secret_key, token)
    
    def verify_backup_code(self, code):
        """Verify backup code"""
        if not self.enabled or not self.backup_codes:
            return False
        
        import json
        try:
            backup_codes = json.loads(self.backup_codes)
        except json.JSONDecodeError:
            return False
        
        if code in backup_codes:
            # Remove used backup code
            backup_codes.remove(code)
            self.backup_codes = json.dumps(backup_codes)
            self.save()
            
            logger.info(f"Backup code used for user: {self.user.username}")
            return True
        
        return False
    
    def get_qr_code(self):
        """Get QR code for Google Authenticator"""
        if not self.secret_key:
            return None
        
        return TwoFactorAuth.generate_qr_code(self.user, self.secret_key)
    
    def send_email_code(self):
        """Send email verification code"""
        return TwoFactorAuth.send_email_code(self.user)
    
    def verify_email_code(self, code):
        """Verify email code"""
        return TwoFactorAuth.verify_email_code(self.user, code)
    
    def get_remaining_backup_codes(self):
        """Get count of remaining backup codes"""
        if not self.backup_codes:
            return 0
        
        import json
        try:
            backup_codes = json.loads(self.backup_codes)
            return len(backup_codes)
        except json.JSONDecodeError:
            return 0


class TwoFactorAuthSession(models.Model):
    """Track 2FA sessions"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    verified_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'auth_twofactor_session'
        indexes = [
            models.Index(fields=['user', 'session_key']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"2FA Session for {self.user.username}"
    
    @classmethod
    def create_session(cls, user, request):
        """Create a new 2FA session"""
        from django.utils import timezone
        import secrets
        
        # Generate session key
        session_key = secrets.token_urlsafe(32)
        
        # Set expiration to 24 hours from now
        expires_at = timezone.now() + timezone.timedelta(hours=24)
        
        # Get IP and user agent
        ip_address = TwoFactorAuth.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create session
        session = cls.objects.create(
            user=user,
            session_key=session_key,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return session
    
    @classmethod
    def verify_session(cls, user, session_key):
        """Verify 2FA session"""
        try:
            from django.utils import timezone
            
            session = cls.objects.get(
                user=user,
                session_key=session_key,
                expires_at__gt=timezone.now()
            )
            
            return session
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """Clean up expired sessions"""
        from django.utils import timezone
        
        expired_count = cls.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]
        
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired 2FA sessions")
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class TwoFactorAuthLog(models.Model):
    """Log 2FA attempts"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20)  # login, verify, backup_code, email_code
    success = models.BooleanField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'auth_twofactor_log'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'success']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"2FA Log: {self.user.username} - {self.action} - {'Success' if self.success else 'Failed'}"


class TwoFactorAuthService:
    """Service for managing 2FA operations"""
    
    @staticmethod
    def setup_2fa(user):
        """Set up 2FA for a user"""
        two_factor, created = TwoFactorAuthModel.objects.get_or_create(user=user)
        
        if not two_factor.secret_key:
            two_factor.secret_key = TwoFactorAuth.generate_secret_key()
            two_factor.save()
        
        return two_factor
    
    @staticmethod
    def verify_2fa(user, token, method='totp'):
        """Verify 2FA token"""
        try:
            two_factor = TwoFactorAuthModel.objects.get(user=user, enabled=True)
        except TwoFactorAuthModel.DoesNotExist:
            return False, "2FA not enabled"
        
        # Log the attempt
        ip_address = TwoFactorAuth.get_client_ip(None)  # Will be updated in middleware
        user_agent = ""  # Will be updated in middleware
        
        if method == 'totp':
            success = two_factor.verify_token(token)
        elif method == 'backup_code':
            success = two_factor.verify_backup_code(token)
        elif method == 'email_code':
            success = two_factor.verify_email_code(token)
        else:
            success = False
        
        # Log the attempt
        TwoFactorAuthLog.objects.create(
            user=user,
            action='verify',
            success=success,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if success:
            return True, "2FA verification successful"
        else:
            return False, "Invalid token"
    
    @staticmethod
    def create_session(user, request):
        """Create 2FA session after successful verification"""
        session = TwoFactorAuthSession.create_session(user, request)
        
        # Set session in Django session
        request.session[f'2fa_verified_{user.id}'] = True
        request.session[f'2fa_session_key_{user.id}'] = session.session_key
        
        return session
    
    @staticmethod
    def is_verified(user, request):
        """Check if user is verified for current session"""
        # Check Django session
        if request.session.get(f'2fa_verified_{user.id}'):
            return True
        
        # Check database session
        session_key = request.session.get(f'2fa_session_key_{user.id}')
        if session_key:
            session = TwoFactorAuthSession.verify_session(user, session_key)
            if session:
                request.session[f'2fa_verified_{user.id}'] = True
                return True
        
        return False
    
    @staticmethod
    def revoke_verification(user, request):
        """Revoke 2FA verification"""
        request.session.pop(f'2fa_verified_{user.id}', None)
        request.session.pop(f'2fa_session_key_{user.id}', None)
        
        # Delete active sessions
        TwoFactorAuthSession.objects.filter(user=user).delete()
    
    @staticmethod
    def get_user_stats(user):
        """Get user's 2FA statistics"""
        try:
            two_factor = TwoFactorAuthModel.objects.get(user=user)
            
            return {
                'enabled': two_factor.enabled,
                'email_enabled': two_factor.email_2fa_enabled,
                'sms_enabled': two_factor.sms_2fa_enabled,
                'backup_codes_remaining': two_factor.get_remaining_backup_codes(),
                'last_login': TwoFactorAuthLog.objects.filter(
                    user=user, 
                    action='verify', 
                    success=True
                ).order_by('-timestamp').first(),
                'failed_attempts': TwoFactorAuthLog.objects.filter(
                    user=user, 
                    action='verify', 
                    success=False
                ).count(),
            }
        except TwoFactorAuthModel.DoesNotExist:
            return {
                'enabled': False,
                'email_enabled': False,
                'sms_enabled': False,
                'backup_codes_remaining': 0,
                'last_login': None,
                'failed_attempts': 0,
            }
    
    @staticmethod
    def cleanup():
        """Clean up expired sessions and old logs"""
        from django.utils import timezone
        
        # Clean up expired sessions
        TwoFactorAuthSession.cleanup_expired_sessions()
        
        # Clean up old logs (older than 30 days)
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        deleted_logs = TwoFactorAuthLog.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()[0]
        
        if deleted_logs > 0:
            logger.info(f"Cleaned up {deleted_logs} old 2FA logs")


# Django management command for cleanup
class TwoFactorCleanupCommand(BaseCommand):
    help = 'Clean up expired 2FA sessions and old logs'
    
    def handle(self, *args, **options):
        TwoFactorAuthService.cleanup()
        self.stdout.write(self.style.SUCCESS('2FA cleanup completed'))
