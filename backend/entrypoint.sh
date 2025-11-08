#!/bin/bash
set -e  # exit on error

echo "Running migrations..."
python3 manage.py migrate

# Check if data already exists before trying to load the massive JSON
echo "Checking if Coordinates table already populated..."
python3 manage.py shell <<EOF
from api.models import Coordinates
count = Coordinates.objects.count()
print(f"Existing records: {count}")
EOF

# Only load data if empty
python3 manage.py shell <<EOF
from django.core.management import call_command
from api.models import Coordinates

if Coordinates.objects.count() == 0:
    print("Coordinates empty. Loading fixture...")
    call_command('loaddata', 'coordinates.json')
else:
    print("Coordinates already loaded. Skipping loaddata.")
EOF

# Finally start the ASGI server
echo "Starting Daphne..."
daphne backend.asgi:application -b 0.0.0.0 -p $PORT
# daphne backend.asgi:application
