"""
Management command to migrate data from SQLite to PostgreSQL
Usage: python manage.py migrate_to_postgresql
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connections
import os
import sys


class Command(BaseCommand):
    help = 'Migrate data from SQLite to PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Create a backup of the SQLite database before migration',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting database migration from SQLite to PostgreSQL...')
        )
        
        # Check if we're using SQLite currently
        if 'sqlite3' not in settings.DATABASES['default']['ENGINE']:
            self.stdout.write(
                self.style.ERROR('Not using SQLite database. Migration not needed.')
            )
            return

        # Check if PostgreSQL URL is provided
        postgres_url = os.getenv('DATABASE_URL')
        if not postgres_url:
            self.stdout.write(
                self.style.ERROR('DATABASE_URL environment variable not set.')
            )
            return

        if options['backup']:
            self.create_sqlite_backup()

        if options['dry_run']:
            self.dry_run_migration()
        else:
            self.perform_migration()

    def create_sqlite_backup(self):
        """Create a backup of the SQLite database"""
        import shutil
        from django.conf import settings
        
        backup_path = 'db_backup.sqlite3'
        original_path = settings.DATABASES['default']['NAME']
        
        try:
            shutil.copy2(original_path, backup_path)
            self.stdout.write(
                self.style.SUCCESS(f'SQLite database backed up to {backup_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to create backup: {e}')
            )

    def dry_run_migration(self):
        """Show what would be migrated"""
        self.stdout.write(
            self.style.WARNING('DRY RUN - No actual migration will be performed')
        )
        
        # Get table counts from SQLite
        sqlite_conn = connections['default']
        with sqlite_conn.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            self.stdout.write(f'\nTables found in SQLite database:')
            for table in tables:
                table_name = table[0]
                if not table_name.startswith('django_'):
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    self.stdout.write(f'  - {table_name}: {count} records')

    def perform_migration(self):
        """Perform the actual migration"""
        self.stdout.write('Performing migration...')
        
        # Set environment variable to use PostgreSQL
        os.environ['DATABASE_URL'] = 'postgresql://postgres:KJUlbnxqvmYJhdEJmlwurmolibUkqdPJ@postgres.railway.internal:5432/railway'
        
        # Run migrations on PostgreSQL
        from django.core.management import execute_from_command_line
        
        self.stdout.write('Running migrations on PostgreSQL...')
        execute_from_command_line(['manage.py', 'migrate'])
        
        self.stdout.write(
            self.style.SUCCESS('Migration completed successfully!')
        )
        self.stdout.write(
            self.style.WARNING('Remember to update your environment variables for production deployment.')
        )
