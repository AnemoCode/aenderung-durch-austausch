#!/bin/bash
set -e

# Recover from partial non-atomic migration state.
#
# 0002_topic_system previously had atomic=False, which meant CREATE TABLE blog_topic
# committed immediately. If the process was killed before django_migrations was updated,
# the DB ends up with blog_topic existing but the migration unrecorded — causing an
# infinite crash loop on every subsequent deploy.
#
# This script detects that state, drops all blog_* tables, and clears blog migration
# records so that migrate can re-apply everything cleanly from 0001_initial.
echo "Checking migration state..."
python - <<'PYEOF' || true
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aenderung_durch_austausch.settings")
django.setup()

from django.db import connection, OperationalError

try:
    with connection.cursor() as c:
        c.execute("SELECT to_regclass('blog_topic')")
        blog_topic_exists = c.fetchone()[0] is not None
except OperationalError:
    # DB not reachable yet — migrate will handle connectivity errors itself.
    blog_topic_exists = False

if blog_topic_exists:
    with connection.cursor() as c:
        try:
            c.execute(
                "SELECT 1 FROM django_migrations WHERE app='blog' AND name='0002_topic_system'"
            )
            recorded = c.fetchone() is not None
        except Exception:
            recorded = True  # Assume OK if we can't check

    if not recorded:
        print("Partial migration detected: blog_topic exists but 0002_topic_system not recorded.")
        print("Dropping all blog_* tables and clearing blog migration records...")
        with connection.cursor() as c:
            c.execute("""
                DO $$
                DECLARE r RECORD;
                BEGIN
                    FOR r IN
                        SELECT tablename FROM pg_tables
                        WHERE schemaname = 'public' AND tablename LIKE 'blog_%'
                    LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END;
                $$
            """)
            c.execute("DELETE FROM django_migrations WHERE app = 'blog'")
        print("Recovery complete. Migrate will re-apply blog migrations from scratch.")
PYEOF

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
