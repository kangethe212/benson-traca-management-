#!/usr/bin/env python3
"""
Railway deployment script for Traca Management System
This script sets up the PostgreSQL database and runs migrations
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def main():
    """Main deployment function"""
    print("🚀 Starting Railway deployment for Traca Management System")
    
    # Set environment variables
    os.environ['DATABASE_URL'] = 'postgresql://postgres:KJUlbnxqvmYJhdEJmlwurmolibUkqdPJ@postgres.railway.internal:5432/railway'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings_production'
    
    # Install dependencies
    run_command("pip install -r requirements.txt", "Installing dependencies")
    
    # Collect static files
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    # Run database migrations
    run_command("python manage.py migrate", "Running database migrations")
    
    # Create superuser if it doesn't exist
    try:
        run_command("python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@tracamanagement.co.ke', 'admin123')\"", "Creating superuser")
    except:
        print("⚠️  Superuser creation skipped (may already exist)")
    
    # Load sample data (optional)
    try:
        run_command("python manage.py loaddata sample_data.json", "Loading sample data")
    except:
        print("⚠️  Sample data loading skipped (file may not exist)")
    
    print("🎉 Railway deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Set up environment variables in Railway dashboard")
    print("2. Configure domain and SSL")
    print("3. Test the application")
    print("\n🔗 Admin URL: /admin/")
    print("👤 Admin credentials: admin / admin123")

if __name__ == "__main__":
    main()
