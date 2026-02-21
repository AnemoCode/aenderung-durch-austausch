#!/bin/bash
set -e

# Populate .venv from the lockfile if it hasn't been installed yet
# (this happens on first start when using a bind-mounted source and named venv volume)
if [ ! -f /app/.venv/bin/python ]; then
    echo "Initialising virtual environment..."
    uv sync --locked
fi

exec "$@"
