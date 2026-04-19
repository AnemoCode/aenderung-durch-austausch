#!/bin/bash
set -e

# Run all migrations from scratch (idempotent – safe to re-run on every deploy).
echo "Running database migrations..."
python manage.py migrate --no-input

# Flush existing seed data and re-seed so every staging deploy starts with a
# known, reproducible dataset.
echo "Seeding database..."
python manage.py seed_db --flush

# Collect static files.
echo "Collecting static files..."
python manage.py collectstatic --no-input -v 0

exec "$@"
