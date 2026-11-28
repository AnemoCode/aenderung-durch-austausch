# Backups und Wiederherstellung

Jede Nacht um 03:00 UTC sichert der Service `backup` die Datenbank und alle hochgeladenen Medien. Er läuft auf dem Server neben `web` und `db` und ist in `docker-compose.prod.yml` definiert. Das Skript dazu ist `scripts/backup.sh`.

Pro Nacht entstehen zwei Dateien in `/opt/aenderung-durch-austausch/backups`:

- `aenderung-durch-austausch_<Datum>_<Zeit>.dump` ist die Datenbank im Custom-Format von `pg_dump`. Sie ist schon komprimiert.
- `aenderung-durch-austausch_<Datum>_<Zeit>.media.tar.gz` enthält alle Uploads aus dem Medienordner.

Backups, die älter als 30 Tage sind, löscht das Skript selbst. Das lässt sich mit `BACKUP_RETENTION_DAYS` ändern, die Uhrzeit mit `BACKUP_TIME`.

## Prüfen, ob die Backups laufen

```bash
cd /opt/aenderung-durch-austausch
docker compose -f docker-compose.prod.yml logs --tail 20 backup
ls -lh backups/
```

Im Log steht nach jedem Lauf „Database backup written“ und die Zeit des nächsten Laufs. Schlägt ein Backup fehl, steht dort „Backup FAILED“ und der Service versucht es in der nächsten Nacht wieder.

Ein Backup sofort auslösen, zum Beispiel vor einem riskanten Update:

```bash
docker compose -f docker-compose.prod.yml exec backup sh /scripts/backup.sh
```

## Offsite-Kopie

Liegen die Backups nur auf dem Server, sind sie mit ihm zusammen weg. Deshalb kann das Skript jede Sicherung zusätzlich mit [rclone](https://rclone.org) woanders hin kopieren. Das ist erst aktiv, wenn `BACKUP_RCLONE_REMOTE` gesetzt ist. Beispiel für eine Hetzner Storage Box über SFTP in der `.env` auf dem Server:

```bash
BACKUP_RCLONE_REMOTE=storagebox:aeda-backups
RCLONE_CONFIG_STORAGEBOX_TYPE=sftp
RCLONE_CONFIG_STORAGEBOX_HOST=uXXXXXX.your-storagebox.de
RCLONE_CONFIG_STORAGEBOX_PORT=23
RCLONE_CONFIG_STORAGEBOX_USER=uXXXXXX
RCLONE_CONFIG_STORAGEBOX_PASS=<Ausgabe von: rclone obscure 'passwort'>
```

Auf dem Ziel löscht das Skript nichts. Wie lange dort aufbewahrt wird, regelt man beim Anbieter, zum Beispiel über Snapshots der Storage Box.

## Wiederherstellen

Die Wiederherstellung überschreibt die laufende Datenbank. Vorher also ein frisches Backup ziehen (siehe oben), damit man zurück kann.

1. Die App anhalten, damit niemand während der Wiederherstellung schreibt:

   ```bash
   cd /opt/aenderung-durch-austausch
   docker compose -f docker-compose.prod.yml stop web
   ```

2. Die Datenbank aus dem gewünschten Dump wiederherstellen. `--clean --if-exists` löscht vorher die vorhandenen Tabellen:

   ```bash
   docker compose -f docker-compose.prod.yml exec -T db sh -c \
     'pg_restore --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
     < backups/aenderung-durch-austausch_20261127_030000.dump
   ```

3. Falls auch Medien fehlen, das passende Archiv in den Medienordner entpacken:

   ```bash
   tar -xzf backups/aenderung-durch-austausch_20261127_030000.media.tar.gz \
     -C /opt/aenderung-durch-austausch/media
   ```

4. Die App wieder starten und kurz durchklicken:

   ```bash
   docker compose -f docker-compose.prod.yml start web
   ```

Getestet am 27.11.2026 mit den Staging-Seed-Daten: Dump und Wiederherstellung in eine leere Datenbank ergaben dieselben Zeilenzahlen in allen geprüften Tabellen.
