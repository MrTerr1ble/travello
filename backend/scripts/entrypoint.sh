#!/bin/bash

echo "Apply database migrations"
python manage.py migrate

echo "Ensure collected_static directory exists"
mkdir -p /app/collected_static

echo "Collect static files"
python manage.py collectstatic --noinput

echo "Copy collected static files to volume mount"
cp -r /app/collected_static/. /backend_static/static/

exec "$@"