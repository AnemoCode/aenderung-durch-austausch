#!/bin/bash
set -e

# Run all migrations from scratch (idempotent – safe to re-run on every deploy).
# The retry handles the concurrent-start race that occurs when Dokploy triggers a
# pre-deploy migrate AND the container entrypoint also runs migrate simultaneously.
# With atomic=False on the topic-system squash migration Django's transaction lock
# does not protect the CREATE TABLE statements, so whichever process loses the race
# exits non-zero; the second attempt finds everything applied and succeeds.
echo "Running database migrations..."
python manage.py migrate --no-input \
  || python manage.py migrate --no-input

# Flush existing seed data and re-seed so every staging deploy starts with a
# known, reproducible dataset.
echo "Seeding database..."
python manage.py seed_db --flush

# Collect static files.
echo "Collecting static files..."
python manage.py collectstatic --no-input -v 0

exec "$@"
