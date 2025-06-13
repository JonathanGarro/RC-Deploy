#!/bin/bash

# Wait for the database to be ready
echo "Waiting for database..."
sleep 5

# Generate migrations for custom apps if they don't exist
echo "Generating migrations..."
python manage.py makemigrations surge users

# Apply database migrations
echo "Applying migrations..."
python manage.py migrate

# Create superuser if not exists
echo "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created.')
else:
    print('Superuser already exists.')
"

# Populate initial data
echo "Populating initial data..."
python manage.py populate_initial_data

# Start the Django development server
echo "Starting server..."
exec "$@"
