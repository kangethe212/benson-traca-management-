# Traca Property Management System

A comprehensive Django-based property management platform with separate portals for landlords and tenants, featuring modern UI, complete CRUD operations, and advanced property management tools.

# Traca Property Management Service

This project is a Django application for property management.

## 🚀 Features
## Deploying to Render (recommended)

1. Sign in to https://render.com using GitHub and grant access to this repository.
2. In Render, choose "New -> Web Service" and connect the repo. Use branch `master`.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `bash start.sh`
5. Add environment variables in Render dashboard:
	- SECRET_KEY (use generated secret; do NOT use the one in code)
	- DEBUG = False
	- DATABASE_URL (if you create a managed Postgres on Render)
	- Any API keys your app needs: TWILIO_AUTH_TOKEN, WHATSAPP_API_TOKEN, EMAIL_HOST_PASSWORD, etc.
6. (Optional) Create a managed Postgres via Render -> New -> PostgreSQL. Copy the `DATABASE_URL` and paste in the Web Service Environment.
7. Deploy. Render will give you a stable public URL you can share with anyone.

There is also a `render.yaml` manifest in the repo which can be used by Render to auto-create services when connecting the repository.

### 🏠 Main Website
- Property listings with advanced search and filtering
- Property comparison tool
- Contact forms and WhatsApp integration
- Responsive design with Bootstrap 5

### 👨‍💼 Landlord Portal
- Property management (CRUD operations)
- Tenant management and tracking
- Financial tracking and analytics
- Maintenance request handling
- Profile management

### 👤 Tenant Portal
- Dashboard with lease information
- Payment tracking and history
- Maintenance request submission
- Document management
- Service requests

### ⚙️ Admin Panel
- Complete system administration
- User management
- Property and tenant oversight

## 🛠 Technology Stack

- **Backend:** Django 4.2.7
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Database:** SQLite (development), PostgreSQL ready
- **Authentication:** Django's built-in system
- **File Storage:** Local media handling

## 📦 Installation

### Prerequisites
- Python 3.8+
- Virtual environment

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd traca-management-service

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## 🗄 Database Models

### Core Models
- **Property:** Listings with images, amenities, location
- **Landlord:** Profiles with verification status
- **Tenant:** Profiles with lease information
- **Lease:** Agreements with terms and dates
- **Payment:** Tracking and history
- **MaintenanceRequest:** Request management
- **Message:** Communication system

## 🌐 Access URLs

- **Main Website:** `http://127.0.0.1:8000/`
- **Landlord Portal:** `http://127.0.0.1:8000/landlord/`
- **Tenant Portal:** `http://127.0.0.1:8000/tenant/`
- **Admin Panel:** `http://127.0.0.1:8000/admin/`

## 🔐 Default Credentials

- **Admin:** `admin` / `admin123`
- **Landlord:** `landlord@example.com` / `password123`
- **Tenant:** `tenant@example.com` / `password123`

## 📁 Project Structure

```
├── listings/              # Main Django app
│   ├── models.py         # Database models
│   ├── views.py          # Main views
│   ├── landlord_views.py # Landlord portal views
│   ├── tenant_views.py   # Tenant portal views
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, images
├── properties/           # Property-specific app
├── myproject/           # Django settings
├── static/              # Static files
├── media/               # User uploads
└── requirements.txt     # Dependencies
```

## 🚀 Deployment

### Development
```bash
python manage.py runserver
```

### Production
1. Configure `settings_production.py`
2. Set up PostgreSQL database
3. Configure static/media file serving
4. Set up email settings
5. Deploy to your preferred platform

## 📝 Management Commands

```bash
python manage.py migrate              # Run migrations
python manage.py collectstatic        # Collect static files
python manage.py createsuperuser      # Create admin user
python manage.py shell                # Django shell
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production:
```
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
EMAIL_HOST=your-email-host
```

## 📊 Features Overview

- ✅ Complete CRUD operations
- ✅ User authentication and authorization
- ✅ File upload and management
- ✅ Email notifications
- ✅ WhatsApp integration
- ✅ Responsive design
- ✅ Property comparison
- ✅ Financial tracking
- ✅ Maintenance management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is proprietary software owned by Traca Management Service Ltd.

## 📞 Support

For technical support or questions, contact the development team.

---

**Traca Management Service Ltd** - Professional Property Management Solutions