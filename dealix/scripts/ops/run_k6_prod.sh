#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run_k6_prod.sh — execute the k6 smoke load test against prod (T6 gate)
# ─────────────────────────────────────────────────────────────────────────────
#
# Reads API_BASE + API_KEY from /opt/dealix/.env on the prod server, then
# runs tests/load/k6_smoke.js with those values.
#
# Prerequisites (on the server):
#   apt-get install -y gnupg ca-certificates
#   gpg -k
#   gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
#   echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | tee /etc/apt/sources.list.d/k6.list
#   apt-get update && apt-get install -y k6
#
# Run on server:
#   bash /opt/dealix/scripts/ops/run_k6_prod.sh
#
# DoD for T6: http_req_failed <2%, p95 <2s, 100 VU peak sustained 1 min
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

ENV_FILE="${ENV_FILE:-/opt/dealix/.env}"
K6_SCRIPT="${K6_SCRIPT:-/opt/dealix/tests/load/k6_smoke.js}"
OUT_DIR="${OUT_DIR:-/var/log/dealix_k6}"
TS=$(date -u +%Y%m%dT%H%M%SZ)

mkdir -p "$OUT_DIR"

[[ -f "$ENV_FILE" ]] || { echo "FATAL: $ENV_FILE not found"; exit 1; }
[[ -f "$K6_SCRIPT" ]] || { echo "FATAL: $K6_SCRIPT not found"; exit 1; }

# Pull values from .env
API_BASE=$(grep -E '^API_BASE=' "$ENV_FILE" | tail -1 | cut -d= -f2- | tr -d '"' || true)
API_KEY=$(grep -E '^API_KEYS=' "$ENV_FILE" | tail -1 | cut -d= -f2- | tr -d '"' | cut -d, -f1 || true)

# Fallback: use localhost + any valid key from API_KEYS
: "${API_BASE:=http://127.0.0.1:8001}"

if [[ -z "$API_KEY" ]]; then
  echo "FATAL: could not extract API_KEY from $ENV_FILE"
  exit 1
fi

echo "=== k6 run started $TS ==="
echo "API_BASE: $API_BASE"
echo "API_KEY:  ${API_KEY:0:4}...${API_KEY: -4} (redacted)"
echo "Output:   $OUT_DIR/k6_${TS}.json"
echo

API_BASE="$API_BASE" API_KEY="$API_KEY" \
  k6 run \
    --summary-export="$OUT_DIR/k6_${TS}_summary.json" \
    --out json="$OUT_DIR/k6_${TS}.json" \
    "$K6_SCRIPT" \
    | tee "$OUT_DIR/k6_${TS}.log"

EXIT_CODE=${PIPESTATUS[0]}

echo
echo "=== k6 run finished (exit=$EXIT_CODE) ==="
echo "Summary: $OUT_DIR/k6_${TS}_summary.json"
echo "Log:     $OUT_DIR/k6_${TS}.log"

if [[ $EXIT_CODE -eq 0 ]]; then
  echo "✅ T6 gate PASSED — thresholds met"
else
  echo "❌ T6 gate FAILED — thresholds breached; inspect log"
fi

exit "$EXIT_CODE"
