# PG Tutoring Hub - Deployment Guide

## Overview
This guide covers deploying the PG Tutoring Hub Django application to production. The application has been thoroughly audited and hardened for security.

## Security Features Implemented

### ✅ Security Audit Complete
All critical security vulnerabilities have been addressed:

1. **Environment Variables**: All sensitive data moved to environment variables
2. **Strong Secret Key**: Generated cryptographically secure secret key
3. **Production Settings**: Comprehensive security settings for production
4. **File Upload Security**: File size limits, extension validation, secure paths
5. **Enhanced Authentication**: Password validation, account verification
6. **Permission System**: Role-based access control throughout application
7. **Input Validation**: Enhanced model and form validation
8. **Error Handling**: Custom error pages (404, 500, 403)
9. **Logging**: Comprehensive logging configuration
10. **Database Security**: Enhanced model constraints and indexes

## Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Copy `.env.production` to `.env` on production server
- [ ] Generate new SECRET_KEY for production
- [ ] Update database credentials
- [ ] Configure email settings
- [ ] Set your domain in ALLOWED_HOSTS
- [ ] Verify SSL certificate is installed

### 2. Database Setup
```bash
# Create production database
sudo -u postgres createdb pg_tutoring_hub_prod
sudo -u postgres createuser tutoring_prod_user
sudo -u postgres psql -c "ALTER USER tutoring_prod_user WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pg_tutoring_hub_prod TO tutoring_prod_user;"
```

### 3. Server Dependencies
```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql redis-server

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Django Setup
```bash
# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Create teacher account (optional)
python manage.py create_teacher --username patience --email patience@example.com --password secure_password --first-name Patience --last-name Gwanyanya
```

### 5. Security Verification
```bash
# Check deployment security
python manage.py check --deploy

# Should return: System check identified no issues (0 silenced).
```

## Production Environment Variables

Copy and modify `.env.production`:

```env
# Generate new secret key
SECRET_KEY=your-new-secret-key-here

# Production mode
DEBUG=False

# Your domain
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Production database
DB_NAME=pg_tutoring_hub_prod
DB_USER=tutoring_prod_user
DB_PASSWORD=your_secure_production_password

# Email configuration
EMAIL_HOST_USER=your_email@yourdomain.com
EMAIL_HOST_PASSWORD=your_app_password

# Security settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Web Server Configuration

### Nginx Configuration
Create `/etc/nginx/sites-available/pg_tutoring_hub`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";

    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/your/project/media/;
        expires 1M;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service
Create `/etc/systemd/system/pg_tutoring_hub.service`:

```ini
[Unit]
Description=PG Tutoring Hub Django Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
Environment=PATH=/path/to/your/project/venv/bin
ExecStart=/path/to/your/project/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 pg_hub.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

## Performance Optimization

### 1. Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_users_user_type ON users_customuser(user_type);
CREATE INDEX idx_hub_assignments_due_date ON hub_assignment(due_date);
CREATE INDEX idx_hub_submissions_created_at ON hub_submission(created_at);
```

### 2. Redis Configuration
Add to `/etc/redis/redis.conf`:
```
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### 3. Gunicorn Configuration
Create `gunicorn.conf.py`:
```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
```

## Monitoring and Maintenance

### 1. Log Files
- Django logs: `/path/to/project/logs/django.log`
- Nginx logs: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`
- System logs: `journalctl -u pg_tutoring_hub`

### 2. Health Checks
```bash
# Check application status
systemctl status pg_tutoring_hub

# Check database connection
python manage.py dbshell

# Check Django health
python manage.py check

# Monitor logs
tail -f logs/django.log
```

### 3. Backup Strategy
```bash
# Database backup
pg_dump pg_tutoring_hub_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Media files backup
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

## Security Maintenance

### Regular Tasks
1. **Update Dependencies**: `pip list --outdated`
2. **Security Audit**: `python manage.py check --deploy`
3. **Log Review**: Check for suspicious activity
4. **SSL Certificate**: Ensure certificates are valid
5. **Backup Verification**: Test backup restoration

### Security Monitoring
- Monitor failed login attempts
- Check for unusual file uploads
- Review error logs regularly
- Monitor database query patterns

## Troubleshooting

### Common Issues
1. **502 Bad Gateway**: Check gunicorn service status
2. **Static Files Not Loading**: Run `collectstatic` and check nginx config
3. **Database Connection**: Verify credentials and PostgreSQL service
4. **SSL Issues**: Check certificate paths and nginx SSL config

### Debug Commands
```bash
# Check Django configuration
python manage.py check_production

# Test database connection
python manage.py dbshell

# View recent logs
journalctl -u pg_tutoring_hub --since "1 hour ago"
```

## Support and Documentation

### Application Features
- **User Management**: Teachers, students, and parents with role-based access
- **Educational Hub**: Material upload, assignments, and progress tracking
- **Real-time Chat**: Communication between users
- **Dashboard System**: Personalized dashboards for each user type
- **File Management**: Secure file upload with validation

### Management Commands
```bash
# Create teacher account
python manage.py create_teacher --username teacher1 --email teacher@school.com --password secure123

# Production readiness check
python manage.py check_production

# Standard Django commands
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

---

**Remember**: Always test deployment in a staging environment before going to production!