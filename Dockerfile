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
    PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /app /app

EXPOSE 8000

CMD ["gunicorn", "overlytics.wsgi:application", "--bind", "0.0.0.0:8000"]

# ── Worker stage (Celery worker + beat) ──────────────────────────────────────
FROM builder AS worker

# git:      GitPython delegates Repo.clone_from to the system git binary
# texcount: Perl script for LaTeX word counting; Debian package 'texcount'
#           requires only Perl — no full TeX installation needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    texlive-extra-utils \
    && rm -rf /var/lib/apt/lists/*
# No CMD — overridden per service in docker-compose.yml
