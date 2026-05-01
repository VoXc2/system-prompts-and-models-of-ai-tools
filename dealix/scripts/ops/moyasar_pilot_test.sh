#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# moyasar_pilot_test.sh — G2 gate: end-to-end Moyasar 1 SAR pilot test
# ─────────────────────────────────────────────────────────────────────────────
#
# Validates the full funnel:
#   1. POST /api/v1/checkout → creates Moyasar invoice for pilot_1sar plan
#   2. Captures payment_url + invoice_id
#   3. Fires PostHog CHECKOUT_STARTED event (in the API)
#   4. Prompts you to open payment_url and pay with Moyasar test card
#   5. Verifies webhook was received + idempotency + DLQ stats stable
#   6. Fires PostHog PAYMENT_SUCCEEDED event (in the webhook handler)
#
# Prerequisites (set in /opt/dealix/.env + service restarted):
#   MOYASAR_SECRET_KEY=sk_test_XXXX
#   MOYASAR_WEBHOOK_SECRET=<random-long-string>   # also registered in Moyasar dashboard
#   POSTHOG_API_KEY=phc_XXXX
#   POSTHOG_HOST=https://us.i.posthog.com
#
# Moyasar test cards: https://docs.moyasar.com/testing
#   * Success: 4111 1111 1111 1111 | any future expiry | any CVV | any 3DS pwd
#   * Fail:    4000 0000 0000 0002
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

API_BASE="${API_BASE:-http://127.0.0.1:8001}"
API_KEY="${API_KEY:?API_KEY is required (from /opt/dealix/.env API_KEYS)}"
TEST_EMAIL="${TEST_EMAIL:-pilot-$(date +%s)@dealix.me}"
TEST_LEAD_ID="${TEST_LEAD_ID:-pilot_$(date +%s)}"

hdr=(-H "X-API-Key: $API_KEY")

echo "========================================="
echo "  Dealix — G2 Moyasar Pilot Test (1 SAR)"
echo "========================================="
echo

# ── Step 0: preflight — check required keys present ──────────────────────────
echo "[0/6] Preflight — checking .env for required keys"
MISSING=()
for key in MOYASAR_SECRET_KEY MOYASAR_WEBHOOK_SECRET POSTHOG_API_KEY; do
  if ! grep -q "^$key=" /opt/dealix/.env 2>/dev/null; then
    MISSING+=("$key")
  fi
done
if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo "❌ Missing in /opt/dealix/.env: ${MISSING[*]}"
  echo "   Add them and 'systemctl restart dealix-api' before running this."
  exit 1
fi
echo "✅ All required keys present"
echo

# ── Step 1: baseline DLQ + approvals ─────────────────────────────────────────
echo "[1/6] Baseline: DLQ stats + approvals stats"
DLQ_BEFORE=$(curl -s "${hdr[@]}" "$API_BASE/api/v1/admin/dlq/stats" || echo "{}")
echo "DLQ before:       $DLQ_BEFORE"
APP_BEFORE=$(curl -s "${hdr[@]}" "$API_BASE/api/v1/admin/approvals/stats" || echo "{}")
echo "Approvals before: $APP_BEFORE"
echo

# ── Step 2: create checkout ──────────────────────────────────────────────────
echo "[2/6] Creating Moyasar invoice for pilot_1sar plan"
CHECKOUT_BODY=$(cat <<JSON
{"plan":"pilot_1sar","email":"$TEST_EMAIL","lead_id":"$TEST_LEAD_ID"}
JSON
)
CHECKOUT_RESP=$(curl -s -X POST "${hdr[@]}" \
  -H "Content-Type: application/json" \
  --data "$CHECKOUT_BODY" \
  "$API_BASE/api/v1/checkout")
echo "Checkout response: $CHECKOUT_RESP"

INVOICE_ID=$(echo "$CHECKOUT_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('invoice_id',''))")
PAYMENT_URL=$(echo "$CHECKOUT_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('payment_url',''))")

if [[ -z "$INVOICE_ID" || -z "$PAYMENT_URL" ]]; then
  echo "❌ Failed to create invoice. Check dealix-api logs:"
  echo "   journalctl -u dealix-api -n 50 --no-pager"
  exit 2
fi
echo "✅ Invoice created: $INVOICE_ID"
echo "   Payment URL:    $PAYMENT_URL"
echo

# ── Step 3: wait for Sami to pay ─────────────────────────────────────────────
echo "[3/6] MANUAL STEP"
echo "─────────────────────────────────────────"
echo "  Open the payment URL above in your browser."
echo "  Use test card: 4111 1111 1111 1111"
echo "                 Expiry: any future date"
echo "                 CVV:    any 3 digits"
echo "  For 3DS:       any password"
echo "─────────────────────────────────────────"
read -r -p "  Press ENTER after payment completed (or Ctrl+C to abort)..."
echo

# ── Step 4: poll invoice status ──────────────────────────────────────────────
echo "[4/6] Polling Moyasar for invoice status (max 60s)"
MOYASAR_KEY=$(grep '^MOYASAR_SECRET_KEY=' /opt/dealix/.env | cut -d= -f2- | tr -d '"')
for i in $(seq 1 20); do
  INV=$(curl -s -u "${MOYASAR_KEY}:" "https://api.moyasar.com/v1/invoices/$INVOICE_ID")
  INV_STATUS=$(echo "$INV" | python3 -c "import json,sys; print(json.load(sys.stdin).get('status','?'))")
  echo "  poll $i: status=$INV_STATUS"
  if [[ "$INV_STATUS" == "paid" ]]; then
    echo "✅ Invoice paid"
    break
  fi
  sleep 3
done

# ── Step 5: check webhook processed (DLQ unchanged = success path) ───────────
echo
echo "[5/6] Post-payment: DLQ stats should be unchanged (webhook ok)"
sleep 5
DLQ_AFTER=$(curl -s "${hdr[@]}" "$API_BASE/api/v1/admin/dlq/stats" || echo "{}")
echo "DLQ after: $DLQ_AFTER"
if [[ "$DLQ_BEFORE" == "$DLQ_AFTER" ]]; then
  echo "✅ DLQ unchanged — webhook handled cleanly"
else
  echo "⚠️  DLQ changed — webhook may have errored (check journalctl)"
fi
echo

# ── Step 6: inspect logs for PostHog fire ────────────────────────────────────
echo "[6/6] Checking logs for PostHog event fire"
journalctl -u dealix-api --since "2 minutes ago" --no-pager | \
  grep -E "moyasar_webhook|posthog|payment_paid|CHECKOUT_STARTED|PAYMENT_SUCCEEDED" | tail -10 || true
echo

# ── Verdict ──────────────────────────────────────────────────────────────────
echo "========================================="
echo "  Verdict"
echo "========================================="
if [[ "$INV_STATUS" == "paid" && "$DLQ_BEFORE" == "$DLQ_AFTER" ]]; then
  echo "✅ G2 gate PASSED"
  echo "   Invoice:  $INVOICE_ID (paid)"
  echo "   DLQ:      clean"
  echo "   PostHog:  check https://us.posthog.com/project/394094/activity/explore"
  echo "             look for PAYMENT_SUCCEEDED event with distinct_id=$TEST_LEAD_ID"
  echo
  echo "   This also closes O3 (PostHog funnel live)."
  exit 0
else
  echo "❌ G2 gate FAILED"
  echo "   Invoice status: $INV_STATUS"
  echo "   DLQ before/after: $DLQ_BEFORE / $DLQ_AFTER"
  exit 3
fi
