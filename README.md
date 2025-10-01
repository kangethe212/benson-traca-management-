# Traca Management Services Ltd - Real Estate Platform

A comprehensive Django-based real estate platform for Traca Management Services Ltd, supporting property sales, rentals, and property management services in Kenya.

## Features

### 🏠 Property Management
- **Sale Listings**: Properties for sale with detailed information
- **Rental Listings**: Properties available for rent
- **Property Management**: Landlord services for property management and rent collection

### 🔍 Advanced Search & Filtering
- Filter by county, price range, property type
- Search by bedrooms, bathrooms, parking slots
- Verified property badge system
- Pagination for large result sets

### 📱 Modern UI/UX
- Responsive Bootstrap 5 design
- Magenta, bright pink, and pale grey branding
- Mobile-friendly interface
- Interactive property galleries

### 🛡️ Admin Features
- Comprehensive admin panel
- Property verification system
- Management request tracking
- User and content management

## Technology Stack

- **Backend**: Django 5.2.6
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **Styling**: Custom CSS with brand colors
- **Media**: File uploads for images and videos

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd traca-management-services
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Seed sample data (optional)**
   ```bash
   python manage.py seed_data
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
traca-management-services/
├── listings/                    # Main Django app
│   ├── models.py               # Database models
│   ├── views.py                # View functions
│   ├── forms.py                # Django forms
│   ├── admin.py                # Admin configuration
│   ├── urls.py                 # URL patterns
│   ├── templates/              # HTML templates
│   │   └── listings/
│   │       ├── properties_list.html
│   │       ├── property_detail.html
│   │       ├── management_request.html
│   │       └── management_requests_list.html
│   ├── management/             # Management commands
│   │   └── commands/
│   │       └── seed_data.py
│   └── tests.py                # Test cases
├── static/                     # Static files
│   └── css/
│       └── brand.css           # Brand styling
├── media/                      # User uploaded files
├── myproject/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

## Models

### Property
- Basic information (title, description, type)
- Location (county)
- Pricing and details (price, area, rooms)
- Verification status
- Media (virtual tours, video tours)

### ManagementRequest
- Landlord information
- Property details
- Service terms
- Status tracking

### County
- Kenyan counties where Traca operates
- Active/inactive status

## Key Features

### 1. Property Listings
- **URL**: `/properties/`
- **Features**: Advanced filtering, pagination, verified badges
- **Filters**: County, price range, property type, bedrooms, bathrooms

### 2. Property Details
- **URL**: `/properties/<id>/`
- **Features**: Image gallery, virtual tours, video tours, inquiry form
- **Media**: Support for multiple images and videos

### 3. Property Management Request
- **URL**: `/management-request/`
- **Features**: Landlord form, property details, media upload
- **Services**: Tenant screening, rent collection, maintenance

### 4. Admin Management
- **URL**: `/admin/management-requests/`
- **Features**: Request tracking, status management, property oversight

## Brand Colors

- **Primary Magenta**: #FF00FF
- **Secondary Pink**: #FF69B4
- **Background Grey**: #F5F5F5
- **White**: #FFFFFF
- **Dark Grey**: #333333

## Testing

Run the test suite:
```bash
python manage.py test listings
```

The test suite covers:
- View functionality
- Model creation and validation
- Form submission
- Admin access controls
- Search and filtering

## Production Deployment

### Environment Variables
```bash
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Static Files
```bash
python manage.py collectstatic
```

### Database
- Use PostgreSQL for production
- Configure database settings in `settings.py`
- Run migrations on production server

### Web Server
- Use Gunicorn + Nginx
- Configure static file serving
- Set up SSL certificates

## API Endpoints

- `GET /api/search/` - Property search API
- `GET /properties/` - Property listings
- `GET /properties/<id>/` - Property details
- `POST /management-request/` - Submit management request

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is proprietary software for Traca Management Services Ltd.

## Support

For technical support or questions, contact the development team.

---

**Traca Management Services Ltd** - Your trusted partner in Kenyan real estate.