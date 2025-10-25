#!/bin/bash

# Traca Management System - Production Start Script
echo "🚀 Starting Traca Management System in Production Mode"

# Set environment variables
export DATABASE_URL="postgresql://postgres:KJUlbnxqvmYJhdEJmlwurmolibUkqdPJ@postgres.railway.internal:5432/railway"
export DJANGO_SETTINGS_MODULE="myproject.settings_production"
export DEBUG=False
export SECRET_KEY="your-production-secret-key-here"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Setting up admin user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@tracamanagement.co.ke', 'admin123')
    print('Admin user created')
else:
    print('Admin user already exists')
"

# Start the application
echo "🌐 Starting Django application..."
python manage.py runserver 0.0.0.0:${PORT:-8000}
