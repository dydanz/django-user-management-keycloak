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

# Set permissions
chmod +x setup.sh 