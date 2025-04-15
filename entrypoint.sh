#!/bin/sh

echo "⏳ Waiting for PostgreSQL to be ready..."
/usr/local/bin/wait-for-it.sh db:5432 --timeout=30 --strict -- echo "✅ Database is up!"

echo "🌐 Starting Django server..."
python src/pollen_forecast/djangoserver/manage.py runserver 0.0.0.0:8000