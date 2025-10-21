# 🚀 Traca Management Service - Deployment Guide

## Deploy to Render (Recommended)

Your Django project is already configured for Render deployment! Follow these steps:

### Prerequisites
- GitHub repository with your code
- Render account (free tier available)

### Step 1: Prepare Your Repository

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for production deployment"
   git push origin master
   ```

### Step 2: Deploy to Render

1. **Go to [Render.com](https://render.com)** and sign up/login
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service**:

   **Basic Settings:**
   - **Name:** `traca-management-service`
   - **Environment:** `Python 3`
   - **Branch:** `master`
   - **Root Directory:** Leave empty
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `bash start.sh`

5. **Environment Variables** (Add these in Render dashboard):
   ```
   DEBUG=False
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

6. **Click "Create Web Service"**

### Step 3: Set Up Database

1. **In Render dashboard, click "New +"** → **"PostgreSQL"**
2. **Name:** `traca-management-db`
3. **Plan:** Free tier
4. **Click "Create Database"**
5. **Copy the database URL** and add it as `DATABASE_URL` environment variable

### Step 4: Configure Environment Variables

In your Render web service, add these environment variables:

```
DEBUG=False
SECRET_KEY=your-generated-secret-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
EMAIL_HOST=your-email-host
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_HOST_USER=your-email-user
DEFAULT_FROM_EMAIL=Traca Management <noreply@tracamanagement.co.ke>
```

### Step 5: Deploy

1. **Click "Deploy"** in Render
2. **Wait for deployment** (5-10 minutes)
3. **Your app will be available at:** `https://your-app-name.onrender.com`

## Alternative Hosting Options

### 1. Railway
- Similar to Render
- Good for Django apps
- Free tier available

### 2. Heroku
- Popular platform
- Easy deployment
- Paid plans required

### 3. DigitalOcean App Platform
- Good performance
- Easy scaling
- Paid plans

### 4. AWS/GCP/Azure
- Enterprise-grade
- More complex setup
- Better for large scale

## Post-Deployment Steps

1. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

2. **Add sample data** (optional):
   ```bash
   python manage.py loaddata fixtures/sample_data.json
   ```

3. **Test all portals:**
   - Main website: `https://your-app.onrender.com/`
   - Admin: `https://your-app.onrender.com/admin/`
   - Landlord: `https://your-app.onrender.com/landlord/`
   - Tenant: `https://your-app.onrender.com/tenant/`

## Troubleshooting

### Common Issues:

1. **Static files not loading:**
   - Check `STATIC_ROOT` setting
   - Run `python manage.py collectstatic`

2. **Database connection issues:**
   - Verify `DATABASE_URL` format
   - Check database credentials

3. **Media files not working:**
   - Configure media file serving
   - Use cloud storage (AWS S3, Cloudinary)

### Support:
- Check Render logs in dashboard
- Django logs: `python manage.py runserver --verbosity=2`
- Database issues: Check PostgreSQL connection

## Security Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up HTTPS (automatic on Render)
- [ ] Configure email settings
- [ ] Set up backup strategy

## Performance Optimization

1. **Enable caching** (Redis/Memcached)
2. **Use CDN** for static files
3. **Optimize database queries**
4. **Enable compression**
5. **Monitor performance**

---

**Your Traca Management Service is ready for production! 🎉**
