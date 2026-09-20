"""
Advanced Search System for TRACA Management
Map-based search, drawing boundaries, saved searches
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
import json
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class SearchQuery(models.Model):
    """Track search queries for analytics and optimization"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='search_queries'
    )
    
    # Search parameters
    query = models.CharField(max_length=500)
    filters = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    
    # Location data
    county = models.ForeignKey('County', on_delete=models.SET_NULL, null=True, blank=True)
    coordinates = models.JSONField(default=dict, encoder=DjangoJSONEncoder)  # lat, lng bounds
    
    # Results
    result_count = models.PositiveIntegerField(default=0)
    properties_shown = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    
    # Analytics
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_queries'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['county']),
            models.Index(fields=['created_at']),
            models.Index(fields=['session_id']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Search by {self.user.username if self.user else 'Anonymous'}: {self.query}"


class SavedSearch(models.Model):
    """Saved searches for users"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='saved_searches'
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Search parameters
    query = models.CharField(max_length=500)
    filters = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    
    # Notification settings
    email_alerts = models.BooleanField(default=True)
    alert_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='immediate'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    last_alert_sent = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'saved_searches'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['email_alerts', 'last_alert_sent']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def get_matching_properties(self):
        """Get properties that match this saved search"""
        from listings.models_enhanced import Property
        
        # Start with base queryset
        properties = Property.objects.filter(
            property_type__in=['sale', 'rent'],
            status='available'
        ).select_related('county').prefetch_related('media')
        
        # Apply filters
        filters = self.filters
        
        # County filter
        if filters.get('county'):
            properties = properties.filter(county__name__icontains=filters['county'])
        
        # Property type
        if filters.get('property_type'):
            properties = properties.filter(property_type=filters['property_type'])
        
        # Category
        if filters.get('category'):
            properties = properties.filter(category=filters['category'])
        
        # Price range
        if filters.get('min_price'):
            properties = properties.filter(price__gte=filters['min_price'])
        
        if filters.get('max_price'):
            properties = properties.filter(price__lte=filters['max_price'])
        
        # Bedrooms
        if filters.get('bedrooms'):
            properties = properties.filter(bedrooms__gte=filters['bedrooms'])
        
        # Bathrooms
        if filters.get('bathrooms'):
            properties = properties.filter(bathrooms__gte=filters['bathrooms'])
        
        # Location boundaries (if coordinates are stored)
        if filters.get('bounds'):
            bounds = filters['bounds']
            # This would require geospatial database support
            # For now, we'll filter by county
            pass
        
        return properties.order_by('-created_at')
    
    def send_alert_if_needed(self):
        """Send email alert if there are new matching properties"""
        if not self.email_alerts or not self.is_active:
            return False
        
        # Check if we should send an alert based on frequency
        from django.utils import timezone
        now = timezone.now()
        
        if self.alert_frequency == 'immediate':
            # Check for new properties since last alert
            if self.last_alert_sent:
                properties = self.get_matching_properties().filter(
                    created_at__gt=self.last_alert_sent
                )
            else:
                properties = self.get_matching_properties()[:5]  # First alert - send 5 properties
            
        elif self.alert_frequency == 'daily':
            # Send daily if there are new properties
            if self.last_alert_sent and self.last_alert_sent.date() == now.date():
                return False  # Already sent today
            
            if self.last_alert_sent:
                properties = self.get_matching_properties().filter(
                    created_at__gt=self.last_alert_sent
                )
            else:
                properties = self.get_matching_properties()[:10]
        
        elif self.alert_frequency == 'weekly':
            # Send weekly if there are new properties
            if self.last_alert_sent and (now - self.last_alert_sent).days < 7:
                return False  # Already sent this week
            
            if self.last_alert_sent:
                properties = self.get_matching_properties().filter(
                    created_at__gt=self.last_alert_sent
                )
            else:
                properties = self.get_matching_properties()[:15]
        
        elif self.alert_frequency == 'monthly':
            # Send monthly if there are new properties
            if self.last_alert_sent and (now - self.last_alert_sent).days < 30:
                return False  # Already sent this month
            
            if self.last_alert_sent:
                properties = self.get_matching_properties().filter(
                    created_at__gt=self.last_alert_sent
                )
            else:
                properties = self.get_matching_properties()[:20]
        
        else:
            return False
        
        if properties.exists():
            # Send email alert
            self.send_email_alert(properties)
            self.last_alert_sent = now
            self.save()
            return True
        
        return False
    
    def send_email_alert(self, properties):
        """Send email alert with matching properties"""
        from django.core.mail import send_mail
        from django.conf import settings
        from django.urls import reverse
        
        # Build email content
        subject = f"New Properties Match Your Search: {self.name}"
        
        property_list = ""
        for property in properties[:10]:  # Limit to 10 properties
            property_url = f"{settings.SITE_URL}{reverse('listings:property_detail', kwargs={'pk': property.pk})}"
            property_list += f"""
• {property.title}
  Location: {property.county.name}, {property.town}
  Price: KES {property.price:,.0f}
  {property_url}

"""
        
        message = f"""
Hello {self.user.get_full_name() or self.user.username},

We found new properties that match your saved search: "{self.name}"

{property_list}

View all matching properties: {settings.SITE_URL}{reverse('listings:properties_list')}?saved_search={self.id}

To manage your saved searches or unsubscribe from alerts, visit your account settings.

Best regards,
TRACA Management Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.user.email],
                fail_silently=False,
            )
            logger.info(f"Property alert sent to {self.user.email} for saved search: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to send property alert: {e}")
            return False


class SearchAlert(models.Model):
    """Individual search alert notifications"""
    
    saved_search = models.ForeignKey(SavedSearch, on_delete=models.CASCADE, related_name='alerts')
    properties = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    sent_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'search_alerts'
        indexes = [
            models.Index(fields=['saved_search', 'sent_at']),
            models.Index(fields=['email_sent', 'success']),
        ]
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Alert for {self.saved_search.name} - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"


class AdvancedSearchService:
    """Service for advanced search operations"""
    
    @staticmethod
    def search_properties(query_params, user=None):
        """Perform advanced property search"""
        from listings.models_enhanced import Property
        
        # Log the search
        search_query = SearchQuery.objects.create(
            user=user,
            query=query_params.get('q', ''),
            filters=query_params,
            county=None,  # Will be set later
            result_count=0,
            ip_address=query_params.get('ip_address', ''),
            user_agent=query_params.get('user_agent', ''),
            session_id=query_params.get('session_id', '')
        )
        
        # Build queryset
        properties = Property.objects.filter(
            property_type__in=['sale', 'rent'],
            status='available'
        ).select_related('county').prefetch_related('media')
        
        # Apply filters
        properties = AdvancedSearchService._apply_filters(properties, query_params)
        
        # Get result count
        result_count = properties.count()
        
        # Update search query
        search_query.result_count = result_count
        search_query.save()
        
        # Apply pagination
        page = int(query_params.get('page', 1))
        page_size = int(query_params.get('page_size', 12))
        start = (page - 1) * page_size
        end = start + page_size
        
        properties_page = properties[start:end]
        
        # Store property IDs in search query
        search_query.properties_shown = list(properties_page.values_list('id', flat=True))
        search_query.save()
        
        return {
            'properties': properties_page,
            'total_count': result_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (result_count + page_size - 1) // page_size,
            'search_query_id': search_query.id,
        }
    
    @staticmethod
    def _apply_filters(queryset, params):
        """Apply filters to property queryset"""
        
        # Keyword search
        keyword = params.get('q', '').strip()
        if keyword:
            queryset = queryset.filter(
                models.Q(title__icontains=keyword) |
                models.Q(description__icontains=keyword) |
                models.Q(county__name__icontains=keyword) |
                models.Q(town__icontains=keyword)
            )
        
        # County filter
        county = params.get('county', '').strip()
        if county:
            queryset = queryset.filter(county__name__icontains=county)
        
        # Property type
        property_type = params.get('property_type', '')
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        # Category
        category = params.get('category', '')
        if category:
            queryset = queryset.filter(category=category)
        
        # Price range
        min_price = params.get('min_price')
        if min_price and min_price.isdigit():
            queryset = queryset.filter(price__gte=int(min_price))
        
        max_price = params.get('max_price')
        if max_price and max_price.isdigit():
            queryset = queryset.filter(price__lte=int(max_price))
        
        # Bedrooms
        bedrooms = params.get('bedrooms')
        if bedrooms and bedrooms.isdigit():
            queryset = queryset.filter(bedrooms__gte=int(bedrooms))
        
        # Bathrooms
        bathrooms = params.get('bathrooms')
        if bathrooms and bathrooms.isdigit():
            queryset = queryset.filter(bathrooms__gte=int(bathrooms))
        
        # Parking
        parking = params.get('parking')
        if parking and parking.isdigit():
            queryset = queryset.filter(parking_slots__gte=int(parking))
        
        # Furnished
        furnished = params.get('furnished')
        if furnished == 'true':
            queryset = queryset.filter(is_furnished=True)
        elif furnished == 'false':
            queryset = queryset.filter(is_furnished=False)
        
        # Verified only
        verified = params.get('verified')
        if verified == 'true':
            queryset = queryset.filter(is_verified=True)
        
        # Featured only
        featured = params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(featured=True)
        
        # Location bounds (for map search)
        bounds = params.get('bounds')
        if bounds:
            # This would require geospatial database support
            # For now, we'll filter by counties within bounds
            try:
                bounds_data = json.loads(bounds)
                # Extract counties that fall within the bounds
                # This is a simplified implementation
                pass
            except json.JSONDecodeError:
                pass
        
        # Sort results
        sort_by = params.get('sort', '-created_at')
        valid_sorts = {
            '-created_at': 'created_at',
            'created_at': 'created_at',
            '-price': 'price',
            'price': 'price',
            'title': 'title',
            '-view_count': 'view_count',
        }
        
        if sort_by in valid_sorts:
            if sort_by.startswith('-'):
                queryset = queryset.order_by(f"-{valid_sorts[sort_by]}")
            else:
                queryset = queryset.order_by(valid_sorts[sort_by])
        
        return queryset
    
    @staticmethod
    def get_search_suggestions(query, limit=10):
        """Get search suggestions"""
        from listings.models_enhanced import Property, County
        
        suggestions = []
        
        # County suggestions
        county_suggestions = County.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:5]
        
        for county in county_suggestions:
            suggestions.append({
                'type': 'county',
                'title': county,
                'url': f"/properties/?county={county}"
            })
        
        # Property suggestions
        property_suggestions = Property.objects.filter(
            title__icontains=query,
            status='available'
        ).select_related('county').values(
            'id', 'title', 'county__name', 'price', 'property_type'
        )[:5]
        
        for prop in property_suggestions:
            suggestions.append({
                'type': 'property',
                'id': prop['id'],
                'title': prop['title'],
                'county': prop['county__name'],
                'price': prop['price'],
                'property_type': prop['property_type'],
                'url': f"/property/{prop['id']}/"
            })
        
        return suggestions
    
    @staticmethod
    def save_search(user, name, query_params):
        """Save a search for a user"""
        saved_search = SavedSearch.objects.create(
            user=user,
            name=name,
            query=query_params.get('q', ''),
            filters=query_params
        )
        
        logger.info(f"Saved search '{name}' for user: {user.username}")
        return saved_search
    
    @staticmethod
    def get_popular_searches(limit=20):
        """Get popular search queries"""
        from django.db.models import Count
        
        popular_queries = SearchQuery.objects.values(
            'query'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
        
        return list(popular_queries)
    
    @staticmethod
    def get_search_analytics(days=30):
        """Get search analytics"""
        from django.utils import timezone
        from django.db.models import Count, Avg
        
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        analytics = {
            'total_searches': SearchQuery.objects.filter(
                created_at__gte=start_date
            ).count(),
            'unique_searches': SearchQuery.objects.filter(
                created_at__gte=start_date
            ).values('query').distinct().count(),
            'avg_results': SearchQuery.objects.filter(
                created_at__gte=start_date
            ).aggregate(avg=Avg('result_count'))['avg'] or 0,
            'top_counties': SearchQuery.objects.filter(
                created_at__gte=start_date,
                county__isnull=False
            ).values('county__name').annotate(
                count=Count('id')
            ).order_by('-count')[:10],
            'search_types': SearchQuery.objects.filter(
                created_at__gte=start_date
            ).values('user__isnull').annotate(
                count=Count('id')
            ).order_by('-count'),
        }
        
        return analytics
    
    @staticmethod
    def send_property_alerts():
        """Send property alerts for all active saved searches"""
        from django.utils import timezone
        
        active_searches = SavedSearch.objects.filter(
            is_active=True,
            email_alerts=True
        )
        
        alerts_sent = 0
        
        for saved_search in active_searches:
            if saved_search.send_alert_if_needed():
                alerts_sent += 1
        
        logger.info(f"Sent {alerts_sent} property alerts")
        return alerts_sent


class MapSearchService:
    """Service for map-based property search"""
    
    @staticmethod
    def get_properties_in_bounds(bounds, filters=None):
        """Get properties within map bounds"""
        from listings.models_enhanced import Property
        
        # bounds should be: {'north': lat, 'south': lat, 'east': lng, 'west': lng}
        
        # This is a simplified implementation
        # In production, you'd use PostGIS or another geospatial database
        
        properties = Property.objects.filter(
            property_type__in=['sale', 'rent'],
            status='available'
        ).select_related('county').prefetch_related('media')
        
        # Apply additional filters
        if filters:
            properties = AdvancedSearchService._apply_filters(properties, filters)
        
        # For now, return all properties (geospatial filtering would be added here)
        return properties
    
    @staticmethod
    def get_property_clusters(bounds, zoom_level):
        """Get property clusters for map display"""
        # This would implement clustering algorithm based on zoom level
        # For now, return empty list
        return []
    
    @staticmethod
    def geocode_address(address):
        """Geocode an address to coordinates"""
        # This would integrate with Google Maps API or similar
        # For now, return None
        return None
    
    @staticmethod
    def reverse_geocode(lat, lng):
        """Reverse geocode coordinates to address"""
        # This would integrate with Google Maps API or similar
        # For now, return None
        return None
