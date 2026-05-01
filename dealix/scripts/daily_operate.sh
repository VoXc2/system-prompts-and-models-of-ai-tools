#!/usr/bin/env bash
# daily_operate.sh — local trigger for Dealix daily revenue machine.
# Run: bash scripts/daily_operate.sh
#
# Default API: https://api.dealix.me
# Override: DEALIX_API=https://api.dealix.me bash scripts/daily_operate.sh

set -e

API="${DEALIX_API:-https://api.dealix.me}"
GMAIL_DRAFTS="${GMAIL_DRAFTS:-50}"
LINKEDIN_DRAFTS="${LINKEDIN_DRAFTS:-20}"
CALL_SCRIPTS="${CALL_SCRIPTS:-10}"
CREATE_IN_INBOX="${CREATE_IN_INBOX:-true}"

# 0. Auth check (search-diag should report tier1_ready)
echo "═══════════════════════════════════════════════════════════════"
echo "  🚀  DEALIX — Daily Operate Mode  ($(date -u +'%Y-%m-%d %H:%M UTC'))"
echo "═══════════════════════════════════════════════════════════════"

echo ""
echo "🔍 Tier readiness:"
curl -fsS "$API/api/v1/prospect/search-diag" 2>/dev/null \
  | jq '{tier1_ready, tier2_ready, hint, gmail_configured: .GMAIL_REFRESH_TOKEN.set, llm: (.GROQ_API_KEY.set or .ANTHROPIC_API_KEY.set)}' \
  || { echo "❌ API unreachable at $API"; exit 1; }

echo ""
echo "═══ 1. Run revenue machine ═══"
curl -fsS -X POST "$API/api/v1/automation/revenue-machine/run" \
  -H 'Content-Type: application/json' \
  -d "{
    \"daily_candidates\": 200,
    \"gmail_drafts\": $GMAIL_DRAFTS,
    \"linkedin_drafts\": $LINKEDIN_DRAFTS,
    \"call_scripts\": $CALL_SCRIPTS,
    \"partner_intros\": 10,
    \"approval_mode\": \"draft_only\",
    \"create_in_gmail_drafts_in_inbox\": $CREATE_IN_INBOX
  }" | jq '{
    candidates_pool: .candidates_pool,
    candidates_eligible: .candidates_eligible,
    excluded: .excluded,
    produced: .produced,
    gmail_drafts_in_inbox: .gmail_drafts_in_inbox
  }'

echo ""
echo "═══ 2. Schedule follow-ups for prior sends ═══"
curl -fsS -X POST "$API/api/v1/automation/followups/run" -d '{}' | jq

echo ""
echo "═══ 3. Today's dashboard ═══"
curl -fsS "$API/api/v1/dashboard/revenue-machine/today" | jq

echo ""
echo "═══ 4. Generate daily report ═══"
curl -fsS -X POST "$API/api/v1/automation/daily-report/generate" \
  | jq '{report_path: .report_path, metrics: .metrics}'

echo ""
echo "═══ 5. Export drafts as CSV (for Excel review) ═══"
curl -fsS "$API/api/v1/automation/revenue-machine/export?format=csv" \
  | jq '{gmail_export, linkedin_export, gmail_count, linkedin_count}'

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅  Daily run complete."
echo "  Open Gmail Drafts folder → review + send manually"
echo "  Open dashboard.html → Local Lead Engine demo + status"
echo "  Check docs/ops/daily_reports/ for today's MD report + CSVs"
echo "═══════════════════════════════════════════════════════════════"
