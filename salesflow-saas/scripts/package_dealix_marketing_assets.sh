#!/usr/bin/env bash
# From repo root: bash salesflow-saas/scripts/package_dealix_marketing_assets.sh
# Layout matches frontend/public: dealix-marketing/ + dealix-presentations/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SAA="$ROOT/salesflow-saas"
STAGING="$(mktemp -d)"
OUT="$SAA/sales_assets/dealix-marketing-bundle.zip"
cleanup() { rm -rf "$STAGING"; }
trap cleanup EXIT
cp -a "$SAA/sales_assets" "$STAGING/dealix-marketing"
rm -f "$STAGING/dealix-marketing/dealix-marketing-bundle.zip"
if [[ -d "$SAA/presentations/dealix-2026-sectors" ]]; then
  cp -a "$SAA/presentations/dealix-2026-sectors" "$STAGING/dealix-presentations"
else
  echo "WARN: missing $SAA/presentations/dealix-2026-sectors" >&2
fi
cat >"$STAGING/README-AR.txt" <<'EOF'
بعد فك الضغط:
- افتح dealix-marketing/index.html في المتصفح (يعمل محلياً بدون خادم إذا بقي dealix-presentations بجانب dealix-marketing).
- لا تنقل مجلداً واحداً فقط؛ الروابط بين المجلدين نسبية.
- عبر Next.js: npm run dev ثم http://localhost:3000/dealix-marketing/
EOF
rm -f "$OUT"
( cd "$STAGING" && zip -r -q "$OUT" . )
echo "OK: $OUT"
ls -la "$OUT"
