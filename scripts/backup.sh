#!/usr/bin/env bash
set -euo pipefail

# Load .env if present (production may source it differently)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"
if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  set -a; source "$ENV_FILE"; set +a
fi

DB_NAME="${POSTGRES_DB:-aenderung-durch-austausch}"
DB_USER="${POSTGRES_USER:-aenderung-durch-austausch}"
DB_PASSWORD="${POSTGRES_PASSWORD:-aenderung-durch-austausch}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"

BACKUP_DIR="$SCRIPT_DIR/../backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTFILE="$BACKUP_DIR/aenderung-durch-austausch_${TIMESTAMP}.sql.gz"

PGPASSWORD="$DB_PASSWORD" pg_dump \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  "$DB_NAME" \
  | gzip > "$OUTFILE"

echo "Backup written: $OUTFILE ($(du -sh "$OUTFILE" | cut -f1))"

# Keep only the 7 most recent backups
find "$BACKUP_DIR" -name 'aenderung-durch-austausch_*.sql.gz' -printf '%T@ %p\n' \
  | sort -rn \
  | awk 'NR>7 {print $2}' \
  | xargs -r rm --
