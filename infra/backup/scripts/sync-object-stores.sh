#!/usr/bin/env bash
# Upload latest backup tree to S3 (primary) and mirror to GCS (secondary).
# Requires: aws CLI (v2), google-cloud-sdk (gsutil), authenticated via IAM / workload identity.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "${SCRIPT_DIR}/lib.sh"

ENV_FILE="${BACKUP_ENV_FILE:-/etc/dealix/backup.env}"
load_env "${ENV_FILE}"

TS="${1:?Usage: sync-object-stores.sh <backup-day-dir>}"
[[ -d "${TS}" ]] || die "Not a directory: ${TS}"

: "${S3_BACKUP_BUCKET:?Set S3_BACKUP_BUCKET}"
: "${AWS_REGION:?Set AWS_REGION}"

PREFIX="${S3_PREFIX:-production/}"
REMOTE_S3="s3://${S3_BACKUP_BUCKET}/${PREFIX}$(basename "$(dirname "${TS}")")/$(basename "${TS}")/"

log "aws s3 sync ${TS} ${REMOTE_S3}"
require_cmd aws
aws s3 sync "${TS}" "${REMOTE_S3}" --region "${AWS_REGION}" --only-show-errors

if [[ -n "${GCS_BACKUP_BUCKET:-}" ]]; then
  require_cmd gsutil
  REMOTE_GCS="${GCS_BACKUP_BUCKET%/}/${PREFIX}$(basename "$(dirname "${TS}")")/$(basename "${TS}")/"
  log "gsutil -m rsync -r ${TS} ${REMOTE_GCS}"
  gsutil -m rsync -r "${TS}" "${REMOTE_GCS}"
fi

log "Object store sync complete"
