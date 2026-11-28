# syntax=docker/dockerfile:1

# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TAILWIND_BIN_DIR=/opt/tailwind

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Download the Tailwind binary in its own layer so it stays cached until the
# script (and with it the pinned version) changes. It lives outside /app, so
# the dev bind mount doesn't hide it and the runtime image doesn't carry it.
COPY scripts/tailwind.sh scripts/tailwind.sh
RUN scripts/tailwind.sh --install

COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

RUN scripts/tailwind.sh

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# The deploy workflow passes the commit SHA so Sentry can tell releases apart.
ARG GIT_SHA=""
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SENTRY_RELEASE=${GIT_SHA}

COPY --from=builder /app /app
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "aenderung_durch_austausch.wsgi:application", "--bind", "0.0.0.0:8000"]

# ── Staging stage ─────────────────────────────────────────────────────────────
# Extends the runtime image with a staging-specific entrypoint that runs fresh
# migrations, seeds the database with representative test data, and then starts
# the application server.  Build with: docker build --target staging .
FROM runtime AS staging

COPY entrypoint.staging.sh /entrypoint.staging.sh
RUN chmod +x /entrypoint.staging.sh

ENTRYPOINT ["/entrypoint.staging.sh"]
CMD ["gunicorn", "aenderung_durch_austausch.wsgi:application", "--bind", "0.0.0.0:8000"]
