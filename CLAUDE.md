# CLAUDE.md — Development Guide

This file documents how to work with this Django codebase. Follow these guidelines when implementing issues and submitting pull requests.

## Project Overview

**Änderung durch Austausch** is a Django 5.2 digital handbook for managing conversations about far-right opinions and conspiracy theories. It uses PostgreSQL, is fully containerized with Docker, and supports German/English via i18n.

## End-of-Session Requirement (MUST DO)

Before finishing any session that changes code, run the full CI command set and confirm **every one passes**. Do not consider a session complete — and do not open a PR — until all of these are green. Run them inside the Docker stack (`docker compose exec -T web ...`) so the environment matches CI:

```bash
# 1. Django system check (the `deploy.yml` CI job runs this)
uv run python manage.py check

# 2. Full test suite with coverage (the `coverage.yml` CI job runs these)
uv run coverage run --source='.' manage.py test
uv run coverage report --fail-under=95   # CI FAILS if total coverage < 95%

# 3. Migrations are in sync with the models (catch un-generated migrations early)
uv run python manage.py makemigrations --check --dry-run
```

Key points:

- **Coverage gate:** CI enforces `--fail-under=95` on *total* coverage. New code without tests can drop the total below 95% and fail the build even when every test passes.
- **Merge result is what CI tests:** the PR CI runs against the **merge with `main`**, so merge or rebase the latest `main` into the branch first. Tests that live only on `main` (and reference code your branch changed) must also pass — a green local branch is not enough.
- **Linting/formatting** is not enforced in CI but is recommended locally: `ruff check .` and `ruff format --check .` (install with `uv add --dev ruff`; run via `uv run ruff ...`).

## Commands

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test apps.blog
python manage.py test apps.accounts

# Run a specific test module
python manage.py test apps.blog.tests.test_post_create

# Run a specific test class or method
python manage.py test apps.blog.tests.test_post_create.PostCreateTest
python manage.py test apps.blog.tests.test_post_create.PostCreateTest.test_method_name

# Via Docker Compose
docker compose exec web python manage.py test
```

### Code Coverage

```bash
# Install coverage (if not present)
uv add --dev coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# View terminal report
coverage report

# Generate HTML report
coverage html
open htmlcov/index.html
```

### Linting & Formatting

```bash
# Install ruff (if not present)
uv add --dev ruff

# Check for linting issues
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code
ruff format .

# Check formatting without applying
ruff format --check .
```

### Django Management

```bash
# Start development server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Django system check (also runs in CI)
python manage.py check

# Create a superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Shell
python manage.py shell

# Update translations
python manage.py makemessages -l de
python manage.py compilemessages
```

### Docker

```bash
# Start local development stack
docker compose up

# Run management commands inside the container
docker compose exec web python manage.py migrate
docker compose exec web python manage.py test
docker compose exec web python manage.py createsuperuser

# Rebuild after dependency changes
docker compose build
```

### Dependency Management

```bash
# Install all dependencies (locked)
uv sync --locked

# Add a new dependency
uv add <package>

# Add a dev-only dependency
uv add --dev <package>
```

## Django Best Practices

### Models

- Keep business logic in model methods or managers, not in views.
- Use `verbose_name` and `verbose_name_plural` on all models.
- Always define `__str__` on every model.
- Use `get_absolute_url()` where linking to model detail pages.
- Prefer `select_related` / `prefetch_related` to avoid N+1 queries.
- Keep migrations small and reversible; never edit applied migrations.

### Views

- Prefer class-based views (CBVs) for standard CRUD operations.
- Use `LoginRequiredMixin` (or `@login_required`) for protected views.
- Use `PermissionRequiredMixin` when fine-grained permissions are needed.
- Keep views thin — delegate logic to models or service functions.
- Use `get_object_or_404` instead of bare `.get()` in views.

### URL Configuration

- Use named URL patterns (`name=`) on every `path()`.
- Reference URLs in templates with `{% url 'name' %}` and in Python with `reverse()`.
- Group app URLs in their own `urls.py` and include them from the root config.

### Templates

- Use template inheritance (`{% extends %}` / `{% block %}`).
- Keep logic minimal in templates — move it to views or template tags.
- Always escape user content (Django auto-escapes by default; don't use `| safe` unless certain).
- Use `{% trans %}` / `{% blocktrans %}` for all user-visible strings.

### Security

- Never commit secrets; use environment variables via `django-environ`.
- Keep `DEBUG=False` in production; `ALLOWED_HOSTS` must be set.
- Use `{% csrf_token %}` in all forms.
- Validate and sanitize all user input at the form layer.

### Settings

- Environment-specific settings are loaded from `.env` via `django-environ`.
- Copy `.env.example` to `.env` for local development and fill in values.
- Never hard-code credentials or secrets in settings files.

### Code Style

- Follow PEP 8 (enforced by Ruff).
- Prefer explicit imports over wildcard imports.
- Keep functions and methods short and focused.
- Write descriptive variable and function names.

## Writing Unit Tests

### Directory Structure

Place tests in a `tests/` directory inside the relevant app:

```
apps/
  blog/
    tests/
      __init__.py
      test_<feature>.py
```

### Test Class Template

```python
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class MyFeatureTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.client.login(username="testuser", password="testpass123")

    def test_something_expected(self):
        response = self.client.get(reverse("blog:index"))
        self.assertEqual(response.status_code, 200)

    def test_permission_required(self):
        self.client.logout()
        response = self.client.get(reverse("blog:index"))
        self.assertRedirects(response, f"/login/?next=/blog/")
```

### Principles

- One logical assertion per test method where possible.
- Test names should describe the scenario: `test_unauthenticated_user_is_redirected`.
- Use `setUp` for shared fixtures; avoid duplicating setup code.
- Test the happy path, edge cases, and failure paths.
- Use `assertContains`, `assertRedirects`, `assertEqual(response.status_code, …)` for view tests.
- Use `TestCase` (wraps each test in a transaction) for database tests.
- Mock external services; never make real HTTP calls in tests.

### Testing Views

```python
def test_create_post_success(self):
    response = self.client.post(reverse("blog:post-create"), data={
        "title": "Test Post",
        "content": "Some content",
    })
    self.assertRedirects(response, reverse("blog:index"))
    self.assertTrue(Post.objects.filter(title="Test Post").exists())

def test_create_post_requires_login(self):
    self.client.logout()
    response = self.client.post(reverse("blog:post-create"), data={})
    self.assertEqual(response.status_code, 302)
```

### Testing Models

```python
def test_str_representation(self):
    topic = Topic(title="Far-right Rhetoric")
    self.assertEqual(str(topic), "Far-right Rhetoric")

def test_model_saves_correctly(self):
    topic = Topic.objects.create(title="Test Topic", author=self.user)
    self.assertEqual(Topic.objects.count(), 1)
    self.assertEqual(topic.title, "Test Topic")
```

## Pull Request Workflow

### Branch Strategy

- Create feature branches from `main`: `git checkout -b feature/short-description`
- Keep branches focused on a single issue or feature.

### Pre-PR Checklist

- [ ] All existing tests pass: `python manage.py test`
- [ ] New tests written for new functionality
- [ ] `python manage.py check` passes with no issues
- [ ] Migrations created for model changes: `python manage.py makemigrations`
- [ ] No secrets or debug code committed
- [ ] i18n strings wrapped with `{% trans %}` / `_()` where applicable

### Commit Messages

Use the conventional commits format:

```
feat: add topic tagging functionality
fix: correct redirect after login
docs: update CLAUDE.md with coverage instructions
test: add unit tests for post creation
refactor: extract permission check into mixin
chore: update dependencies
```

### Creating a PR

```bash
gh pr create \
  --title "feat: short description of change" \
  --body "## Summary

- What changed and why

## Test Plan

- [ ] Tests pass: \`python manage.py test\`
- [ ] Manual verification of the feature

Closes #<issue-number>

Generated with [Claude Code](https://claude.ai/code)"
```

### PR Description Template

```markdown
## Summary

Brief description of what this PR does and why.

## Changes

- List of key changes

## Test Plan

- [ ] \`python manage.py test\` passes
- [ ] \`python manage.py check\` passes
- [ ] Manual smoke test completed

Closes #<issue-number>
```

## CI/CD Overview

### CI Jobs (`.github/workflows/deploy.yml`)

1. **CI** — Runs `python manage.py check` against a live PostgreSQL 17-alpine instance.
2. **Build** — Multi-arch Docker image build pushed to GHCR (triggers on merge to `main`).
3. **Deploy** — SSH to production server, pulls new image, restarts with `docker compose`.

The CI job does **not** run the full test suite by default. Tests should be run locally before opening a PR.

### Environment Variables

Copy `.env.example` to `.env` for local development:

```bash
cp .env.example .env
```

Required variables:

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for dev, `False` for prod |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts |
| `POSTGRES_DB` | Database name |
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_HOST` | Database host (e.g. `db` in Docker) |
| `POSTGRES_PORT` | Database port (default `5432`) |
