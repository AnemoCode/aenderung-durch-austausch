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

## Internationalisierung (i18n)

Das Projekt unterstützt Deutsch (Standard) und Englisch.

**Übersetzungen aktualisieren:**

```bash
# Neue Strings extrahieren
uv run python manage.py makemessages -l en -l de --no-wrap --no-location

# Übersetzungen kompilieren (erzeugt .mo Dateien)
uv run python manage.py compilemessages
```

Die Übersetzungsdateien befinden sich im Ordner `locale/`.

## Issue-System & Kanban-Board

Für ein strukturiertes Issue-Management sind Issue-Formulare und ein Kanban-Workflow hinterlegt:

- Issue-Formulare: Bug Report, Feature Request und Task
- Automatisches Hinzufügen neuer Issues/PRs zu einem GitHub Project (Kanban)

Einmalig in den Repository-Einstellungen konfigurieren:

1. **GitHub Project** (Kanban-Board) erstellen oder auswählen.
2. Repository Variable `KANBAN_PROJECT_URL` auf die URL des Projects setzen.
3. Repository Secret `ADD_TO_PROJECT_PAT` hinterlegen (Classic PAT mit `repo` + `project` Scope), damit die Action Einträge ins Project schreiben kann.
