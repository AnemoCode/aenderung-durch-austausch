#!/bin/bash
set -e

# Serialize concurrent migrate calls with a Postgres session-level advisory lock.
#
# Problem: the blog 0002_topic_system squash migration has atomic=False, so Django
# does not wrap its CREATE TABLE statements in a transaction.  When Dokploy starts
# multiple containers simultaneously each one races to CREATE TABLE blog_topic; all
# but one fail.  The failing container's entrypoint exits non-zero → Docker restarts
# it → same race → infinite crash loop.
#
# The simple "|| migrate" retry doesn't help because it fires immediately: the
# winning container is still running migrate_data (RunPython) and hasn't recorded
# the migration in django_migrations yet, so the loser retries and hits the same
# CREATE TABLE error again.
#
# Fix: acquire an exclusive Postgres advisory lock before spawning manage.py migrate.
# The lock is session-level and is released automatically when the outer Python
# process exits.  Concurrent containers block at pg_advisory_lock() until the lock
# holder finishes; they then acquire it, run migrate (which finds everything already
# applied), and exit 0.
echo "Running database migrations..."
python - <<'PYEOF'
import os, sys, subprocess
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aenderung_durch_austausch.settings")
import django; django.setup()
from django.db import connection

with connection.cursor() as cur:
    cur.execute("SELECT pg_advisory_lock(20260509)")
    result = subprocess.run([sys.executable, "manage.py", "migrate", "--no-input"])
    sys.exit(result.returncode)
PYEOF

# Flush existing seed data and re-seed so every staging deploy starts with a
# known, reproducible dataset.
echo "Seeding database..."
python manage.py seed_db --flush

# Collect static files.
echo "Collecting static files..."
python manage.py collectstatic --no-input -v 0

exec "$@"
