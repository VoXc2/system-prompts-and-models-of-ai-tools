#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# rollback_drill.sh — Dealix rollback drill (T7 gate)
# ─────────────────────────────────────────────────────────────────────────────
#
# Goal: prove we can roll back from current HEAD to .last_good_sha in <5 min.
#
# Modes:
#   --dry-run    (default)  Print every step, touch nothing. Safe in prod.
#   --real       Actually perform the rollback. Requires CONFIRM=YES env.
#
# Run on the prod server (or matching staging) as root:
#   sudo bash /opt/dealix/scripts/ops/rollback_drill.sh --dry-run
#
# Exit codes:
#   0 = success
#   1 = preflight failed
#   2 = rollback failed
#   3 = health check failed after rollback
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

MODE="${1:---dry-run}"
APP_DIR="${APP_DIR:-/opt/dealix}"
SERVICE="${SERVICE:-dealix-api}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8001/health/deep}"
LAST_GOOD_FILE="${APP_DIR}/.last_good_sha"
LOG_FILE="/var/log/dealix_rollback_drill.$(date +%Y%m%dT%H%M%SZ).log"

log() { echo "[$(date -u +%H:%M:%SZ)] $*" | tee -a "$LOG_FILE"; }
die() { log "FATAL: $*"; exit "${2:-1}"; }

# ── Preflight ────────────────────────────────────────────────────────────────
log "=== Rollback drill start (mode=$MODE) ==="

[[ -d "$APP_DIR/.git" ]] || die "Not a git checkout: $APP_DIR" 1
[[ -f "$LAST_GOOD_FILE" ]] || die "Missing $LAST_GOOD_FILE — cannot roll back" 1

CURRENT_SHA=$(cd "$APP_DIR" && git rev-parse --short HEAD)
TARGET_SHA=$(tr -d '[:space:]' < "$LAST_GOOD_FILE" | head -c 10)

log "Current HEAD:  $CURRENT_SHA"
log "Rollback to:   $TARGET_SHA"

if [[ "$CURRENT_SHA" == "$TARGET_SHA" ]]; then
  die "Already on .last_good_sha — nothing to roll back" 1
fi

# Check service is currently up
if systemctl is-active --quiet "$SERVICE"; then
  log "Service $SERVICE is active — proceeding"
else
  log "WARN: Service $SERVICE is NOT active before drill"
fi

# Check current health
PRE_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" || echo "000")
log "Pre-drill /health/deep: HTTP $PRE_HEALTH"

# ── Dry run: stop here ───────────────────────────────────────────────────────
if [[ "$MODE" == "--dry-run" ]]; then
  log ""
  log "=== DRY-RUN: would execute the following on --real ==="
  log "  1. systemctl stop $SERVICE"
  log "  2. (cd $APP_DIR && git fetch origin && git reset --hard $TARGET_SHA)"
  log "  3. (cd $APP_DIR && .venv/bin/pip install -q -r requirements.txt)"
  log "  4. systemctl start $SERVICE"
  log "  5. Wait 10s, then curl $HEALTH_URL"
  log "  6. If health != 200 → die 3 (you MUST then reset to $CURRENT_SHA manually)"
  log ""
  log "Target rollback time: <5 min (most of it is pip install)"
  log "=== Dry run complete. No state changed. ==="
  exit 0
fi

# ── Real rollback ────────────────────────────────────────────────────────────
if [[ "$MODE" == "--real" ]]; then
  if [[ "${CONFIRM:-}" != "YES" ]]; then
    die "Refusing to run --real without CONFIRM=YES in env" 1
  fi

  START_TS=$(date +%s)

  log "STEP 1/5: systemctl stop $SERVICE"
  systemctl stop "$SERVICE" || die "Failed to stop service" 2

  log "STEP 2/5: git reset --hard $TARGET_SHA"
  (cd "$APP_DIR" && git fetch origin && git reset --hard "$TARGET_SHA") \
    || die "git reset failed" 2

  log "STEP 3/5: pip install -r requirements.txt"
  (cd "$APP_DIR" && .venv/bin/pip install -q -r requirements.txt) \
    || die "pip install failed — service still stopped, manual recovery needed" 2

  log "STEP 4/5: systemctl start $SERVICE"
  systemctl start "$SERVICE" || die "Failed to start service after rollback" 2

  log "STEP 5/5: wait + health check"
  sleep 10
  POST_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" || echo "000")

  END_TS=$(date +%s)
  ELAPSED=$((END_TS - START_TS))

  log "Post-rollback /health/deep: HTTP $POST_HEALTH"
  log "Elapsed: ${ELAPSED}s"

  if [[ "$POST_HEALTH" != "200" ]]; then
    die "Health check failed after rollback — $POST_HEALTH" 3
  fi

  if (( ELAPSED > 300 )); then
    log "WARN: Rollback took ${ELAPSED}s (>5min target) — review pip cache"
  fi

  log "=== Rollback complete. HEAD is now $TARGET_SHA. ==="
  log "Remember to:"
  log "  * Update .last_good_sha if this rollback is now the stable version"
  log "  * Investigate the bad commit that triggered the rollback"
  log "  * File an incident post-mortem in docs/incidents/"
  exit 0
fi

die "Unknown mode: $MODE (expected --dry-run or --real)" 1
