# PG Tutoring Hub - Project Documentation

## Overview

PG Tutoring Hub is a comprehensive web application built with Django to support Patience Gwanyanya's tutoring business. The platform provides user management, educational content delivery, real-time communication, and progress tracking.

## 🏗️ Project Structure

```
pg_tutoring_hub/
├── 📁 core/                    # Main app - home page, landing pages
├── 📁 users/                   # User authentication and profiles
├── 📁 dashboard/               # Role-based dashboards
├── 📁 hub/                     # Educational materials and assignments
├── 📁 chat/                    # Real-time communication system
├── 📁 templates/               # HTML templates
├── 📁 static/                  # CSS, JavaScript, images
├── 📁 media/                   # User uploads (materials, profile pics)
├── 📁 docs/                    # Project documentation
├── 📁 pg_hub/                  # Django project settings
└── 📄 manage.py               # Django management script
```

## 🎯 Features

### User Management

- **Multi-role system**: Students, Parents, Teachers
- **Custom user model** with role-specific fields
- **Registration flow** with role-based redirects
- **Profile management** with image uploads

### Dashboards

- **Teacher Dashboard**: Manage students, create materials/assignments
- **Student Dashboard**: Access materials, view assignments, track progress
- **Parent Dashboard**: Monitor children's progress and communication

### Educational Hub

- **Material Management**: Upload and organize learning materials
- **Assignment System**: Create and assign tasks to students
- **Progress Tracking**: Monitor completion rates and performance

### Communication

- **Real-time Chat**: WebSocket-based messaging system
- **Announcements**: Broadcast messages to groups
- **Direct Communication**: Teacher-student/parent messaging

## 🛠️ Technical Stack

- **Backend**: Django 5.2.7
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, Custom CSS/JS
- **Real-time**: Django Channels + Redis
- **Authentication**: Django's built-in auth with custom user model
- **File Handling**: Django's file upload system

## 📝 Quick Start

1. **Activate virtual environment**:

   ```bash
   source venv/bin/activate
   ```

2. **Run migrations**:

   ```bash
   python manage.py migrate
   ```

3. **Create superuser** (Teacher account):

   ```bash
   echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('patience', 'patience@pgtutoring.com', '1234', user_type='teacher')" | python manage.py shell
   ```

4. **Start development server**:

   ```bash
   python manage.py runserver 8001
   ```

5. **Access the application**: http://127.0.0.1:8001/

## 🔐 User Roles & Permissions

### Teacher (Patience)

- Full system access
- Create and manage materials
- Assign tasks to students
- Send announcements
- View all student progress
- Manage user accounts

### Students

- Access assigned materials
- Submit assignments
- Chat with teacher
- View personal progress
- Update profile information

### Parents

- View children's progress
- Communicate with teacher
- Receive announcements
- Monitor assignment completion

## 🌐 URL Structure

```
/                           # Home page
/users/login/               # User login
/users/register/            # User registration
/dashboard/                 # Role-based dashboard redirect
/dashboard/teacher/         # Teacher dashboard
/dashboard/student/         # Student dashboard
/dashboard/parent/          # Parent dashboard
/hub/                       # Materials hub
/chat/                      # Chat system
/admin/                     # Django admin panel
```

## 📊 Database Models

### Users App

- `CustomUser`: Extended user model with role and profile fields

### Hub App

- `Material`: Educational content uploads
- `Assignment`: Tasks assigned to students
- `StudentProgress`: Completion tracking

### Chat App

- `ChatRoom`: Communication channels
- `Message`: Individual messages

## 🎨 Design System

### Colors

- Primary: #667eea (Blue)
- Secondary: #764ba2 (Purple)
- Accent: #fcb69f (Peach)
- Success: #28a745
- Warning: #ffc107
- Danger: #dc3545

### Components

- Gradient buttons and backgrounds
- Card-based layouts
- Responsive design
- Smooth animations
- Bootstrap 5 components

## 🔧 Development Guidelines

### Code Organization

- Each app has specific responsibility
- Templates organized by app
- Static files centralized
- Media files organized by type

### Best Practices

- Use Django's built-in features
- Follow Django naming conventions
- Write descriptive commit messages
- Test before deployment
- Keep sensitive data in environment variables

## 🚀 Deployment Checklist

- [ ] Set `DEBUG = False`
- [ ] Configure production database
- [ ] Set up static file serving
- [ ] Configure email backend
- [ ] Set up Redis for production
- [ ] Configure domain and SSL
- [ ] Set up backup strategy

## 📞 Support

For technical support or questions about the PG Tutoring Hub, contact the development team or refer to the Django documentation for framework-specific issues.

---

_Last updated: October 3, 2025_
