#!/usr/bin/env bash
# Dealix grand launch: backend pytest, frontend lint + build, optional HTTP checks.
# Usage:
#   ./scripts/grand_launch_verify.sh
#   DEALIX_BASE_URL=http://127.0.0.1:8000 ./scripts/grand_launch_verify.sh --http
#   ./scripts/grand_launch_verify.sh --http --soft-ready
#   ./scripts/grand_launch_verify.sh --http-only --soft-ready   # API only, no pytest/lint/build

set -euo pipefail

# ── Path Resolution ───────────────────────────────
. "$(cd "$(dirname "$0")/lib" && pwd)/resolve-paths.sh"
ROOT="$PROJECT_ROOT"
BACKEND="$BACKEND_DIR"
FRONTEND="$FRONTEND_DIR"

HTTP=0
SOFT_READY=0
HTTP_ONLY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --http) HTTP=1; shift ;;
    --soft-ready) SOFT_READY=1; shift ;;
    --http-only) HTTP_ONLY=1; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ "$HTTP_ONLY" -eq 1 ]]; then
  require_component backend || { echo "FAIL: backend required for --http-only" >&2; exit 1; }
  echo "Dealix root: $ROOT"
  echo "== HTTP only =="
  PY_ARGS=(scripts/full_stack_launch_test.py --http-only)
  [[ "$SOFT_READY" -eq 1 ]] && PY_ARGS+=(--soft-ready)
  (cd "$BACKEND" && python "${PY_ARGS[@]}")
  echo "HTTP-only verify OK."
  exit 0
fi

echo "Dealix root: $ROOT"

if require_component backend; then
  echo "== Backend: pytest =="
  (cd "$BACKEND" && python -m pytest tests -q --tb=line)
else
  echo "== Backend: SKIPPED (not found) =="
fi

echo "== Sync marketing -> frontend/public =="
(cd "$ROOT" && node scripts/sync-marketing-to-public.cjs) || echo "[WARN] marketing sync skipped or failed"

if require_component frontend; then
  echo "== Frontend: lint =="
  (cd "$FRONTEND" && npm run lint)

  echo "== Frontend: build =="
  (cd "$FRONTEND" && npm run build)
else
  echo "== Frontend: SKIPPED (not found) =="
fi

if [[ "$HTTP" -eq 1 ]]; then
  require_component backend || { echo "FAIL: backend required for --http" >&2; exit 1; }
  echo "== HTTP: full_stack_launch_test =="
  PY_ARGS=(scripts/full_stack_launch_test.py)
  [[ "$SOFT_READY" -eq 1 ]] && PY_ARGS+=(--soft-ready)
  (cd "$BACKEND" && python "${PY_ARGS[@]}")
else
  echo "Skip HTTP (start API and run: ./scripts/grand_launch_verify.sh --http)" >&2
fi

echo "Grand launch verify OK."
