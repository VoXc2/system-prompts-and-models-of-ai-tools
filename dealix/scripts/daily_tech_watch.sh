#!/usr/bin/env bash
# Dealix Daily Tech Watch — runs tech_detect on target domains and flags changes.
# CRON-ready. Example: 0 9 * * * bash /path/to/daily_tech_watch.sh
#
# Usage:
#   bash scripts/daily_tech_watch.sh <path-to-domains.txt> [--api-base URL]
#   Or: DEALIX_DOMAINS_FILE=domains.txt bash scripts/daily_tech_watch.sh

set -euo pipefail

API_BASE="${DEALIX_API_BASE:-https://web-dealix.up.railway.app}"
DOMAINS_FILE="${1:-${DEALIX_DOMAINS_FILE:-docs/ops/lead_machine/TODAY_20_TARGETS.csv}}"
OUT_DIR="docs/ops/lead_machine/tech_watch"
mkdir -p "$OUT_DIR"
TODAY=$(date +%Y-%m-%d)
OUT="$OUT_DIR/$TODAY.json"

# Extract domains (column named 'website' or 'domain')
DOMAINS=$(python3 - <<PY
import csv, sys
fn = sys.argv[1] if len(sys.argv) > 1 else ""
try:
    with open(fn) as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit(0)
    col = next((c for c in rows[0].keys() if c.lower() in ("website","domain")), None)
    if not col:
        sys.exit(0)
    for r in rows:
        v = (r.get(col) or "").strip().replace("https://","").replace("http://","").strip("/")
        if v and "." in v and v != "unknown":
            print(v)
except Exception as e:
    print(f"error:{e}", file=sys.stderr)
PY
"$DOMAINS_FILE" | head -20 | tr '\n' ',' | sed 's/,$//')

if [[ -z "$DOMAINS" ]]; then
  echo "No domains found in $DOMAINS_FILE"
  exit 1
fi

# Build JSON array
JSON_ARR="["$(echo "$DOMAINS" | tr ',' '\n' | sed 's/.*/"&"/' | tr '\n' ',' | sed 's/,$//')"]"
BODY="{\"domains\":$JSON_ARR,\"concurrency\":5}"

echo "→ scanning $(echo "$DOMAINS" | tr ',' '\n' | wc -l) domains at $TODAY"
curl -sS -X POST "$API_BASE/api/v1/prospect/bulk-enrich" \
  -H "Content-Type: application/json" -d "$BODY" \
  --max-time 60 > "$OUT"

# Compare with yesterday if exists
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null || echo "")
PREV="$OUT_DIR/$YESTERDAY.json"
if [[ -f "$PREV" ]]; then
  python3 - <<PY
import json
today = json.load(open("$OUT"))["results"]
yest  = json.load(open("$PREV"))["results"]
added = []
removed = []
for d, t in today.items():
    today_tools = {x["name"] for x in t.get("tools", [])}
    yest_tools  = {x["name"] for x in yest.get(d, {}).get("tools", [])}
    new = today_tools - yest_tools
    gone = yest_tools - today_tools
    if new:
        added.append(f"  + {d}: {', '.join(sorted(new))}")
    if gone:
        removed.append(f"  - {d}: {', '.join(sorted(gone))}")
if added or removed:
    print("━━━ TECH STACK CHANGES ━━━")
    for l in added: print(l)
    for l in removed: print(l)
    print("\nTrigger outreach — these companies just added/removed tools.")
else:
    print("No stack changes detected today.")
PY
else
  echo "Baseline saved. Run again tomorrow to see changes."
fi

echo "→ saved: $OUT"
