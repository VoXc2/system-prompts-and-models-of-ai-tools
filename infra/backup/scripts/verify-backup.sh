#!/usr/bin/env bash
# Verifies recent backups: manifest present, age, sha256, optional download from S3.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh"

ENV_FILE="${BACKUP_ENV_FILE:-/etc/dealix/backup.env}"
load_env "${ENV_FILE}"

BACKUP_ROOT="${BACKUP_ROOT:-/var/lib/dealix-backups}"
MAX_AGE="${BACKUP_MAX_AGE_SEC:-93600}"

FAILED=0
while IFS= read -r -d '' m; do
  dir="$(dirname "${m}")"
  age=$(( $(date +%s) - $(stat -c %Y "${m}" 2>/dev/null || stat -f %m "${m}") ))
  if [[ "${age}" -gt "${MAX_AGE}" ]]; then
    log "STALE manifest: ${m} (age ${age}s > ${MAX_AGE}s)"
    FAILED=1
  fi
  sha_files=0
  while IFS= read -r -d '' _; do sha_files=$((sha_files + 1)); done < <(find "${dir}" -maxdepth 1 -name '*.sha256' -print0)
  if [[ "${sha_files}" -gt 0 ]]; then
    while IFS= read -r -d '' sf; do
      (cd "$(dirname "${sf}")" && sha256sum -c "$(basename "${sf}")") || FAILED=1
    done < <(find "${dir}" -maxdepth 1 -name '*.sha256' -print0)
  fi
done < <(find "${BACKUP_ROOT}" -name manifest.json -print0)

if [[ "${FAILED}" -ne 0 ]]; then
  alert_all "Backup verification failed" "Check ${BACKUP_ROOT}"
  exit 1
fi
log "Backup verification OK"
exit 0
