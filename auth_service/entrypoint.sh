#!/bin/bash
set -e

echo "Waiting for Postgres..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done
echo "Postgres is up!"

# Run Django migrations and collect static files
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start Gunicorn serving your auth service
exec gunicorn auth_service.wsgi:application --bind 0.0.0.0:8001
