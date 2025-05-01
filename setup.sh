#!/bin/bash

# Create Django project
django-admin startproject core .

# Create apps
python manage.py startapp users
python manage.py startapp api

# Create frontend directory
mkdir -p frontend

# Create necessary directories
mkdir -p core/templates
mkdir -p core/static
mkdir -p media

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser if environment variables are set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py createsuperuser --noinput
    echo "Superuser created."
fi

# Set permissions
chmod +x setup.sh 