#!/usr/bin/env bash
# Packages dealix-marketing-bundle.zip: sales_assets + presentations/dealix-2026-sectors
# Run from repo root or salesflow-saas:
#   bash salesflow-saas/scripts/package_dealix_marketing_assets.sh
#   bash scripts/package_dealix_marketing_assets.sh
set -euo pipefail

# ── Path Resolution ───────────────────────────────
. "$(cd "$(dirname "$0")/lib" && pwd)/resolve-paths.sh"

require_component sales_assets || { echo "FAIL: sales_assets directory not found." >&2; exit 1; }

STAGING="$(mktemp -d)"
OUT="${SALES_ASSETS_DIR}/dealix-marketing-bundle.zip"
cleanup() { rm -rf "$STAGING"; }
trap cleanup EXIT

cp -a "$SALES_ASSETS_DIR" "$STAGING/sales_assets"
rm -f "$STAGING/sales_assets/dealix-marketing-bundle.zip"

PRES_DIR="${PROJECT_ROOT}/presentations/dealix-2026-sectors"
if [[ -d "$PRES_DIR" ]]; then
  cp -a "$PRES_DIR" "$STAGING/presentations-dealix-2026-sectors"
fi

rm -f "$OUT"
( cd "$STAGING" && zip -r -q "$OUT" . )
echo "OK: $OUT"
ls -la "$OUT"
