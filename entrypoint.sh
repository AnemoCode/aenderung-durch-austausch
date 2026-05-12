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
    # `relation "blog_topic" already exists`. Commit 8acf898 restored
    # atomicity so the state can't reoccur, but existing prod DBs that
    # already entered it need a one-shot recovery.
    #
    # 0002_topic_system declares `replaces=[<the 7 original names>]`. Django's
    # MigrationLoader REMOVES the squash from `applied_migrations` whenever
    # not all of those replaced names are recorded — even if the squash row
    # itself is present. So we must fake-record all 7 replaced names (the
    # squash row is optional, included for symmetry). User data preserved.
    python - <<'PYEOF' || true
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aenderung_durch_austausch.settings")
django.setup()

from django.db import OperationalError, connection

REPLACED = (
    "0002_topic",
    "0003_topicpart_taggit",
    "0004_topic_legacy_post_id",
    "0005_comment_like_topic_field",
    "0006_migrate_posts_to_topics",
    "0007_finalize_topic_drop_post",
    "0008_topicpart_author",
)
SQUASH = "0002_topic_system"

try:
    with connection.cursor() as c:
        c.execute("SELECT to_regclass('blog_topic')")
        if c.fetchone()[0] is None:
            raise SystemExit
        placeholders = ",".join(["%s"] * len(REPLACED))
        c.execute(
            f"SELECT COUNT(*) FROM django_migrations WHERE app='blog' AND name IN ({placeholders})",
            REPLACED,
        )
        if c.fetchone()[0] == len(REPLACED):
            raise SystemExit
        print("Partial migration detected: blog_topic exists but 0002_topic_system's replaced names are not recorded.")
        print("Fake-recording the 7 replaced migration names + squash to unblock deploy (data preserved).")
        rows = [("blog", n) for n in (*REPLACED, SQUASH)]
        c.executemany(
            "INSERT INTO django_migrations (app, name, applied) "
            "SELECT %s, %s, NOW() "
            "WHERE NOT EXISTS (SELECT 1 FROM django_migrations WHERE app=%s AND name=%s)",
            [(a, n, a, n) for a, n in rows],
        )
except OperationalError:
    pass
PYEOF

    python manage.py migrate --no-input
    python manage.py collectstatic --no-input -v 0
fi

exec "$@"
