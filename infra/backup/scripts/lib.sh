#!/usr/bin/env bash
# shellcheck disable=SC2034
# Shared helpers for Dealix backup scripts (bash 4+).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_BACKUP_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

log() { echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] $*"; }
die() { log "ERROR: $*"; exit 1; }

load_env() {
  local f="${1:-}"
  if [[ -n "${f}" && -f "${f}" ]]; then
    # shellcheck source=/dev/null
    set -a && source "${f}" && set +a
    log "Loaded env from ${f}"
  fi
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Missing required command: $1"
}

slack_notify() {
  local text="$1"
  if [[ -n "${SLACK_BACKUP_WEBHOOK_URL:-}" ]] && command -v python3 >/dev/null 2>&1; then
    local payload
    payload="$(python3 -c 'import json,sys; print(json.dumps({"text": sys.argv[1]}))' "${text}")" || return 0
    curl -sS -X POST -H 'Content-type: application/json' -d "${payload}" \
      "${SLACK_BACKUP_WEBHOOK_URL}" >/dev/null || true
  fi
}

email_notify() {
  local subject="$1" body="$2"
  if [[ -n "${ALERT_EMAIL_TO:-}" ]] && command -v mail >/dev/null 2>&1; then
    echo "${body}" | mail -s "${subject}" "${ALERT_EMAIL_TO}" || true
  fi
}

alert_all() {
  local subject="$1" body="$2"
  log "ALERT: ${subject}"
  slack_notify "*${subject}*\n${body}"
  email_notify "${subject}" "${body}"
}

backup_timestamp() { date -u +"%Y%m%dT%H%M%SZ"; }

ensure_dir() {
  mkdir -p "$1"
}
