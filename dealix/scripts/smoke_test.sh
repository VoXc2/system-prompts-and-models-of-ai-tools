#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Dealix Railway Smoke Test
# بعد ما تضيف Variables + Redeploy في Railway، شغّل:
#   bash dealix_smoke_test.sh <your-railway-domain>
# مثال:
#   bash dealix_smoke_test.sh dealix-production-abcd.up.railway.app
# أو بعد ربط dealix.me:
#   bash dealix_smoke_test.sh dealix.me
# ═══════════════════════════════════════════════════════════════

set -u
DOMAIN="${1:-dealix.me}"
BASE="https://$DOMAIN"
PASS=0
FAIL=0

test_endpoint() {
  local name="$1"
  local path="$2"
  local expected="$3"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$BASE$path")
  if [ "$code" = "$expected" ]; then
    echo "  ✅ $name ($path) → $code"
    PASS=$((PASS+1))
  else
    echo "  ❌ $name ($path) → $code (expected $expected)"
    FAIL=$((FAIL+1))
  fi
}

echo ""
echo "═══ اختبار Dealix على $DOMAIN ═══"
echo ""
echo "[1] Core endpoints"
test_endpoint "Health"          "/health"              "200"
test_endpoint "Health deep"     "/health/deep"         "200"
test_endpoint "Root"            "/"                    "200"
test_endpoint "OpenAPI docs"    "/docs"                "200"

echo ""
echo "[2] API routes (موجودة على root مو /api/v1)"
test_endpoint "Pricing plans"   "/pricing/plans"       "200"

echo ""
echo "[3] Moyasar webhook endpoint (يقبل POST)"
WEBHOOK_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
  -X POST "$BASE/webhooks/moyasar" \
  -H "Content-Type: application/json" \
  -d '{"type":"payment_paid","data":{"id":"test"}}')
if [ "$WEBHOOK_CODE" = "200" ] || [ "$WEBHOOK_CODE" = "401" ] || [ "$WEBHOOK_CODE" = "400" ]; then
  echo "  ✅ Webhook موجود → $WEBHOOK_CODE (endpoint يرد)"
  PASS=$((PASS+1))
else
  echo "  ❌ Webhook → $WEBHOOK_CODE"
  FAIL=$((FAIL+1))
fi

echo ""
echo "[4] محتوى /health"
HEALTH=$(curl -s --max-time 10 "$BASE/health")
echo "  $HEALTH"

echo ""
echo "═══ النتيجة ═══"
echo "  ✅ نجح: $PASS"
echo "  ❌ فشل: $FAIL"
echo ""
if [ $FAIL -eq 0 ]; then
  echo "🎉 كل شي جاهز — Railway deployment يشتغل!"
  exit 0
else
  echo "⚠️  فيه مشاكل. شف Railway Deploy Logs لتفاصيل."
  exit 1
fi
