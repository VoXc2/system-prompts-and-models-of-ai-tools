#!/usr/bin/env bash
# Rotating log snapshot (last N days). Large fleets should ship logs to Loki/CloudWatch instead of tarballing raw files.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh"

ENV_FILE="${BACKUP_ENV_FILE:-/etc/dealix/backup.env}"
load_env "${ENV_FILE}"

require_cmd tar

TS="$(backup_timestamp)"
BACKUP_ROOT="${BACKUP_ROOT:-/var/lib/dealix-backups}"
LOGS_DIR="${LOGS_DIR:-/var/log/dealix}"
OUT_DIR="${BACKUP_ROOT}/logs/${TS}"
ensure_dir "${OUT_DIR}"

ARCHIVE="${OUT_DIR}/logs-${TS}.tar.gz"
log "Archiving logs from ${LOGS_DIR}"

if [[ ! -d "${LOGS_DIR}" ]]; then
  log "WARN: LOGS_DIR missing, writing empty manifest"
  echo "{\"kind\":\"logs\",\"timestamp\":\"${TS}\",\"bytes\":0,\"skipped\":true}" > "${OUT_DIR}/manifest.json"
  echo "${OUT_DIR}"
  exit 0
fi

tar -czf "${ARCHIVE}" -C "$(dirname "${LOGS_DIR}")" "$(basename "${LOGS_DIR}")" 2>/dev/null || true
if [[ -f "${ARCHIVE}" ]]; then
  sha256sum "${ARCHIVE}" > "${ARCHIVE}.sha256"
  SIZE_BYTES="$(stat -c%s "${ARCHIVE}" 2>/dev/null || stat -f%z "${ARCHIVE}")"
else
  SIZE_BYTES=0
fi
echo "{\"kind\":\"logs\",\"timestamp\":\"${TS}\",\"bytes\":${SIZE_BYTES},\"path\":\"${ARCHIVE}\"}" > "${OUT_DIR}/manifest.json"
log "Done logs backup"
echo "${OUT_DIR}"
