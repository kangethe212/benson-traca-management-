"""
Enhanced Django settings for TRACA Management
Includes all security, performance, and feature configurations
"""

import os
from pathlib import Path
from datetime import timedelta
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Site configuration
SITE_URL = config('SITE_URL', default='http://127.0.0.1:8000')
SITE_NAME = config('SITE_NAME', default='TRACA Management')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'django_jazzmin',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'django_extensions',
]

LOCAL_APPS = [
    'listings',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    # Security middleware first
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    
    # Custom security middleware
    'listings.middleware.security.RateLimitMiddleware',
    'listings.middleware.security.SecurityHeadersMiddleware',
    'listings.middleware.security.DataEncryptionMiddleware',
    'listings.middleware.security.TwoFactorAuthMiddleware',
    'listings.middleware.security.CSRFProtectionMiddleware',
    'listings.middleware.security.SessionSecurityMiddleware',
    'listings.middleware.security.AuditLoggingMiddleware',
    'listings.middleware.security.InputValidationMiddleware',
    
    # Standard Django middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Performance middleware
    'listings.middleware.security.DatabaseConnectionMiddleware',
    'listings.middleware.security.CacheControlMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'listings' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'listings.context_processors.site_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
            'check_same_thread': False,
        }
    }
}

# For production, use PostgreSQL
if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='traca_db'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'OPTIONS': {
                'connect_timeout': 60,
            }
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Custom storage for Windows
if os.name == 'nt':  # Windows
    class WindowsFileSystemStorage:
        def __init__(self, location, base_url):
            self.location = location
            self.base_url = base_url
        
        def save(self, name, content):
            import os
            import shutil
            from django.core.files.storage import default_storage
            
            # Create directory if it doesn't exist
            full_path = os.path.join(self.location, name)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Save file
            with open(full_path, 'wb') as destination:
                shutil.copyfileobj(content, destination)
            
            return name
        
        def url(self, name):
            return self.base_url + name
    
    DEFAULT_FILE_STORAGE = 'myproject.settings.WindowsFileSystemStorage'
    DEFAULT_FILE_STORAGE_LOCATION = MEDIA_ROOT
    DEFAULT_FILE_STORAGE_BASE_URL = MEDIA_URL

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# Django Jazzmin Admin Configuration
JAZZMIN_SETTINGS = {
    "site_title": "Traca Management Admin",
    "site_header": "Traca Management",
    "site_brand": "Traca Management",
    "site_logo": "images/traca-logo-new.png",
    "login_logo": "images/traca-logo-new.png",
    "login_logo_dark": "images/traca-logo-new.png",
    "site_logo_classes": "img-circle",
    "site_icon": "images/traca-logo-new.png",
    "welcome_sign": "Welcome to Traca Management Admin Panel",
    "copyright": "Traca Management Services Ltd",
    "search_model": ["auth.User", "listings.Property", "listings.Tenant", "listings.Landlord"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.User"},
        {"app": "listings"},
    ],
    "usermenu_links": [
        {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
        {"model": "auth.user"}
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "listings", "listings.Property", "listings.Tenant", "listings.Landlord"],
    "custom_links": {
        "listings": [{
            "name": "Property Analytics",
            "url": "admin:listings_property_changelist",
            "icon": "fas fa-chart-bar",
            "permissions": ["listings.view_property"]
        }]
    },
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "listings.Property": "fas fa-building",
        "listings.Tenant": "fas fa-user-friends",
        "listings.Landlord": "fas fa-user-tie",
        "listings.Lease": "fas fa-file-contract",
        "listings.Payment": "fas fa-credit-card",
        "listings.MaintenanceRequest": "fas fa-tools",
        "listings.Message": "fas fa-envelope",
        "listings.County": "fas fa-map-marker-alt",
        "listings.Amenity": "fas fa-star",
        "listings.PropertyViewing": "fas fa-calendar-check",
        "listings.Inquiry": "fas fa-question-circle",
        "listings.Testimonial": "fas fa-quote-left",
        "listings.TenantService": "fas fa-concierge-bell",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": "css/admin-custom.css",
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-primary navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

# CORS Settings
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000', cast=lambda v: [s.strip() for s in v.split(',')])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Redis configuration for production
if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                }
            },
            'TIMEOUT': 300,
            'KEY_PREFIX': 'traca',
        }
    }

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@tracamanagement.co.ke')
CONTACT_EMAIL = config('CONTACT_EMAIL', default='info@tracamanagement.co.ke')

# For development, use console backend
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'listings': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console', 'mail_admins'],
        'level': 'WARNING',
    },
}

# Create logs directory if it doesn't exist
import os
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Two-Factor Authentication Settings
TWO_FACTOR_ENABLED = config('TWO_FACTOR_ENABLED', default=True, cast=bool)
TWO_FACTOR_ISSUER = 'TRACA Management'
TWO_FACTOR_DIGITS = 6
TWO_FACTOR_WINDOW = 1

# Rate Limiting Settings
RATELIMIT_ENABLE = config('RATELIMIT_ENABLE', default=True, cast=bool)
RATELIMIT_USE_CACHE = 'default'

# Background Tasks (Celery Configuration)
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'send-payment-reminders': {
        'task': 'listings.tasks.send_payment_reminders',
        'schedule': timedelta(hours=6),  # Every 6 hours
    },
    'send-lease-expiration-reminders': {
        'task': 'listings.tasks.send_lease_expiration_reminders',
        'schedule': timedelta(days=1),  # Daily
    },
    'send-property-alerts': {
        'task': 'listings.tasks.send_property_alerts',
        'schedule': timedelta(minutes=30),  # Every 30 minutes
    },
    'cleanup-expired-sessions': {
        'task': 'listings.tasks.cleanup_expired_sessions',
        'schedule': timedelta(hours=1),  # Hourly
    },
    'update-search-analytics': {
        'task': 'listings.tasks.update_search_analytics',
        'schedule': timedelta(hours=2),  # Every 2 hours
    },
}

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_FILE_MAX_SIZE = 20 * 1024 * 1024  # 20MB

# Allowed file types
ALLOWED_UPLOAD_IMAGES = ['jpg', 'jpeg', 'png', 'gif', 'webp']
ALLOWED_UPLOAD_DOCUMENTS = ['pdf', 'doc', 'docx', 'txt']
ALLOWED_UPLOAD_VIDEOS = ['mp4', 'avi', 'mov', 'wmv']

# API Settings
API_VERSION = 'v1'
API_DOCS_ENABLED = config('API_DOCS_ENABLED', default=DEBUG, cast=bool)

# Analytics Settings
GOOGLE_ANALYTICS_ID = config('GOOGLE_ANALYTICS_ID', default='')
GOOGLE_TAG_MANAGER_ID = config('GOOGLE_TAG_MANAGER_ID', default='')

# Social Media Settings
SOCIAL_MEDIA = {
    'facebook': config('FACEBOOK_URL', default=''),
    'twitter': config('TWITTER_URL', default=''),
    'instagram': config('INSTAGRAM_URL', default=''),
    'linkedin': config('LINKEDIN_URL', default=''),
    'youtube': config('YOUTUBE_URL', default=''),
}

# WhatsApp Settings
WHATSAPP_BUSINESS_NUMBER = config('WHATSAPP_BUSINESS_NUMBER', default='+254700000000')
WHATSAPP_API_KEY = config('WHATSAPP_API_KEY', default='')

# Map Settings
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', default='')
MAP_DEFAULT_CENTER = {'lat': -1.2921, 'lng': 36.8219}  # Nairobi
MAP_DEFAULT_ZOOM = 10

# Payment Gateway Settings
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
MPESA_SHORTCODE = config('MPESA_SHORTCODE', default='')
MPESA_CONSUMER_KEY = config('MPESA_CONSUMER_KEY', default='')
MPESA_CONSUMER_SECRET = config('MPESA_CONSUMER_SECRET', default='')

# SMS Service Settings
SMS_SERVICE_PROVIDER = config('SMS_SERVICE_PROVIDER', default='twilio')
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')

# Performance Settings
ENABLE_QUERY_DEBUG = config('ENABLE_QUERY_DEBUG', default=DEBUG, cast=bool)
DATABASE_QUERY_TIMEOUT = config('DATABASE_QUERY_TIMEOUT', default=30, cast=int)

# Development/Testing Settings
if DEBUG:
    # Enable debug toolbar
    try:
        import debug_toolbar
        INSTALLED_APPS.append('debug_toolbar')
        MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        INTERNAL_IPS = ['127.0.0.1']
    except ImportError:
        pass
    
    # Enable Django extensions
    try:
        import django_extensions
        # Already added to INSTALLED_APPS
    except ImportError:
        pass

# Production Settings
if not DEBUG:
    # Additional security settings for production
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Email settings for production
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    
    # Cache settings for production
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# Custom User Model (if needed)
# AUTH_USER_MODEL = 'listings.CustomUser'

# Site ID for Django Sites framework
SITE_ID = 1

# Context Processors
TEMPLATES[0]['OPTIONS']['context_processors'].extend([
    'django.template.context_processors.request',
])

# Additional Settings for Features
FEATURES = {
    'VIRTUAL_TOURS': config('FEATURE_VIRTUAL_TOURS', default=True, cast=bool),
    'MORTGAGE_CALCULATOR': config('FEATURE_MORTGAGE_CALCULATOR', default=True, cast=bool),
    'PROPERTY_COMPARISON': config('FEATURE_PROPERTY_COMPARISON', default=True, cast=bool),
    'SAVED_SEARCHES': config('FEATURE_SAVED_SEARCHES', default=True, cast=bool),
    'PROPERTY_ALERTS': config('FEATURE_PROPERTY_ALERTS', default=True, cast=bool),
    'VIDEO_UPLOADS': config('FEATURE_VIDEO_UPLOADS', default=True, cast=bool),
    'MULTIPLE_LANGUAGES': config('FEATURE_MULTIPLE_LANGUAGES', default=False, cast=bool),
    'ADVANCED_SEARCH': config('FEATURE_ADVANCED_SEARCH', default=True, cast=bool),
    'MAP_SEARCH': config('FEATURE_MAP_SEARCH', default=True, cast=bool),
}

# Mobile App Settings
MOBILE_APP_ENABLED = config('MOBILE_APP_ENABLED', default=False, cast=bool)
MOBILE_PUSH_NOTIFICATIONS = config('MOBILE_PUSH_NOTIFICATIONS', default=False, cast=bool)
FIREBASE_CLOUD_MESSAGING_KEY = config('FIREBASE_CLOUD_MESSAGING_KEY', default='')

# Backup Settings
BACKUP_ENABLED = config('BACKUP_ENABLED', default=True, cast=bool)
BACKUP_SCHEDULE = config('BACKUP_SCHEDULE', default='daily')
BACKUP_RETENTION_DAYS = config('BACKUP_RETENTION_DAYS', default=30, cast=int)

# Maintenance Mode
MAINTENANCE_MODE = config('MAINTENANCE_MODE', default=False, cast=bool)
MAINTENANCE_MESSAGE = config('MAINTENANCE_MESSAGE', default='Site is under maintenance. Please check back later.')

# API Rate Limiting
API_RATE_LIMIT = config('API_RATE_LIMIT', default='1000/hour')
SEARCH_RATE_LIMIT = config('SEARCH_RATE_LIMIT', default='100/hour')
CONTACT_RATE_LIMIT = config('CONTACT_RATE_LIMIT', default='10/hour')
