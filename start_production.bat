@echo off
REM Traca Management System - Production Start Script
echo 🚀 Starting Traca Management System in Production Mode

REM Set environment variables
set DATABASE_URL=postgresql://postgres:KJUlbnxqvmYJhdEJmlwurmolibUkqdPJ@postgres.railway.internal:5432/railway
set DJANGO_SETTINGS_MODULE=myproject.settings_production
set DEBUG=False
set SECRET_KEY=your-production-secret-key-here

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

REM Run database migrations
echo 🗄️  Running database migrations...
python manage.py migrate

REM Create superuser if it doesn't exist
echo 👤 Setting up admin user...
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@tracamanagement.co.ke', 'admin123')"

REM Start the application
echo 🌐 Starting Django application...
python manage.py runserver 0.0.0.0:8000
