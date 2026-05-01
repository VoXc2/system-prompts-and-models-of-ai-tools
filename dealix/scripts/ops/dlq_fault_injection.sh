#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# dlq_fault_injection.sh — prove DLQ catches a failed webhook (T5 final)
# ─────────────────────────────────────────────────────────────────────────────
#
# Sends an intentionally malformed Moyasar webhook (bad signature). Expectation:
#   * API responds 401 (signature verify fail) OR 400 (malformed body)
#   * WEBHOOKS_DLQ depth increments from N to N+1
#   * Event is inspectable via /admin/dlq/webhooks/peek
#   * Can be drained via /admin/dlq/webhooks/drain (test-only)
#
# Run on server (or from any machine with network access to the API):
#   API_KEY=<key> API_BASE=http://127.0.0.1:8001 \
#     bash /opt/dealix/scripts/ops/dlq_fault_injection.sh
#
# DoD for T5 full closure: depth goes up, peek returns the injected event.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

API_BASE="${API_BASE:-http://127.0.0.1:8001}"
API_KEY="${API_KEY:?API_KEY is required}"
QUEUE="${QUEUE:-webhooks}"

hdr=(-H "X-API-Key: $API_KEY")

echo "=== DLQ fault-injection drill ==="
echo "API:   $API_BASE"
echo "Queue: $QUEUE"
echo

# ── Step 1: baseline ─────────────────────────────────────────────────────────
echo "[1/4] Baseline DLQ stats:"
BEFORE=$(curl -s "${hdr[@]}" "$API_BASE/api/v1/admin/dlq/stats")
echo "$BEFORE"
BEFORE_DEPTH=$(echo "$BEFORE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('$QUEUE', d.get('queues',{}).get('$QUEUE',0)))")
echo "Baseline $QUEUE depth: $BEFORE_DEPTH"
echo

# ── Step 2: inject bad webhook ───────────────────────────────────────────────
echo "[2/4] Injecting malformed webhook (bad signature):"
INJECT_PAYLOAD='{"id":"drill-test-'$(date +%s)'","type":"payment_paid","data":{"amount":100,"currency":"SAR"}}'
INJECT_RESP=$(curl -s -o /tmp/inject_body.txt -w "HTTP %{http_code}" \
  -X POST "$API_BASE/api/v1/webhooks/moyasar" \
  -H "Content-Type: application/json" \
  -H "X-Moyasar-Signature: invalid-signature-$(date +%s)" \
  --data "$INJECT_PAYLOAD")
echo "Response: $INJECT_RESP"
echo "Body: $(cat /tmp/inject_body.txt | head -c 200)"
echo

# Expected: 401 (bad sig) or 400 (reject). NOT 200.
if echo "$INJECT_RESP" | grep -q "HTTP 200"; then
  echo "⚠️  WARN: Got 200 — signature verification may be disabled in this env"
fi

# ── Step 3: check DLQ increment ──────────────────────────────────────────────
sleep 2
echo "[3/4] Post-injection DLQ stats:"
AFTER=$(curl -s "${hdr[@]}" "$API_BASE/api/v1/admin/dlq/stats")
echo "$AFTER"
AFTER_DEPTH=$(echo "$AFTER" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('$QUEUE', d.get('queues',{}).get('$QUEUE',0)))")
echo "After $QUEUE depth: $AFTER_DEPTH"
echo

# ── Step 4: peek the failed event ────────────────────────────────────────────
echo "[4/4] Peek DLQ contents:"
curl -s "${hdr[@]}" "$API_BASE/api/v1/admin/dlq/$QUEUE/peek" | python3 -m json.tool || true
echo

# ── Verdict ──────────────────────────────────────────────────────────────────
if (( AFTER_DEPTH > BEFORE_DEPTH )); then
  echo "✅ T5 fault-injection PASSED"
  echo "   Depth increased: $BEFORE_DEPTH → $AFTER_DEPTH"
  echo "   DLQ caught the failed webhook as expected."
  echo
  echo "Next (optional): drain the drill entry:"
  echo "   curl -X POST -H 'X-API-Key: \$API_KEY' $API_BASE/api/v1/admin/dlq/$QUEUE/drain"
else
  echo "❌ T5 fault-injection FAILED"
  echo "   Depth did not change ($BEFORE_DEPTH → $AFTER_DEPTH)"
  echo "   Either: webhook was silently accepted, or DLQ is not wired."
  exit 1
fi
