#!/bin/bash
set -e

# Sync the venv when it is missing OR when uv.lock is newer than the Python
# binary (i.e. dependencies have changed since the volume was last populated).
# Guard with command -v because the runtime image does not include uv.
if command -v uv &>/dev/null; then
    if [ ! -f /app/.venv/bin/python ] || [ /app/uv.lock -nt /app/.venv/bin/python ]; then
        echo "Syncing virtual environment..."
        uv sync --locked
    fi
fi

# Run migrations and collect static files only from the web process (first
# argument is not "celery").  Celery containers declare a depends_on condition
# on the web healthcheck so they only start after migrations are confirmed
# applied — avoiding concurrent CREATE TABLE races.
if [ "$1" != "celery" ]; then
    # Recover from partial non-atomic migration state.
    #
    # The original 0002_topic_system migration ran with atomic=False, so a
    # process crash between CREATE TABLE blog_topic and the django_migrations
    # INSERT left some deployments with the table present but no migration
    # recorded. Every subsequent deploy then crashes with
    # `relation "blog_topic" already exists`. The fix in commit 8acf898
    # restored atomicity so the state can't reoccur, but existing prod DBs
    # that already entered it need a one-shot recovery. We fake-record the
    # squash (which represents the current on-disk schema) so migrate moves
    # on. User data in blog_topic and friends is preserved.
    python - <<'PYEOF' || true
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aenderung_durch_austausch.settings")
django.setup()

from django.db import OperationalError, connection

REPLACED = (
    "0002_topic_system",
    "0002_topic",
    "0003_topicpart_taggit",
    "0004_topic_legacy_post_id",
    "0005_comment_like_topic_field",
    "0006_migrate_posts_to_topics",
    "0007_finalize_topic_drop_post",
    "0008_topicpart_author",
)

try:
    with connection.cursor() as c:
        c.execute("SELECT to_regclass('blog_topic')")
        if c.fetchone()[0] is None:
            raise SystemExit
        placeholders = ",".join(["%s"] * len(REPLACED))
        c.execute(
            f"SELECT 1 FROM django_migrations WHERE app='blog' AND name IN ({placeholders}) LIMIT 1",
            REPLACED,
        )
        if c.fetchone() is not None:
            raise SystemExit
        print("Partial migration detected: blog_topic exists but 0002_topic_system is not recorded.")
        print("Fake-recording blog.0002_topic_system to unblock deploy (data preserved).")
        c.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES ('blog', '0002_topic_system', NOW())"
        )
except OperationalError:
    pass
PYEOF

    python manage.py migrate --no-input
    python manage.py collectstatic --no-input -v 0
fi

exec "$@"
