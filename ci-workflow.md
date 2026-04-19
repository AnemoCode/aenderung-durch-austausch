# CI Workflow Setup

Copy the YAML below into `.github/workflows/ci.yml` in your repository.

```yaml
name: CI

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Install dependencies
        run: uv sync --group dev

      - name: Install coverage
        run: uv pip install coverage

      - name: Run tests with coverage
        run: |
          uv run coverage run manage.py test --settings=aenderung_durch_austausch.test_settings
          uv run coverage report --fail-under=90
```

## Notes

- **Branch triggers:** Runs on every push/PR to `main`. Adjust as needed.
- **Coverage threshold:** `--fail-under=90` matches the `.coveragerc` config — the job fails if coverage drops below 90%.
- **No `.env` required:** `test_settings.py` uses an in-memory SQLite database, so no secrets need to be configured in GitHub.
- **`uv` is used** to match the project's existing lock file (`uv.lock`), ensuring reproducible installs.
