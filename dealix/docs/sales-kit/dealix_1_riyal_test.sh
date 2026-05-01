#!/usr/bin/env bash
# Dealix — 1 Riyal End-to-End Test
# يختبر كامل دورة الدفع: health → pricing → demo request → checkout
#
# الاستخدام:
#   bash dealix_1_riyal_test.sh
#   bash dealix_1_riyal_test.sh https://your-railway-url.up.railway.app
#
# بعد النجاح: افتح payment_url في المتصفح وادفع 1 ريال

set -euo pipefail

# ── Config ──
BASE_URL="${1:-https://dealix-production-up.railway.app}"
TEST_EMAIL="${TEST_EMAIL:-sami.assiri11@gmail.com}"
TEST_PHONE="${TEST_PHONE:-+966500000000}"

# ── Colors ──
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

fail() { echo -e "${RED}❌ $1${NC}"; exit 1; }
pass() { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }

echo ""
echo "════════════════════════════════════════════════════════"
echo "  Dealix — End-to-End Payment Test"
echo "  Base URL: $BASE_URL"
echo "════════════════════════════════════════════════════════"
echo ""

# ── Test 1: Health ──
info "1/5 فحص /health"
HEALTH=$(curl -s -w "\n%{http_code}" "$BASE_URL/health" || echo -e "\n000")
HEALTH_BODY=$(echo "$HEALTH" | sed '$d')
HEALTH_CODE=$(echo "$HEALTH" | tail -n1)

if [ "$HEALTH_CODE" = "200" ]; then
  pass "/health → 200"
  echo "   Response: $HEALTH_BODY" | head -c 200; echo ""
else
  fail "/health → $HEALTH_CODE (expected 200). Railway not deployed — راجع RAILWAY_MOYASAR_STEP_BY_STEP.md"
fi
echo ""

# ── Test 2: Public Health ──
info "2/5 فحص /api/v1/public/health"
PH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/public/health")
if [ "$PH_CODE" = "200" ]; then
  pass "/api/v1/public/health → 200"
else
  warn "/api/v1/public/health → $PH_CODE (قد تكون النسخة قديمة — redeploy بعد PR #70)"
fi
echo ""

# ── Test 3: Pricing ──
info "3/5 فحص /api/v1/pricing/plans"
PRICING=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/pricing/plans")
PRICING_BODY=$(echo "$PRICING" | sed '$d')
PRICING_CODE=$(echo "$PRICING" | tail -n1)

if [ "$PRICING_CODE" = "200" ]; then
  pass "/api/v1/pricing/plans → 200"
  echo "   Response: $PRICING_BODY" | head -c 400; echo ""
else
  fail "/api/v1/pricing/plans → $PRICING_CODE"
fi
echo ""

# ── Test 4: Demo Request ──
info "4/5 اختبار POST /api/v1/public/demo-request"
DEMO=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/public/demo-request" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"سامي تجربة\",
    \"company\": \"Dealix Test\",
    \"email\": \"$TEST_EMAIL\",
    \"phone\": \"$TEST_PHONE\",
    \"sector\": \"saas\",
    \"consent\": true
  }")
DEMO_BODY=$(echo "$DEMO" | sed '$d')
DEMO_CODE=$(echo "$DEMO" | tail -n1)

if [ "$DEMO_CODE" = "200" ]; then
  pass "/api/v1/public/demo-request → 200"
  CALENDLY=$(echo "$DEMO_BODY" | grep -o 'calendly_url":"[^"]*' | cut -d'"' -f3)
  echo "   Calendly URL: $CALENDLY"
else
  warn "/api/v1/public/demo-request → $DEMO_CODE"
  echo "   Response: $DEMO_BODY"
fi
echo ""

# ── Test 5: Checkout (1 SAR Pilot) ──
info "5/5 اختبار POST /api/v1/checkout (Pilot 1 ريال)"
CHECKOUT=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/checkout" \
  -H "Content-Type: application/json" \
  -d "{
    \"plan\": \"pilot_1sar\",
    \"email\": \"$TEST_EMAIL\"
  }")
CHECKOUT_BODY=$(echo "$CHECKOUT" | sed '$d')
CHECKOUT_CODE=$(echo "$CHECKOUT" | tail -n1)

echo ""
if [ "$CHECKOUT_CODE" = "200" ]; then
  PAYMENT_URL=$(echo "$CHECKOUT_BODY" | grep -o '"payment_url":"[^"]*' | cut -d'"' -f4)
  INVOICE_ID=$(echo "$CHECKOUT_BODY" | grep -o '"invoice_id":"[^"]*' | cut -d'"' -f4)

  pass "/api/v1/checkout → 200"
  echo ""
  echo "════════════════════════════════════════════════════════"
  echo -e "${GREEN}  🎉 النظام جاهز لاستقبال دفعات حقيقية${NC}"
  echo "════════════════════════════════════════════════════════"
  echo ""
  echo "  Invoice ID:  $INVOICE_ID"
  echo ""
  echo "  💳 Payment URL (افتح في المتصفح):"
  echo ""
  echo "  $PAYMENT_URL"
  echo ""
  echo "════════════════════════════════════════════════════════"
  echo ""
  warn "اختبر الدفع ببطاقتك الشخصية — ريال واحد للتأكد"
  warn "Moyasar سيرسل webhook لـ $BASE_URL/api/v1/webhooks/moyasar"
  warn "PostHog سيسجّل 'payment succeeded' event (إذا كان API key مضبوط)"
  echo ""
elif [ "$CHECKOUT_CODE" = "502" ]; then
  fail "checkout → 502 (Moyasar API error). تأكد من MOYASAR_SECRET_KEY صحيح في Railway"
elif [ "$CHECKOUT_CODE" = "401" ]; then
  fail "checkout → 401 (Moyasar Unauthorized). sk_live_* قد يكون ناقص أو خاطئ"
else
  fail "checkout → $CHECKOUT_CODE"
  echo "   Response: $CHECKOUT_BODY"
fi

echo ""
echo "── الخطوة التالية ──"
echo "1. افتح Moyasar Dashboard → Payments"
echo "   https://dashboard.moyasar.com/payments"
echo "2. بعد الدفع، Payment يظهر كـ 'paid'"
echo "3. تحقق من Railway Logs → يجب أن يظهر:"
echo "   'moyasar_webhook ok ... status=paid'"
echo "4. PostHog Events → payment_succeeded"
echo ""
echo "إذا الدفع نجح والـ webhook وصل → Dealix شغّال 100%"
echo ""
