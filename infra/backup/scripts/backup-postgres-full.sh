#!/usr/bin/env bash
# Full logical backup (pg_dump custom format). Suitable for daily full backups for most SaaS DB sizes.
# For TB-scale or sub-minute RPO, use WAL archiving + pg_basebackup or managed RDS PITR (see BACKUP_AND_RECOVERY.md).

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh"

ENV_FILE="${BACKUP_ENV_FILE:-/etc/dealix/backup.env}"
load_env "${ENV_FILE}"

require_cmd pg_dump

TS="$(backup_timestamp)"
BACKUP_ROOT="${BACKUP_ROOT:-/var/lib/dealix-backups}"
OUT_DIR="${BACKUP_ROOT}/postgres/full/${TS}"
ensure_dir "${OUT_DIR}"

: "${PGDATABASE:?Set PGDATABASE}"
: "${PGUSER:?Set PGUSER}"

DUMP_FILE="${OUT_DIR}/dump-${PGDATABASE}-${TS}.dump"
log "Starting pg_dump custom format -> ${DUMP_FILE}"

# Custom format allows parallel restore and selective restore
pg_dump -h "${PGHOST:-localhost}" -p "${PGPORT:-5432}" -U "${PGUSER}" -d "${PGDATABASE}" \
  -Fc --verbose -f "${DUMP_FILE}.tmp"
mv "${DUMP_FILE}.tmp" "${DUMP_FILE}"

# Sidecar manifest for integrity monitoring
sha256sum "${DUMP_FILE}" > "${DUMP_FILE}.sha256"
SIZE_BYTES="$(stat -c%s "${DUMP_FILE}" 2>/dev/null || stat -f%z "${DUMP_FILE}")"
echo "{\"kind\":\"postgres_full\",\"timestamp\":\"${TS}\",\"bytes\":${SIZE_BYTES},\"path\":\"${DUMP_FILE}\"}" > "${OUT_DIR}/manifest.json"
log "Done postgres full backup: ${DUMP_FILE} (${SIZE_BYTES} bytes)"

echo "${OUT_DIR}"
