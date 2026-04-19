# CLAUDE.md – Development Guide

This file provides guidance for Claude when implementing issues and pull requests in this Django project.

## Project Overview

**Änderung durch Austausch** is a Django 5.2 web application serving as a digital handbook for discussing far-right opinions and conspiracy theories. It uses PostgreSQL, Docker, and UV for package management.

## Environment Setup

This project uses [UV](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install dependencies
uv sync --locked

# Activate the virtual environment
source .venv/bin/activate
```

Copy `.env.example` to `.env` and configure the required environment variables before running locally.

For local development with Docker:

```bash
docker-compose up
```

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
python manage.py test apps.blog.tests.test_post_create.PostCreateViewTest
python manage.py test apps.blog.tests.test_post_create.PostCreateViewTest.test_authenticated_user_can_create_post

# Run tests with verbosity
python manage.py test --verbosity=2

# Preserve the test database between runs (faster for iterative testing)
python manage.py test --keepdb
```

### Test Coverage

Install coverage if not present:

```bash
uv add --dev coverage
```

Then run:

```bash
# Run tests with coverage
coverage run manage.py test

# Generate a terminal report
coverage report

# Generate an HTML report (opens in browser)
coverage html
open htmlcov/index.html

# Set minimum coverage threshold
coverage report --fail-under=80
```

### Linting and Formatting

This project does not yet have linting tools configured. When adding linting, use **Ruff** (fast Python linter and formatter):

```bash
uv add --dev ruff

# Check for linting errors
ruff check .

# Auto-fix fixable errors
ruff check . --fix

# Format code
ruff format .

# Check formatting without modifying
ruff format . --check
```

Recommended `pyproject.toml` configuration for Ruff:

```toml
[tool.ruff]
target-version = "py312"
line-length = 119

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "DJ"]
ignore = ["E501"]

[tool.ruff.lint.per-file-ignores]
"*/migrations/*.py" = ["E501", "F401"]
```

### Django System Checks

```bash
# Run Django's built-in system checks (also used in CI)
python manage.py check

# Check for deployment readiness
python manage.py check --deploy
```

### Database Migrations

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check for missing migrations (important before committing)
python manage.py migrate --check
```

### Internationalization

```bash
# Collect translatable strings
python manage.py makemessages -l de -l en

# Compile translations
python manage.py compilemessages
```

### Static Files

```bash
python manage.py collectstatic --noinput
```

## Django Best Practices

### Models

- Use `verbose_name` and `verbose_name_plural` on every model.
- Always add `__str__` methods that return a human-readable string.
- Use `get_absolute_url()` for model URLs.
- Define `class Meta` with `ordering` to avoid unpredictable query ordering.
- Add `db_index=True` on fields used in `filter()`, `order_by()`, or `select_related()`.
- Use `select_related()` for ForeignKey/OneToOne traversals and `prefetch_related()` for ManyToMany.
- Never make raw SQL queries; use the ORM. If raw SQL is unavoidable, parameterize all inputs.
- Place business logic in models or service functions, not in views.

### Views

- Prefer class-based views (CBVs) for standard CRUD operations using Django's built-in generics (`ListView`, `DetailView`, `CreateView`, etc.).
- Use `LoginRequiredMixin` for views that require authentication.
- Never trust user input — validate with forms or serializers.
- Use `get_object_or_404()` instead of `Model.objects.get()` to avoid unhandled `DoesNotExist` exceptions in views.
- Keep views thin: move complex logic to models, managers, or dedicated service functions.

### URLs

- Name every URL pattern and use `reverse()` or `{% url %}` instead of hardcoding paths.
- Group app URLs in `apps/<app>/urls.py` and include them in the root `urls.py`.

### Templates

- Use template inheritance (`{% extends %}` and `{% block %}`).
- Never execute business logic in templates; pass prepared context from views.
- Use `{% load i18n %}` and `{% trans %}` / `{% blocktrans %}` for all user-visible strings.
- Escape user-generated content — Django auto-escapes by default; never use `| safe` on untrusted data.

### Security

- Never expose secret keys, database credentials, or tokens. Use `django-environ` (already installed) to load from `.env`.
- Always use `{% csrf_token %}` in forms.
- Mark `HttpOnly` and `Secure` cookies in production settings.
- Validate file uploads with allowed content types and size limits.
- Use Django's permission system (`permission_required`, `PermissionRequiredMixin`) for access control.

### Settings

- Use `django-environ` to read all sensitive values from environment variables.
- Keep a single `settings.py`; use environment variables to switch between development and production behaviour.
- Set `DEBUG = False` in production.

### Code Style

- Follow [PEP 8](https://pep8.org/) with a line length of 119 characters.
- Use descriptive variable and function names; avoid abbreviations.
- Keep functions and methods small and focused on a single responsibility.
- Avoid circular imports — use `apps.get_model()` when referencing models across apps.

## Writing Unit Tests

### Structure

Place tests in `apps/<app>/tests/` as separate modules per feature area:

```
apps/
  blog/
    tests/
      __init__.py
      test_models.py
      test_views.py
      test_forms.py
```

### Test Class Template

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class MyFeatureTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create shared, read-only objects for all tests in this class."""
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword123",
        )

    def setUp(self):
        """Set up per-test state (e.g. log in)."""
        self.client = Client()
        self.client.login(email="test@example.com", password="testpassword123")

    def test_example(self):
        response = self.client.get(reverse("some-url-name"))
        self.assertEqual(response.status_code, 200)
```

### Key Principles

- Use `setUpTestData()` for expensive, read-only fixtures shared across tests; use `setUp()` for per-test state.
- Each test method should test **one** thing.
- Test names must be descriptive: `test_unauthenticated_user_is_redirected_to_login`.
- Test the happy path, error cases, edge cases, and permission boundaries.
- Use `assertContains`, `assertRedirects`, `assertFormError` etc. rather than raw string checks.
- Do **not** mock the database — tests run against a real (test) database.
- Avoid testing Django internals (e.g. that `Model.save()` works); test your own code.

### Testing Views

```python
def test_view_requires_login(self):
    self.client.logout()
    response = self.client.get(reverse("protected-view"))
    self.assertRedirects(response, f"/accounts/login/?next={reverse('protected-view')}")

def test_view_returns_correct_template(self):
    response = self.client.get(reverse("my-view"))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "blog/my_template.html")

def test_post_creates_object(self):
    data = {"title": "Test", "content": "Body text"}
    response = self.client.post(reverse("create-view"), data)
    self.assertEqual(response.status_code, 302)
    self.assertEqual(MyModel.objects.count(), 1)
```

### Testing Models

```python
def test_str_representation(self):
    obj = MyModel(title="Hello")
    self.assertEqual(str(obj), "Hello")

def test_get_absolute_url(self):
    obj = MyModel.objects.create(title="Hello")
    self.assertEqual(obj.get_absolute_url(), f"/blog/{obj.pk}/")
```

## Pull Request Workflow

When implementing an issue, Claude should:

1. **Work on the existing branch** created for the issue (branch names follow `claude/issue-<number>-<date>`).
2. **Run the test suite** after implementation to verify nothing is broken:
   ```bash
   python manage.py test
   ```
3. **Run Django system checks**:
   ```bash
   python manage.py check
   ```
4. **Check for missing migrations**:
   ```bash
   python manage.py makemigrations --check --dry-run
   ```
5. **Commit changes** with a clear, descriptive message referencing the issue:
   ```bash
   git add <files>
   git commit -m "feat: <short description>

   Closes #<issue-number>

   Co-authored-by: <user> <user@users.noreply.github.com>"
   ```
6. **Push the branch**:
   ```bash
   /home/runner/work/_actions/anthropics/claude-code-action/v1/scripts/git-push.sh origin <branch-name>
   ```
7. **Create a pull request** using the GitHub CLI:
   ```bash
   gh pr create \
     --title "<title>" \
     --body "<description>\n\nCloses #<issue-number>\n\nGenerated with [Claude Code](https://claude.ai/code)" \
     --base main
   ```
   Or provide a manual PR link in the issue comment.

### PR Description Template

```markdown
## Summary

Brief description of what was changed and why.

## Changes

- Change 1
- Change 2

## Test plan

- [ ] Run `python manage.py test` — all tests pass
- [ ] Run `python manage.py check` — no issues
- [ ] Manually verify the feature in the browser

Closes #<issue-number>

Generated with [Claude Code](https://claude.ai/code)
```

## CI/CD

The CI pipeline (`.github/workflows/deploy.yml`) runs `python manage.py check` against a PostgreSQL 17 service before building and deploying. Ensure all Django system checks pass before opening a PR.

Docker images are built for ARM architecture and pushed to `ghcr.io`. Production deployment is SSH-based with a health check at `GET /health/`.
