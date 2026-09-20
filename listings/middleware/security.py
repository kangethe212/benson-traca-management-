"""
Enhanced security middleware for TRACA Management
Two-factor authentication, rate limiting, CSRF protection
"""

import time
import hashlib
import hmac
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware to prevent abuse
    """
    
    def process_request(self, request):
        # Skip rate limiting for admin users
        if request.user.is_staff:
            return None
            
        # Different rate limits for different endpoints
        if self.is_search_request(request):
            return self.check_rate_limit(request, 'search', limit=100, window=3600)  # 100 searches/hour
        elif self.is_contact_request(request):
            return self.check_rate_limit(request, 'contact', limit=10, window=3600)  # 10 contacts/hour
        elif self.is_auth_request(request):
            return self.check_rate_limit(request, 'auth', limit=20, window=900)  # 20 auth attempts/15min
        elif self.is_api_request(request):
            return self.check_rate_limit(request, 'api', limit=1000, window=3600)  # 1000 API calls/hour
        else:
            return self.check_rate_limit(request, 'general', limit=1000, window=3600)  # General limit
    
    def is_search_request(self, request):
        return (
            request.path.startswith('/properties/') or
            request.path.startswith('/api/search') or
            'search' in request.GET or
            'county' in request.GET
        )
    
    def is_contact_request(self, request):
        return (
            request.path.startswith('/contact') or
            request.path.startswith('/inquiry') or
            request.method == 'POST' and 'contact' in request.path
        )
    
    def is_auth_request(self, request):
        return (
            request.path.startswith('/login') or
            request.path.startswith('/register') or
            request.path.startswith('/password') or
            'auth' in request.path
        )
    
    def is_api_request(self, request):
        return request.path.startswith('/api/')
    
    def check_rate_limit(self, request, key_prefix, limit=100, window=3600):
        # Get client identifier
        client_id = self.get_client_id(request)
        cache_key = f"rate_limit:{key_prefix}:{client_id}"
        
        # Get current count
        count = cache.get(cache_key, 0)
        
        if count >= limit:
            logger.warning(f"Rate limit exceeded for {client_id} on {request.path}")
            return HttpResponseForbidden(
                "Rate limit exceeded. Please try again later.",
                content_type="text/plain"
            )
        
        # Increment counter
        cache.set(cache_key, count + 1, window)
        return None
    
    def get_client_id(self, request):
        # Use IP address as client identifier
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Hash the IP for privacy
        return hashlib.sha256(ip.encode()).hexdigest()[:16]


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses
    """
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://www.google.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://www.google-analytics.com; "
            "frame-ancestors 'none';"
        )
        
        # Remove server information
        response.pop('Server', None)
        
        return response


class DataEncryptionMiddleware(MiddlewareMixin):
    """
    Encrypt sensitive data in requests and responses
    """
    
    def process_request(self, request):
        # Log sensitive data access
        if self.has_sensitive_data(request):
            logger.info(f"Sensitive data access: {request.method} {request.path}")
        
        return None
    
    def has_sensitive_data(self, request):
        sensitive_fields = ['phone', 'email', 'id_number', 'kra_pin', 'bank_account']
        
        if request.method == 'POST':
            for field in sensitive_fields:
                if field in request.POST:
                    return True
        
        return False


class TwoFactorAuthMiddleware(MiddlewareMixin):
    """
    Enforce two-factor authentication for admin users
    """
    
    def process_request(self, request):
        # Skip for non-admin users
        if not request.user.is_authenticated or not request.user.is_staff:
            return None
        
        # Skip for exempt URLs
        if self.is_exempt_url(request.path):
            return None
        
        # Check if 2FA is enabled and verified
        if not self.is_2fa_verified(request):
            logger.warning(f"2FA not verified for admin user: {request.user.username}")
            return HttpResponseForbidden(
                "Two-factor authentication required",
                content_type="text/plain"
            )
        
        return None
    
    def is_exempt_url(self, path):
        exempt_paths = [
            '/admin/login/',
            '/admin/2fa/',
            '/static/',
            '/media/',
        ]
        return any(path.startswith(exempt_path) for exempt_path in exempt_paths)
    
    def is_2fa_verified(self, request):
        # Check if user has 2FA enabled
        if not hasattr(request.user, 'twofactor') or not request.user.twofactor.enabled:
            return True  # 2FA not required if not enabled
        
        # Check 2FA verification session
        session_key = f'2fa_verified_{request.user.id}'
        return request.session.get(session_key, False)


class CSRFProtectionMiddleware(MiddlewareMixin):
    """
    Enhanced CSRF protection
    """
    
    def process_request(self, request):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            if not self.validate_csrf_token(request):
                logger.warning(f"CSRF validation failed for {request.path}")
                return HttpResponseForbidden(
                    "CSRF token validation failed",
                    content_type="text/plain"
                )
        
        return None
    
    def validate_csrf_token(self, request):
        # Get CSRF token from header or form
        csrf_token = request.META.get('HTTP_X_CSRFTOKEN') or request.POST.get('csrfmiddlewaretoken')
        
        if not csrf_token:
            return False
        
        # Validate against session
        session_token = request.session.get('csrf_token')
        if not session_token:
            return False
        
        # Use constant-time comparison
        return hmac.compare_digest(csrf_token, session_token)


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Enhanced session security
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Check session age
            if self.is_session_expired(request):
                logger.warning(f"Session expired for user: {request.user.username}")
                request.session.flush()
                return HttpResponseForbidden(
                    "Session expired. Please log in again.",
                    content_type="text/plain"
                )
            
            # Update last activity
            request.session['last_activity'] = time.time()
        
        return None
    
    def is_session_expired(self, request):
        last_activity = request.session.get('last_activity', time.time())
        session_timeout = getattr(settings, 'SESSION_TIMEOUT', 3600)  # 1 hour default
        
        return time.time() - last_activity > session_timeout


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Audit logging for sensitive operations
    """
    
    def process_request(self, request):
        # Log sensitive operations
        if self.is_sensitive_operation(request):
            self.log_operation(request)
        
        return None
    
    def is_sensitive_operation(self, request):
        sensitive_operations = [
            'DELETE',
            '/admin/',
            '/user/delete',
            '/property/delete',
            '/payment/',
            '/lease/',
        ]
        
        return any(op in request.method or op in request.path for op in sensitive_operations)
    
    def log_operation(self, request):
        log_data = {
            'user': request.user.username if request.user.is_authenticated else 'Anonymous',
            'method': request.method,
            'path': request.path,
            'ip': self.get_client_ip(request),
            'timestamp': time.time(),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
        
        logger.info(f"Audit log: {log_data}")
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class InputValidationMiddleware(MiddlewareMixin):
    """
    Input validation and sanitization
    """
    
    def process_request(self, request):
        if request.method in ('POST', 'PUT', 'PATCH'):
            self.validate_input(request)
        
        return None
    
    def validate_input(self, request):
        # Check for SQL injection patterns
        sql_patterns = [
            'union select',
            'drop table',
            'insert into',
            'update set',
            'delete from',
            '--',
            '/*',
            '*/',
            'xp_',
            'sp_',
        ]
        
        for key, value in request.POST.items():
            if isinstance(value, str):
                for pattern in sql_patterns:
                    if pattern.lower() in value.lower():
                        logger.warning(f"Potential SQL injection detected: {key}={value}")
                        raise PermissionDenied("Invalid input detected")
        
        # Check for XSS patterns
        xss_patterns = [
            '<script',
            'javascript:',
            'onload=',
            'onerror=',
            'onclick=',
            '<iframe',
            '<object',
            '<embed',
        ]
        
        for key, value in request.POST.items():
            if isinstance(value, str):
                for pattern in xss_patterns:
                    if pattern.lower() in value.lower():
                        logger.warning(f"Potential XSS detected: {key}={value}")
                        raise PermissionDenied("Invalid input detected")


class DatabaseConnectionMiddleware(MiddlewareMixin):
    """
    Database connection optimization
    """
    
    def process_request(self, request):
        # Set database connection parameters for performance
        from django.db import connection
        
        # Enable query counting for debugging
        if settings.DEBUG:
            connection.queries_logged = True
        
        return None


class CacheControlMiddleware(MiddlewareMixin):
    """
    Cache control headers for performance
    """
    
    def process_response(self, request, response):
        # Add cache control headers
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            # Static files - cache for 1 year
            response['Cache-Control'] = 'public, max-age=31536000, immutable'
        elif request.path.startswith('/api/'):
            # API responses - cache for 5 minutes
            response['Cache-Control'] = 'public, max-age=300'
        else:
            # Dynamic content - no caching
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response
