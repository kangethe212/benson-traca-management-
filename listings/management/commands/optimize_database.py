"""
Database optimization and indexing for TRACA Management
Enhanced performance for property queries and searches
"""

from django.db import models, connection
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Create database indexes for optimal performance'

    def handle(self, *args, **options):
        self.stdout.write('Creating database indexes for optimal performance...')
        
        indexes = [
            # Property indexes for search performance
            "CREATE INDEX IF NOT EXISTS idx_property_price ON listings_property(price);",
            "CREATE INDEX IF NOT EXISTS idx_property_county ON listings_property(county_id);",
            "CREATE INDEX IF NOT EXISTS idx_property_type ON listings_property(property_type);",
            "CREATE INDEX IF NOT EXISTS idx_property_status ON listings_property(status);",
            "CREATE INDEX IF NOT EXISTS idx_property_verified ON listings_property(is_verified);",
            "CREATE INDEX IF NOT EXISTS idx_property_created ON listings_property(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_property_featured ON listings_property(featured);",
            
            # Composite indexes for common query patterns
            "CREATE INDEX IF NOT EXISTS idx_property_search ON listings_property(property_type, status, is_verified, price);",
            "CREATE INDEX IF NOT EXISTS idx_property_location ON listings_property(county_id, town, status);",
            "CREATE INDEX IF NOT EXISTS idx_property_price_type ON listings_property(price, property_type);",
            "CREATE INDEX IF NOT EXISTS idx_property_availability ON listings_property(status, is_verified, created_at);",
            
            # Tenant indexes
            "CREATE INDEX IF NOT EXISTS idx_tenant_status ON listings_tenant(status, is_verified);",
            "CREATE INDEX IF NOT EXISTS idx_tenant_county ON listings_tenant(county_id);",
            "CREATE INDEX IF NOT EXISTS idx_tenant_created ON listings_tenant(created_at);",
            
            # Landlord indexes
            "CREATE INDEX IF NOT EXISTS idx_landlord_verified ON listings_landlord(is_verified, is_active);",
            "CREATE INDEX IF NOT EXISTS idx_landlord_created ON listings_landlord(created_at);",
            
            # Lease indexes
            "CREATE INDEX IF NOT EXISTS idx_lease_active ON listings_lease(status, property_id, tenant_id);",
            "CREATE INDEX IF NOT EXISTS idx_lease_dates ON listings_lease(start_date, end_date, status);",
            
            # Payment indexes
            "CREATE INDEX IF NOT EXISTS idx_payment_status ON listings_payment(status, payment_date);",
            "CREATE INDEX IF NOT EXISTS idx_payment_tenant ON listings_payment(tenant_id, payment_date);",
            "CREATE INDEX IF NOT EXISTS idx_payment_property ON listings_payment(property_id, payment_date);",
            
            # Inquiry indexes
            "CREATE INDEX IF NOT EXISTS idx_inquiry_status ON listings_inquiry(status, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_inquiry_property ON listings_inquiry(property_id, created_at);",
            
            # Maintenance request indexes
            "CREATE INDEX IF NOT EXISTS idx_maintenance_status ON listings_maintenancerequest(status, priority, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_maintenance_property ON listings_maintenancerequest(property_id, status);",
            
            # Message indexes
            "CREATE INDEX IF NOT EXISTS idx_message_recipient ON listings_message(recipient_id, created_at, status);",
            "CREATE INDEX IF NOT EXISTS idx_message_sender ON listings_message(sender_id, created_at);",
            
            # County indexes
            "CREATE INDEX IF NOT EXISTS idx_county_active ON listings_county(is_active, name);",
            
            # Property media indexes
            "CREATE INDEX IF NOT EXISTS idx_media_property ON listings_propertymedia(property_id, media_type, is_primary);",
            
            # Viewing indexes
            "CREATE INDEX IF NOT EXISTS idx_viewing_property ON listings_propertyviewing(property_id, viewing_date, status);",
            "CREATE INDEX IF NOT EXISTS idx_viewing_date ON listings_propertyviewing(viewing_date, status);",
        ]
        
        with connection.cursor() as cursor:
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    self.stdout.write(self.style.SUCCESS(f'✓ Created index'))
                except OperationalError as e:
                    if 'already exists' in str(e):
                        self.stdout.write(self.style.WARNING(f'⚠ Index already exists'))
                    else:
                        self.stdout.write(self.style.ERROR(f'✗ Error creating index: {e}'))
        
        # Analyze tables for query optimization
        tables_to_analyze = [
            'listings_property',
            'listings_tenant', 
            'listings_landlord',
            'listings_lease',
            'listings_payment',
            'listings_inquiry',
            'listings_maintenancerequest',
            'listings_message',
            'listings_county',
            'listings_propertymedia',
            'listings_propertyviewing'
        ]
        
        with connection.cursor() as cursor:
            for table in tables_to_analyze:
                try:
                    cursor.execute(f'ANALYZE {table};')
                    self.stdout.write(self.style.SUCCESS(f'✓ Analyzed {table}'))
                except OperationalError as e:
                    self.stdout.write(self.style.ERROR(f'✗ Error analyzing {table}: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Database optimization completed!'))
