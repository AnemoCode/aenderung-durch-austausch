#!/bin/sh
# Runs backup.sh once a day at $BACKUP_TIME (UTC, default 03:00). This is the
# command of the backup service in docker-compose.prod.yml.
#
# A plain sleep loop instead of cron, because busybox crond does not pass the
# container's environment (database password etc.) on to its jobs.
set -eu

BACKUP_TIME="${BACKUP_TIME:-03:00}"
trap 'exit 0' TERM INT

if [ -n "${BACKUP_RCLONE_REMOTE:-}" ] && ! command -v rclone >/dev/null; then
  apk add --no-cache rclone
fi

while true; do
  now="$(date -u +%s)"
  next="$(date -u -d "$(date -u +%Y-%m-%d) $BACKUP_TIME" +%s)"
  if [ "$next" -le "$now" ]; then
    next=$((next + 86400))
  fi
  echo "Next backup at $(date -u -d "@$next" '+%Y-%m-%d %H:%M') UTC"
  # Sleep in the background and wait for it, so `docker stop` ends the loop
  # right away instead of after its 10 second timeout.
  sleep $((next - now)) &
  wait $!
  sh /scripts/backup.sh || echo "Backup FAILED, see the output above" >&2
done
