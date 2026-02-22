#!/bin/bash
set -e

# Sync the venv when it is missing OR when uv.lock is newer than the Python
# binary (i.e. dependencies have changed since the volume was last populated).
if [ ! -f /app/.venv/bin/python ] || [ /app/uv.lock -nt /app/.venv/bin/python ]; then
    echo "Syncing virtual environment..."
    uv sync --locked
fi

# Run migrations only from the web process (first argument is "python").
# Celery containers (first argument is "celery") declare a depends_on
# condition on the web healthcheck so they only start after migrations
# are confirmed applied — avoiding concurrent CREATE TABLE races.
if [ "$1" != "celery" ]; then
    python manage.py migrate --no-input
fi

exec "$@"
