#!/usr/bin/env bash
# ─────────────────────────────────────────────────────
# backup_pg.sh — pg_dump nightly, retain 14 days
# Cron:  0 3 * * * /opt/dealix/scripts/infra/backup_pg.sh
# ─────────────────────────────────────────────────────
set -euo pipefail

DSN="${DATABASE_URL:-postgresql://dealix:dealix_local_dev_2026@127.0.0.1:5432/dealix}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/dealix}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"

mkdir -p "$BACKUP_DIR"
STAMP=$(date +%Y%m%d_%H%M%S)
OUT="${BACKUP_DIR}/dealix_${STAMP}.sql.gz"

pg_dump --no-owner --no-privileges --clean --if-exists "$DSN" | gzip -9 > "$OUT"
echo "✓ Backup → $OUT ($(du -h "$OUT" | cut -f1))"

# Prune old backups
find "$BACKUP_DIR" -name "dealix_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete
echo "✓ Pruned backups older than ${RETENTION_DAYS} days"

# Optional: sync to S3 if AWS creds set
if [[ -n "${AWS_S3_BUCKET:-}" ]]; then
  aws s3 cp "$OUT" "s3://${AWS_S3_BUCKET}/backups/$(basename "$OUT")" --quiet
  echo "✓ Synced to s3://${AWS_S3_BUCKET}"
fi
