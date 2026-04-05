#!/usr/bin/env bash
# Tarball of uploads volume (adjust UPLOADS_DIR to match app.config UPLOAD_DIR / docker volume).

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh"

ENV_FILE="${BACKUP_ENV_FILE:-/etc/dealix/backup.env}"
load_env "${ENV_FILE}"

require_cmd tar

TS="$(backup_timestamp)"
BACKUP_ROOT="${BACKUP_ROOT:-/var/lib/dealix-backups}"
UPLOADS_DIR="${UPLOADS_DIR:?Set UPLOADS_DIR}"
OUT_DIR="${BACKUP_ROOT}/uploads/${TS}"
ensure_dir "${OUT_DIR}"

ARCHIVE="${OUT_DIR}/uploads-${TS}.tar.zst"
log "Archiving ${UPLOADS_DIR} -> ${ARCHIVE}"

if [[ ! -d "${UPLOADS_DIR}" ]]; then
  log "WARN: UPLOADS_DIR missing, skipping"
  echo "{}"
  exit 0
fi

if command -v zstd >/dev/null 2>&1; then
  tar --posix -C "$(dirname "${UPLOADS_DIR}")" -cf - "$(basename "${UPLOADS_DIR}")" | zstd -19 -o "${ARCHIVE}.tmp"
  mv "${ARCHIVE}.tmp" "${ARCHIVE}"
else
  ARCHIVE="${OUT_DIR}/uploads-${TS}.tar.gz"
  tar -czf "${ARCHIVE}" -C "$(dirname "${UPLOADS_DIR}")" "$(basename "${UPLOADS_DIR}")"
fi

sha256sum "${ARCHIVE}" > "${ARCHIVE}.sha256"
SIZE_BYTES="$(stat -c%s "${ARCHIVE}" 2>/dev/null || stat -f%z "${ARCHIVE}")"
echo "{\"kind\":\"uploads\",\"timestamp\":\"${TS}\",\"bytes\":${SIZE_BYTES},\"path\":\"${ARCHIVE}\"}" > "${OUT_DIR}/manifest.json"
log "Done uploads backup: ${ARCHIVE}"
echo "${OUT_DIR}"
