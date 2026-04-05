#!/usr/bin/env bash
# Orchestrates daily backup: postgres, uploads, logs, encrypted config, then full tree sync to S3 + GCS.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh"

ENV_FILE="${BACKUP_ENV_FILE:-/etc/dealix/backup.env}"
load_env "${ENV_FILE}"

BACKUP_ROOT="${BACKUP_ROOT:-/var/lib/dealix-backups}"
FAILED=0

step() {
  local title="$1"
  shift
  log "=== ${title} ==="
  if "$@"; then
    log "OK: ${title}"
  else
    FAILED=1
    alert_all "Backup step failed: ${title}" "Command: $*"
  fi
}

step "postgres_full" "${SCRIPT_DIR}/backup-postgres-full.sh" || true
step "uploads" "${SCRIPT_DIR}/backup-uploads.sh" || true
step "logs" "${SCRIPT_DIR}/backup-logs.sh" || true
step "config_encrypted" "${SCRIPT_DIR}/backup-env-encrypted.sh" || true

if [[ "${FAILED}" -eq 0 ]]; then
  log "=== sync_object_stores ==="
  TS_TAG="$(date -u +"%Y%m%dT%H%M%SZ")"
  STAGING="${BACKUP_ROOT}/.sync-staging-${TS_TAG}"
  ensure_dir "${STAGING}"
  # Point-in-time snapshot path for sync (copy manifests + last hour)
  find "${BACKUP_ROOT}" -type f \( -name "*.dump" -o -name "*.tar.gz" -o -name "*.tar.zst" -o -name "*.gpg" -o -name "manifest.json" -o -name "*.sha256" \) -mmin -180 -print0 | while IFS= read -r -d '' f; do
    rel="${f#${BACKUP_ROOT}/}"
    mkdir -p "${STAGING}/$(dirname "${rel}")"
    cp -a "${f}" "${STAGING}/${rel}"
  done || true

  if [[ -d "${STAGING}" ]] && [[ -n "$(ls -A "${STAGING}" 2>/dev/null)" ]]; then
    if [[ -n "${S3_BACKUP_BUCKET:-}" ]]; then
      require_cmd aws
      aws s3 sync "${STAGING}" "s3://${S3_BACKUP_BUCKET}/${S3_PREFIX:-production}/sync-${TS_TAG}/" --region "${AWS_REGION:-eu-central-1}" --only-show-errors
    fi
    if [[ -n "${GCS_BACKUP_BUCKET:-}" ]]; then
      require_cmd gsutil
      gsutil -m rsync -r "${STAGING}" "${GCS_BACKUP_BUCKET%/}/${S3_PREFIX:-production}/sync-${TS_TAG}/"
    fi
  fi
  rm -rf "${STAGING}"
else
  log "Skipping cloud sync due to earlier failures"
fi

if [[ "${FAILED}" -ne 0 ]]; then
  exit 1
fi

slack_notify ":white_check_mark: Dealix daily backup OK ($(hostname))"
log "Daily backup finished successfully"
