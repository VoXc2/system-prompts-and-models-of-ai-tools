#!/usr/bin/env bash
# Dealix — Moyasar Live Test Invoice
# Usage: bash docs/ops/moyasar_live_test.sh <customer_email> [amount_in_sar] [plan]
#
# Examples:
#   bash docs/ops/moyasar_live_test.sh sami.assiri11@gmail.com          # 1 SAR pilot
#   bash docs/ops/moyasar_live_test.sh customer@company.com 999 starter  # Starter
#   bash docs/ops/moyasar_live_test.sh customer@company.com 2999 growth  # Growth
#
# Requires: MOYASAR_SECRET_KEY env var set (sk_live_... or sk_test_...)

set -euo pipefail

CUSTOMER_EMAIL="${1:-sami.assiri11@gmail.com}"
AMOUNT_SAR="${2:-1}"
PLAN="${3:-pilot}"

: "${MOYASAR_SECRET_KEY:?Set MOYASAR_SECRET_KEY env var (sk_live_... or sk_test_...)}"

# Moyasar wants halalas (1 SAR = 100 halalas)
AMOUNT_HALALAS=$(( AMOUNT_SAR * 100 ))

# Plan-based description
case "$PLAN" in
  pilot)   DESC="Dealix Pilot — 7 أيام (قابل للاسترداد كاملاً)" ;;
  starter) DESC="Dealix Starter — اشتراك الشهر الأول (1-3 مندوبين)" ;;
  growth)  DESC="Dealix Growth — اشتراك الشهر الأول (4-10 مندوبين)" ;;
  scale)   DESC="Dealix Scale — اشتراك الشهر الأول (Enterprise)" ;;
  *)       DESC="Dealix — $PLAN" ;;
esac

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧾 Creating Moyasar invoice"
echo "   Customer: $CUSTOMER_EMAIL"
echo "   Amount:   $AMOUNT_SAR SAR  ($AMOUNT_HALALAS halalas)"
echo "   Plan:     $PLAN"
echo "   Key:      ${MOYASAR_SECRET_KEY:0:8}...  (${#MOYASAR_SECRET_KEY} chars)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

RESPONSE=$(curl -sS -X POST https://api.moyasar.com/v1/invoices \
  -u "${MOYASAR_SECRET_KEY}:" \
  -d "amount=${AMOUNT_HALALAS}" \
  -d "currency=SAR" \
  -d "description=${DESC}" \
  -d "callback_url=https://voxc2.github.io/dealix/thank-you.html" \
  -d "metadata[plan]=${PLAN}" \
  -d "metadata[customer_email]=${CUSTOMER_EMAIL}" \
  -d "metadata[source]=manual_sop")

echo ""
echo "📥 Response:"
echo "$RESPONSE"
echo ""

# Parse invoice URL if present
INVOICE_URL=$(echo "$RESPONSE" | grep -o '"url":"[^"]*"' | head -1 | sed 's/"url":"//;s/"$//')
INVOICE_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | sed 's/"id":"//;s/"$//')

if [[ -n "$INVOICE_URL" ]]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "✅ Invoice created"
  echo "   ID:  $INVOICE_ID"
  echo "   URL: $INVOICE_URL"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "📨 WhatsApp template:"
  echo ""
  echo "مرحباً،"
  echo ""
  echo "رابط دفع Dealix الخاص بك:"
  echo "$INVOICE_URL"
  echo ""
  echo "المبلغ: $AMOUNT_SAR ريال"
  echo "الباقة: $PLAN"
  echo "طرق الدفع: Mada / Visa / Mastercard / Apple Pay / STC Pay"
  echo ""
  echo "بعد الدفع تواصل معي مباشرة للتفعيل."
  echo ""
  echo "سامي — Dealix"
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "➡️  Next:"
  echo "    1. Copy the WhatsApp template above"
  echo "    2. Update pipeline_tracker.csv: invoice_id=$INVOICE_ID"
  echo "    3. Watch Moyasar dashboard for 'paid' status"
else
  echo "❌ Failed to create invoice. Check:"
  echo "   - MOYASAR_SECRET_KEY is correct"
  echo "   - Account is KYC-activated (if using sk_live_)"
  echo "   - Response above for error details"
  exit 1
fi
