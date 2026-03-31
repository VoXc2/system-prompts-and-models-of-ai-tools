#!/usr/bin/env bash
# Dealix Backup Script
set -e

BACKUP_DIR="${BACKUP_DIR:-/root/dealix-backups}"
DB_NAME="${DB_NAME:-salesflow}"
DB_USER="${DB_USER:-salesflow}"
DB_HOST="${DB_HOST:-localhost}"
RETENTION_DAILY=7
RETENTION_WEEKLY=4
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DAY_OF_WEEK=$(date +%u)

mkdir -p "${BACKUP_DIR}/daily" "${BACKUP_DIR}/weekly"

echo "=========================================="
echo "  Dealix Backup - ${TIMESTAMP}"
echo "=========================================="

# Database backup
echo "📦 Backing up database..."
DB_FILE="${BACKUP_DIR}/daily/db_${TIMESTAMP}.sql.gz"
pg_dump -h "${DB_HOST}" -U "${DB_USER}" "${DB_NAME}" | gzip > "${DB_FILE}"
echo "  → ${DB_FILE} ($(du -h ${DB_FILE} | cut -f1))"

# Application files backup
echo "📦 Backing up application files..."
APP_FILE="${BACKUP_DIR}/daily/app_${TIMESTAMP}.tar.gz"
tar -czf "${APP_FILE}" --exclude='node_modules' --exclude='.next' --exclude='__pycache__' --exclude='.git' /root/dealix/ 2>/dev/null || true
echo "  → ${APP_FILE}"

# Weekly backup (on Sundays)
if [ "${DAY_OF_WEEK}" = "7" ]; then
  echo "📦 Creating weekly backup..."
  cp "${DB_FILE}" "${BACKUP_DIR}/weekly/db_weekly_${TIMESTAMP}.sql.gz"
  cp "${APP_FILE}" "${BACKUP_DIR}/weekly/app_weekly_${TIMESTAMP}.tar.gz"
fi

# Cleanup old daily backups
echo "🧹 Cleaning old backups..."
find "${BACKUP_DIR}/daily" -type f -mtime +${RETENTION_DAILY} -delete 2>/dev/null
find "${BACKUP_DIR}/weekly" -type f -mtime +$((RETENTION_WEEKLY * 7)) -delete 2>/dev/null

echo ""
echo "✅ Backup completed successfully"
echo "  Daily backups: $(ls ${BACKUP_DIR}/daily/ | wc -l) files"
echo "  Weekly backups: $(ls ${BACKUP_DIR}/weekly/ | wc -l) files"
