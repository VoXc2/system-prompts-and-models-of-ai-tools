#!/bin/bash
# Dealix — Daily Revenue Cycle
# Run morning: generates targets, creates drafts
# Run afternoon: sends approved, checks follow-ups
#
# Usage:
#   Morning:   API_BASE=https://api.dealix.me ./scripts/daily_cycle.sh morning
#   Afternoon: API_BASE=https://api.dealix.me ./scripts/daily_cycle.sh afternoon

BASE="${API_BASE:-http://localhost:8000}"
ACTION="${1:-morning}"

case "$ACTION" in
  morning)
    echo "🌅 === MORNING CYCLE ==="
    echo ""
    echo "1. Generating 10 targets..."
    curl -s -X POST "$BASE/api/v1/automation/daily-pipeline/run" \
      -H "Content-Type: application/json" \
      -d '{"sectors":["real_estate","saas","agency","construction"],"daily_target_count":10}' | python3 -m json.tool 2>/dev/null || echo "  (endpoint returned non-JSON)"

    echo ""
    echo "2. Listing drafts for review..."
    curl -s "$BASE/api/v1/drafts?status=draft" | python3 -m json.tool 2>/dev/null || echo "  (no drafts or endpoint error)"

    echo ""
    echo "3. Draft stats..."
    curl -s "$BASE/api/v1/drafts/stats" | python3 -m json.tool 2>/dev/null || echo "  (stats unavailable)"

    echo ""
    echo "📋 Next: Review drafts above, then run:"
    echo "   curl -X POST '$BASE/api/v1/drafts/approve-batch' -H 'Content-Type: application/json' -d '{\"batch_id\":\"BATCH_ID\"}'"
    echo "   Then: ./scripts/daily_cycle.sh afternoon"
    ;;

  afternoon)
    echo "🌇 === AFTERNOON CYCLE ==="
    echo ""
    echo "1. Sending approved emails (batch of 5)..."
    curl -s -X POST "$BASE/api/v1/drafts/send-approved-batch?channel=email&batch_size=5" | python3 -m json.tool 2>/dev/null || echo "  (send result)"

    echo ""
    echo "2. Checking due follow-ups..."
    curl -s "$BASE/api/v1/followups/due" | python3 -m json.tool 2>/dev/null || echo "  (no follow-ups due)"

    echo ""
    echo "3. Generating follow-up drafts..."
    curl -s -X POST "$BASE/api/v1/followups/generate" | python3 -m json.tool 2>/dev/null || echo "  (follow-ups generated)"

    echo ""
    echo "4. Updated stats..."
    curl -s "$BASE/api/v1/drafts/stats" | python3 -m json.tool 2>/dev/null || echo "  (stats)"

    echo ""
    echo "✅ Afternoon cycle complete. Check replies tomorrow morning."
    ;;

  status)
    echo "📊 === STATUS CHECK ==="
    echo ""
    curl -s "$BASE/api/v1/drafts/stats" | python3 -m json.tool 2>/dev/null
    echo ""
    curl -s "$BASE/api/v1/os/whatsapp-providers" | python3 -m json.tool 2>/dev/null
    ;;

  *)
    echo "Usage: $0 {morning|afternoon|status}"
    echo "  morning   — generate targets + create drafts"
    echo "  afternoon — send approved + generate follow-ups"
    echo "  status    — check current stats"
    ;;
esac
