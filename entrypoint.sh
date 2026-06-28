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

# Ensure the user-uploaded media directory exists.  In docker the host bind-mount
# usually creates this, but when MEDIA_ROOT points somewhere unmounted (or in
# non-docker setups) the dir may be missing and uploads would 500.
mkdir -p "${MEDIA_ROOT:-/app/data/media}"

# Run migrations and collect static files only from the web process (first
# argument is not "celery").  Celery containers declare a depends_on condition
# on the web healthcheck so they only start after migrations are confirmed
# applied — avoiding concurrent CREATE TABLE races.
if [ "$1" != "celery" ]; then
    python manage.py migrate --no-input
    python manage.py collectstatic --no-input -v 0
fi

exec "$@"
