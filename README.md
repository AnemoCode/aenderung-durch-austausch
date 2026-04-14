# Änderung durch Austausch

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

## Details

| Komponente | Version |
|---|---|
| Framework | Django 5.2 |
| Datenbank | PostgreSQL 17 |
| Python | 3.12+ |
| Paketverwaltung | uv |
