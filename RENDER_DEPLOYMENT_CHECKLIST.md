# 🚀 Render Deployment Checklist

## Pre-Deployment Checklist

### ✅ Repository Preparation
- [x] `render.yaml` configuration file created
- [x] `start.sh` script updated for production
- [x] `requirements.txt` updated with production dependencies
- [x] Production settings configured in `myproject/settings_production.py`

### ✅ Files Ready for Deployment
- [x] `render.yaml` - Render configuration
- [x] `start.sh` - Startup script
- [x] `requirements.txt` - Python dependencies
- [x] `myproject/settings_production.py` - Production settings

## Deployment Steps

### 1. GitHub Repository
- [ ] Push all changes to GitHub
- [ ] Ensure repository is public (for free Render tier)

### 2. Render Account Setup
- [ ] Go to [render.com](https://render.com)
- [ ] Sign up with GitHub account
- [ ] Authorize Render to access your repositories

### 3. Database Setup
- [ ] Create PostgreSQL database on Render
- [ ] Copy database URL for environment variables

### 4. Web Service Setup
- [ ] Create new Web Service
- [ ] Connect GitHub repository
- [ ] Configure build and start commands
- [ ] Set environment variables

### 5. Environment Variables
```
DEBUG=False
SECRET_KEY=your-generated-secret-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
DJANGO_SETTINGS_MODULE=myproject.settings_production
```

### 6. Deploy and Test
- [ ] Deploy the application
- [ ] Test all portals:
  - Main website: `https://your-app.onrender.com/`
  - Admin: `https://your-app.onrender.com/admin/`
  - Landlord: `https://your-app.onrender.com/landlord/`
  - Tenant: `https://your-app.onrender.com/tenant/`

## Post-Deployment Tasks

### 1. Create Admin User
```bash
python manage.py createsuperuser
```

### 2. Add Sample Data (Optional)
- Create sample properties
- Add sample landlords and tenants
- Test all functionality

### 3. Configure Email (Optional)
- Set up email service (Gmail, SendGrid, etc.)
- Configure email settings in environment variables

### 4. Configure WhatsApp/SMS (Optional)
- Set up WhatsApp Business API
- Configure Twilio for SMS
- Add API keys to environment variables

## Troubleshooting

### Common Issues:
1. **Build fails**: Check `requirements.txt` and Python version
2. **Database connection**: Verify `DATABASE_URL` format
3. **Static files**: Check `collectstatic` command
4. **Media files**: Configure media file serving

### Support:
- Check Render logs in dashboard
- Django logs: `python manage.py runserver --verbosity=2`
- Database issues: Check PostgreSQL connection

## Security Checklist

- [x] `DEBUG=False` in production
- [x] Strong `SECRET_KEY` generated
- [x] `ALLOWED_HOSTS` configured for Render
- [x] HTTPS enabled (automatic on Render)
- [ ] Email settings configured
- [ ] Backup strategy planned

---

**Ready to deploy! 🎉**
