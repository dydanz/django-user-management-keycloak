#!/bin/bash

# Wait for database to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "PostgreSQL is ready."

# Check if manage.py exists, if not, run setup.sh
if [ ! -f "/app/manage.py" ]; then
  echo "Django project not initialized. Running setup.sh..."
  chmod +x /app/setup.sh
  /app/setup.sh
fi

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if needed
if [[ -n "$DJANGO_SUPERUSER_USERNAME" && -n "$DJANGO_SUPERUSER_EMAIL" && -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput
fi

# Start Gunicorn
echo "Starting Gunicorn server..."
exec "$@" 