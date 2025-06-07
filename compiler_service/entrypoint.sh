#!/bin/bash
set -e

echo "Waiting for Redis..."
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 1
done
echo "Redis is up!"

echo "Waiting for RabbitMQ..."
while ! nc -z $RABBITMQ_HOST $RABBITMQ_PORT; do
  sleep 1
done
echo "RabbitMQ is up!"

# Run Django migrations and collect static files
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Check the first argument to decide which process to run.
# If "worker" is passed, run the Celery worker.
if [ "$1" = "worker" ]; then
    echo "Starting Celery worker..."
    exec celery -A compiler_service worker --loglevel=info
else
    echo "Starting Daphne server..."
    exec daphne -b 0.0.0.0 -p 8002 compiler_service.asgi:application
fi
