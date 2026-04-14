# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`Änderung durch Austausch` — a Django 6.0 / Python 3.14 web application (generated from cookiecutter-django) serving as a digital handbook for dealing with right-wing extremist opinions and conspiracy theories. License: MIT.

Dependencies are managed with `uv` (see `uv.lock`). All Python commands must be prefixed with `uv run` unless running inside the Docker container.

## Commands

### Running & managing the app
- `uv run python manage.py <cmd>` — any Django management command (runserver, migrate, createsuperuser, makemigrations, shell_plus, …). `manage.py` hard-codes `DJANGO_SETTINGS_MODULE=config.settings.local`.
- `just up` / `just down` / `just logs` / `just build` — wrappers around `docker-compose.local.yml` (Postgres, Redis, Mailpit, Django, Celery worker/beat, Flower). `just manage <cmd>` runs `manage.py` inside the Django container.
- Local dev without Docker requires a running Postgres (`DATABASE_URL`) and Redis (`REDIS_URL`). See `.envs/.local/`.

### Tests
- `uv run pytest` — runs the full suite. Pytest config in `pyproject.toml` sets `--ds=config.settings.test --reuse-db --import-mode=importlib`.
- `uv run pytest aenderung_durch_austausch/users/tests/test_models.py::test_user_get_absolute_url` — single test.
- `uv run coverage run -m pytest && uv run coverage html` — coverage report into `htmlcov/`.
- Test discovery: files named `tests.py` or `test_*.py`. Factories live in `aenderung_durch_austausch/users/tests/factories.py`; the top-level `aenderung_durch_austausch/conftest.py` provides an autouse `_media_storage` fixture and a `user` fixture backed by `UserFactory`.

### Lint, format, type-check
- `uv run ruff check .` / `uv run ruff format .` — linting + formatting (config in `pyproject.toml`, very large ruleset enabled).
- `uv run mypy aenderung_durch_austausch` — type-checking with `django-stubs` + `djangorestframework-stubs` plugins. Settings module for stubs is pinned to `config.settings.test`.
- `uv run djlint aenderung_durch_austausch/templates --reformat` — Django template formatting.
- `uv run pre-commit run --all-files` — runs all of the above (trailing-whitespace, ruff, pyproject-fmt, djlint, django-upgrade targeting 6.0). CI runs pre-commit via `.github/workflows/ci.yml`.

### Celery
Run from the repo root with the nested app dir as cwd:
```
cd aenderung_durch_austausch
uv run celery -A config.celery_app worker -l info
uv run celery -A config.celery_app beat        # periodic tasks (DatabaseScheduler)
```

## Architecture

Cookiecutter-django layout — two top-level Python roots that together form the project:

- `config/` — Django project package (not an app). `settings/{base,local,production,test}.py` are layered (test/local/production all `from .base import *`). `urls.py` mounts `users/`, allauth, admin, DRF API (`/api/` via `api_router.py`), and drf-spectacular schema/docs. `celery_app.py` defines the Celery app used by all workers.
- `aenderung_durch_austausch/` — the Django "apps" root. `manage.py` adds this directory to `sys.path` so apps can be imported either as `aenderung_durch_austausch.users` (the canonical import) or bare `users`. Currently contains only the `users` app plus shared `templates/`, `static/`, and `contrib/sites/` (whose migrations are redirected via `MIGRATION_MODULES` in `base.py` so the built-in `django.contrib.sites` writes migrations into the project tree).
- `tests/` — project-level tests that live outside the Django apps (e.g. `test_merge_production_dotenvs_in_dotenv.py`). App-level tests live inside `aenderung_durch_austausch/<app>/tests/`.

### Custom User model — important
`aenderung_durch_austausch.users.User` replaces Django's default: `email` is `USERNAME_FIELD`, `username`/`first_name`/`last_name` are set to `None`, and a custom `UserManager` handles creation. `AUTH_USER_MODEL = "users.User"`. Allauth is configured for email-only login (`ACCOUNT_LOGIN_METHODS = {"email"}`, `ACCOUNT_EMAIL_VERIFICATION = "mandatory"`, MFA enabled via `allauth.mfa`). When adding signup fields, update both `users/forms.py` (`UserSignupForm`, `UserSocialSignupForm`) — they are wired in via `ACCOUNT_FORMS` / `SOCIALACCOUNT_FORMS`.

### API
DRF endpoints live under `/api/`. Routers are assembled in `config/api_router.py` (`DefaultRouter` in DEBUG, `SimpleRouter` otherwise). The `users` API lives at `aenderung_durch_austausch/users/api/{views,serializers}.py`. OpenAPI schema at `/api/schema/`, Swagger UI at `/api/docs/` (admin-only by default via `SPECTACULAR_SETTINGS.SERVE_PERMISSIONS`). Default auth is session + token; default permission is `IsAuthenticated`. CORS is restricted to `^/api/.*$`.

### Settings layering
All settings derive from `config/settings/base.py`. `DATABASES["default"]` comes from `DATABASE_URL` (django-environ). `base.py` reads `.env` only if `DJANGO_READ_DOT_ENV_FILE=True`; Docker passes env via `.envs/.local/.{django,postgres}`. Redis is shared between Django cache, Celery broker, and Celery result backend (`REDIS_URL`). `TIME_ZONE = "CET"`.

### Ruff conventions worth knowing
The ruff config enables a broad set (including `S`, `DJ`, `PL`, `TRY`, `EM`, `N`, `UP`, …). `lint.isort.force-single-line = true` — imports must be one name per line. Migrations and `staticfiles/` are excluded. `S101` (assert) and `SIM102` are ignored project-wide; don't re-enable them casually.
