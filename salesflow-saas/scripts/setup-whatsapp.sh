#!/bin/bash
# ============================================================
# Dealix WhatsApp Integration - Deploy Script
# شغّل هذا السكربت على السيرفر: 46.225.123.110
# ============================================================

echo "🚀 Dealix WhatsApp Integration Setup"
echo "======================================"

cd /root/salesflow || { echo "❌ /root/salesflow not found"; exit 1; }

# ──────────────────────────────────────
# 1. Add WhatsApp credentials to .env
# ──────────────────────────────────────
echo "📝 Adding WhatsApp credentials to .env..."

# Check if already has WhatsApp config
if grep -q "WHATSAPP_API_TOKEN" .env 2>/dev/null; then
    echo "  Updating existing WhatsApp config..."
    sed -i 's|^WHATSAPP_API_TOKEN=.*|WHATSAPP_API_TOKEN=EAAk7SRCUYwUBRM7pm2Jc6AfqDKFQ8v5v2x2ZCJ4v3DdfehhZAQY18yc0ZBC1pZC3v0u0dvxlgT4mx49WYDuGZA7ReA8ogRMPDmCgyafsfBZAZC8OHGW9yAB5wZC2ip7gLSuRAgaBCvMYqjHEAANhh8e1DMUDnROwvHUrfnZA7pMXguWuwHrdA7jDpXovjkOEZBI0kWjiC4BZBZCW1ZCdFq9Gul4kqVojZCztBliUZBrzZChcmFwbe0uTvWw1sgZDZD|' .env
    sed -i 's|^WHATSAPP_PHONE_NUMBER_ID=.*|WHATSAPP_PHONE_NUMBER_ID=1068891919637293|' .env
    sed -i 's|^WHATSAPP_BUSINESS_ACCOUNT_ID=.*|WHATSAPP_BUSINESS_ACCOUNT_ID=2371037243416065|' .env
    sed -i 's|^WHATSAPP_VERIFY_TOKEN=.*|WHATSAPP_VERIFY_TOKEN=dealix_webhook_verify_2026|' .env
else
    echo "  Adding new WhatsApp config..."
    cat >> .env << 'ENVEOF'

# ── WhatsApp Business API (Saudi Number: +966 57 032 7724) ──
WHATSAPP_API_TOKEN=EAAk7SRCUYwUBRM7pm2Jc6AfqDKFQ8v5v2x2ZCJ4v3DdfehhZAQY18yc0ZBC1pZC3v0u0dvxlgT4mx49WYDuGZA7ReA8ogRMPDmCgyafsfBZAZC8OHGW9yAB5wZC2ip7gLSuRAgaBCvMYqjHEAANhh8e1DMUDnROwvHUrfnZA7pMXguWuwHrdA7jDpXovjkOEZBI0kWjiC4BZBZCW1ZCdFq9Gul4kqVojZCztBliUZBrzZChcmFwbe0uTvWw1sgZDZD
WHATSAPP_PHONE_NUMBER_ID=1068891919637293
WHATSAPP_BUSINESS_ACCOUNT_ID=2371037243416065
WHATSAPP_VERIFY_TOKEN=dealix_webhook_verify_2026

# ── WhatsApp Test Number (+1 555 158 3283) ──
WHATSAPP_TEST_PHONE_NUMBER_ID=982472281627090
WHATSAPP_TEST_BUSINESS_ACCOUNT_ID=928923493294526
ENVEOF
fi

echo "  ✅ WhatsApp credentials added"

# ──────────────────────────────────────
# 2. Test WhatsApp API connectivity
# ──────────────────────────────────────
echo ""
echo "🧪 Testing WhatsApp API..."

# Test with hello_world template to the Saudi number
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  "https://graph.facebook.com/v22.0/1068891919637293/messages" \
  -H "Authorization: Bearer EAAk7SRCUYwUBRM7pm2Jc6AfqDKFQ8v5v2x2ZCJ4v3DdfehhZAQY18yc0ZBC1pZC3v0u0dvxlgT4mx49WYDuGZA7ReA8ogRMPDmCgyafsfBZAZC8OHGW9yAB5wZC2ip7gLSuRAgaBCvMYqjHEAANhh8e1DMUDnROwvHUrfnZA7pMXguWuwHrdA7jDpXovjkOEZBI0kWjiC4BZBZCW1ZCdFq9Gul4kqVojZCztBliUZBrzZChcmFwbe0uTvWw1sgZDZD" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "96659778859",
    "type": "template",
    "template": {
      "name": "hello_world",
      "language": {"code": "en_US"}
    }
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "  ✅ WhatsApp API works! Message sent to +96659778859"
    echo "  Response: $BODY"
else
    echo "  ⚠️ API returned HTTP $HTTP_CODE"
    echo "  Response: $BODY"
    echo ""
    echo "  Possible issues:"
    echo "  1. Add payment method in Meta Business (if free tier)"
    echo "  2. Add +96659778859 as test recipient in Meta Developer Console"
    echo "  3. Token may have expired — regenerate in developers.facebook.com"
fi

# ──────────────────────────────────────
# 3. Restart services to pick up new env
# ──────────────────────────────────────
echo ""
echo "🔄 Restarting services..."
docker-compose restart api 2>/dev/null || docker compose restart api 2>/dev/null
echo "  ✅ API restarted with WhatsApp credentials"

# ──────────────────────────────────────
# 4. Verify health
# ──────────────────────────────────────
echo ""
echo "⏳ Waiting for API to come back..."
sleep 5
HEALTH=$(curl -s http://localhost:9000/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "  ✅ API is healthy: $HEALTH"
else
    echo "  ⚠️ API not responding yet, wait a few more seconds..."
    sleep 5
    curl -s http://localhost:9000/health
fi

echo ""
echo "======================================"
echo "✅ WhatsApp Integration Setup Complete"
echo "======================================"
echo ""
echo "📱 Configured Numbers:"
echo "  Saudi: +966 57 032 7724 (Phone ID: 1068891919637293)"
echo "  Test:  +1 555 158 3283  (Phone ID: 982472281627090)"
echo ""
echo "⚠️  IMPORTANT — Do these in Meta Developer Console:"
echo "  1. Add payment method (required to send messages first)"
echo "  2. Add +96659778859 as test recipient number"
echo "  3. Send first 'hello_world' template from Meta console"
echo "  4. Set webhook URL: http://46.225.123.110:9000/api/v1/webhooks/whatsapp"
echo "     Verify token: dealix_webhook_verify_2026"
echo ""
echo "🧪 Test command (after setup):"
echo '  curl -X POST "http://localhost:9000/api/v1/agents/outreach" \'
echo '    -H "Content-Type: application/json" \'
echo '    -d '"'"'{"phone":"96659778859","message":"مرحباً من Dealix!"}'"'"''
echo ""
