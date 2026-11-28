#!/bin/sh
# Writes one database dump and one archive of the uploaded media to
# $BACKUP_DIR, copies both offsite if $BACKUP_RCLONE_REMOTE is set, and then
# deletes local backups older than $BACKUP_RETENTION_DAYS.
#
# In production this runs every night in the backup service of
# docker-compose.prod.yml. It can also be run by hand on any machine with
# pg_dump 17. Restore steps are in docs/operations/backup-restore.md.
set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Outside docker, read the database settings from the project's .env.
if [ -f "$SCRIPT_DIR/../.env" ] && [ -z "${POSTGRES_DB:-}" ]; then
  set -a
  . "$SCRIPT_DIR/../.env"
  set +a
fi

DB_NAME="${POSTGRES_DB:-aenderung-durch-austausch}"
DB_USER="${POSTGRES_USER:-aenderung-durch-austausch}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-$SCRIPT_DIR/../backups}"
MEDIA_DIR="${BACKUP_MEDIA_DIR:-}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

mkdir -p "$BACKUP_DIR"
STAMP="$(date +%Y%m%d_%H%M%S)"
PREFIX="$BACKUP_DIR/aenderung-durch-austausch_${STAMP}"

# Custom format (-Fc) is compressed and restores with pg_restore. Writing to a
# .part file first means a failed dump never looks like a finished backup.
PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_dump -Fc \
  -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -f "$PREFIX.dump.part" "$DB_NAME"
mv "$PREFIX.dump.part" "$PREFIX.dump"
echo "Database backup written: $PREFIX.dump ($(du -h "$PREFIX.dump" | cut -f1))"

if [ -n "$MEDIA_DIR" ] && [ -d "$MEDIA_DIR" ]; then
  tar -czf "$PREFIX.media.tar.gz.part" -C "$MEDIA_DIR" .
  mv "$PREFIX.media.tar.gz.part" "$PREFIX.media.tar.gz"
  echo "Media backup written: $PREFIX.media.tar.gz ($(du -h "$PREFIX.media.tar.gz" | cut -f1))"
fi

if [ -n "${BACKUP_RCLONE_REMOTE:-}" ]; then
  for f in "$PREFIX".dump "$PREFIX".media.tar.gz; do
    [ -f "$f" ] && rclone copy "$f" "$BACKUP_RCLONE_REMOTE"
  done
  echo "Copied to $BACKUP_RCLONE_REMOTE"
fi

find "$BACKUP_DIR" -type f -name 'aenderung-durch-austausch_*' -mtime +"$RETENTION_DAYS" -print -delete
