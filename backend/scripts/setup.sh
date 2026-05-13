#!/bin/bash
# PG Tutoring Hub - Development Setup Script

echo "🚀 Setting up PG Tutoring Hub for development..."

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run migrations
echo "🗄️ Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating superuser account..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.get_or_create(username='patience', defaults={'email': 'patience@pgtutoring.com', 'user_type': 'teacher', 'is_superuser': True, 'is_staff': True})" | python manage.py shell

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Check for any issues
echo "🔍 Running system checks..."
python manage.py check

echo "✅ Setup complete! Run 'python manage.py runserver' to start the development server."