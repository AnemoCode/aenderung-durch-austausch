# Änderung durch Austausch 🫂

Digitales Handbuch zum analogen Umgang mit rechtsextremen Meinungen und Verschwörungstheorien.

---

## Development Setup

**Voraussetzungen:** Docker & Docker Compose

```bash
# Projekt starten
docker compose up

# Datenbank-Migrationen ausführen
docker compose exec web python manage.py migrate

# Admin-Benutzer erstellen
docker compose exec web python manage.py createsuperuser
```

Die Anwendung ist anschließend unter [http://localhost:8000](http://localhost:8000) erreichbar,  
das Admin-Panel unter [http://localhost:8000/admin](http://localhost:8000/admin).

## Unit Tests

The test suite uses Django's built-in test runner with an in-memory SQLite database (no running services needed).

```bash
# Run all tests
python manage.py test --settings=aenderung_durch_austausch.test_settings

# Run tests with coverage report
coverage run manage.py test --settings=aenderung_durch_austausch.test_settings
coverage report

# Run tests for a specific app
python manage.py test apps.accounts --settings=aenderung_durch_austausch.test_settings
python manage.py test apps.blog --settings=aenderung_durch_austausch.test_settings
```

The suite currently achieves **≥ 97 % coverage** across all application code.

---

## Details

| Komponente | Version |
|---|---|
| Framework | Django 5.2 |
| Datenbank | PostgreSQL 17 |
| Python | 3.12+ |
| Paketverwaltung | uv |