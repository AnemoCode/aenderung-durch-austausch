# Coverage Check — GitHub Actions Workflow

Copy the YAML below into `.github/workflows/coverage.yml` to add a coverage-check job to your CI.

The workflow:
- Runs on every push and pull request against `main`
- Spins up a PostgreSQL 17 service (matching the existing CI setup)
- Installs all dependencies (including dev) with `uv`
- Runs the full test suite under `coverage`
- Prints a per-file coverage report in the job log
- **Fails the job** if total coverage drops below the configured threshold (default: 95 %)

## Workflow YAML

```yaml
name: Coverage

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  coverage:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:17-alpine
        env:
          POSTGRES_DB: aenderung-durch-austausch
          POSTGRES_USER: aenderung-durch-austausch
          POSTGRES_PASSWORD: aenderung-durch-austausch
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    env:
      DJANGO_SECRET_KEY: ci-placeholder-not-used-in-production
      DEBUG: "True"
      POSTGRES_DB: aenderung-durch-austausch
      POSTGRES_USER: aenderung-durch-austausch
      POSTGRES_PASSWORD: aenderung-durch-austausch
      POSTGRES_HOST: localhost
      POSTGRES_PORT: "5432"

    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: uv sync --locked --all-groups

      - name: Run tests with coverage
        run: uv run coverage run --source='.' manage.py test

      - name: Coverage report
        run: uv run coverage report --show-missing

      - name: Enforce minimum coverage
        run: uv run coverage report --fail-under=95
```

## Usage

1. Copy the file to `.github/workflows/coverage.yml`.
2. Push to GitHub — the workflow will run automatically on the next push or PR against `main`.
3. Adjust the `--fail-under` threshold in the last step to suit your target (currently set to `95`; the project is already at 99 %).

## Notes

- Coverage settings (`omit`, `exclude_lines`) are read from `pyproject.toml` automatically — no extra flags needed.
- To trigger the workflow manually, add `workflow_dispatch:` under the `on:` key.
- To upload results to [Codecov](https://codecov.io), add the following step after "Coverage report":

```yaml
      - name: Upload to Codecov
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
```
