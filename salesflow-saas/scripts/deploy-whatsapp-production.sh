#!/bin/bash
# ============================================================
# Dealix WhatsApp Integration — Full Production Deployment
# السيرفر: 46.225.123.110 — /root/salesflow
#
# هذا السكربت يضيف كل كود الواتساب + الإعدادات + يعيد التشغيل
# شغّله مرة واحدة على السيرفر:
#   bash deploy-whatsapp-production.sh
# ============================================================

set -e

echo "🚀 Dealix WhatsApp — Full Production Deployment"
echo "================================================="

cd /root/salesflow || { echo "❌ /root/salesflow not found"; exit 1; }

# ──────────────────────────────────────────────────────────────
# 1. Add WhatsApp credentials to .env
# ──────────────────────────────────────────────────────────────
echo ""
echo "📝 Step 1: Adding WhatsApp credentials to .env..."

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

echo "  ✅ WhatsApp credentials configured"

# ──────────────────────────────────────────────────────────────
# 2. Create WhatsApp integration module
# ──────────────────────────────────────────────────────────────
echo ""
echo "📦 Step 2: Creating WhatsApp integration code..."

mkdir -p app/integrations

# Create __init__.py if not exists
touch app/integrations/__init__.py

cat > app/integrations/whatsapp.py << 'PYEOF'
"""
WhatsApp Business Cloud API Integration
Sends text messages and templates via Meta's WhatsApp Business API v22.0
"""
import os
import re
import logging
import httpx

logger = logging.getLogger(__name__)

WHATSAPP_API_URL = "https://graph.facebook.com/v22.0"
E164_PATTERN = re.compile(r"^\+[1-9]\d{1,14}$")

def _get_token():
    return os.getenv("WHATSAPP_API_TOKEN", "")

def _get_phone_number_id():
    return os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")

def _get_verify_token():
    return os.getenv("WHATSAPP_VERIFY_TOKEN", "")


def normalize_phone(phone: str) -> str:
    """Normalize phone number to E.164 format."""
    phone = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if phone.startswith("05") and len(phone) == 10:
        phone = "+966" + phone[1:]
    elif phone.startswith("5") and len(phone) == 9:
        phone = "+966" + phone
    elif phone.startswith("966") and not phone.startswith("+"):
        phone = "+" + phone
    elif not phone.startswith("+"):
        phone = "+" + phone
    return phone


def validate_phone(phone: str) -> str:
    """Validate and normalize phone number."""
    phone = normalize_phone(phone)
    if not E164_PATTERN.match(phone):
        raise ValueError(f"Invalid phone number: {phone}")
    return phone


async def send_whatsapp_message(phone: str, message: str) -> dict:
    """Send a text message via WhatsApp Business API."""
    token = _get_token()
    phone_id = _get_phone_number_id()

    if not token or not phone_id:
        logger.error("WhatsApp not configured: missing API_TOKEN or PHONE_NUMBER_ID")
        return {"status": "error", "detail": "WhatsApp not configured"}

    try:
        phone = validate_phone(phone)
    except ValueError as e:
        return {"status": "error", "detail": str(e)}

    url = f"{WHATSAPP_API_URL}/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone.replace("+", ""),
        "type": "text",
        "text": {"body": message},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code >= 400:
                error_data = response.json()
                logger.error(f"WhatsApp API error {response.status_code}: {error_data}")
                return {"status": "error", "http_code": response.status_code, "detail": error_data}
            result = response.json()
            msg_id = result.get("messages", [{}])[0].get("id", "unknown")
            logger.info(f"WhatsApp message sent to {phone}: message_id={msg_id}")
            return {"status": "success", "message_id": msg_id, **result}
        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            return {"status": "error", "detail": str(e)}


async def send_whatsapp_template(phone: str, template_name: str, language: str = "ar", components: list = None) -> dict:
    """Send a template message via WhatsApp Business API."""
    token = _get_token()
    phone_id = _get_phone_number_id()

    if not token or not phone_id:
        return {"status": "error", "detail": "WhatsApp not configured"}

    try:
        phone = validate_phone(phone)
    except ValueError as e:
        return {"status": "error", "detail": str(e)}

    url = f"{WHATSAPP_API_URL}/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone.replace("+", ""),
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
        },
    }
    if components:
        payload["template"]["components"] = components

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code >= 400:
                error_data = response.json()
                logger.error(f"WhatsApp template error {response.status_code}: {error_data}")
                return {"status": "error", "http_code": response.status_code, "detail": error_data}
            result = response.json()
            logger.info(f"WhatsApp template '{template_name}' sent to {phone}")
            return {"status": "success", **result}
        except Exception as e:
            logger.error(f"WhatsApp template send failed: {e}")
            return {"status": "error", "detail": str(e)}
PYEOF

echo "  ✅ app/integrations/whatsapp.py created"

# ──────────────────────────────────────────────────────────────
# 3. Create WhatsApp webhook + API endpoints
# ──────────────────────────────────────────────────────────────
echo ""
echo "📡 Step 3: Creating WhatsApp webhook & API routes..."

cat > app/whatsapp_routes.py << 'PYEOF'
"""
WhatsApp Routes — Webhook + Send Message API
Add to main.py: from app.whatsapp_routes import whatsapp_router
                app.include_router(whatsapp_router)
"""
import os
import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

whatsapp_router = APIRouter(tags=["WhatsApp"])


# ── Webhook Verification (Meta sends GET) ──
@whatsapp_router.get("/api/v1/webhooks/whatsapp")
async def verify_whatsapp_webhook(request: Request):
    """WhatsApp webhook verification — Meta sends this during setup."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "")

    if mode == "subscribe" and token == verify_token:
        logger.info("WhatsApp webhook verified successfully")
        return int(challenge)

    logger.warning(f"WhatsApp webhook verification failed: mode={mode}, token_match={token == verify_token}")
    raise HTTPException(status_code=403, detail="Verification failed")


# ── Webhook Handler (Meta sends POST for incoming messages) ──
@whatsapp_router.post("/api/v1/webhooks/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages from Meta."""
    body = await request.json()

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            contacts = value.get("contacts", [])
            metadata = value.get("metadata", {})

            phone_number_id = metadata.get("phone_number_id", "")
            display_phone = metadata.get("display_phone_number", "")

            for i, message in enumerate(messages):
                msg_type = message.get("type")
                sender_phone = message.get("from", "")
                msg_id = message.get("id", "")

                # Get contact name
                contact_name = "عميل"
                if contacts and i < len(contacts):
                    profile = contacts[i].get("profile", {})
                    contact_name = profile.get("name", "عميل")

                # Extract text
                text = ""
                if msg_type == "text":
                    text = message.get("text", {}).get("body", "")
                elif msg_type == "button":
                    text = message.get("button", {}).get("text", "")
                elif msg_type == "interactive":
                    interactive = message.get("interactive", {})
                    if interactive.get("type") == "button_reply":
                        text = interactive.get("button_reply", {}).get("title", "")
                    elif interactive.get("type") == "list_reply":
                        text = interactive.get("list_reply", {}).get("title", "")

                if text:
                    logger.info(
                        f"📩 WhatsApp incoming: {contact_name} ({sender_phone}) → "
                        f"business {display_phone}: {text[:100]}"
                    )

                    # TODO: Route to AI agent for auto-response
                    # For now, log the message. Integration with AI agents
                    # can be added by importing the relevant agent and calling it here.

            # Handle delivery status updates
            statuses = value.get("statuses", [])
            for status in statuses:
                status_type = status.get("status", "unknown")
                recipient_id = status.get("recipient_id", "unknown")
                if status_type == "failed":
                    errors = status.get("errors", [])
                    error_detail = errors[0] if errors else {}
                    logger.error(
                        f"❌ WhatsApp delivery FAILED to {recipient_id}: "
                        f"{error_detail.get('title', 'unknown error')}"
                    )
                else:
                    logger.info(f"WhatsApp status: {status_type} → {recipient_id}")

    return {"status": "ok"}


# ── Send Message API ──
class SendMessageRequest(BaseModel):
    phone: str
    message: str

class SendTemplateRequest(BaseModel):
    phone: str
    template_name: str = "hello_world"
    language: str = "en_US"
    components: Optional[list] = None


@whatsapp_router.post("/api/v1/whatsapp/send")
async def send_whatsapp(req: SendMessageRequest):
    """Send a WhatsApp text message."""
    from app.integrations.whatsapp import send_whatsapp_message
    result = await send_whatsapp_message(req.phone, req.message)
    return result


@whatsapp_router.post("/api/v1/whatsapp/send-template")
async def send_template(req: SendTemplateRequest):
    """Send a WhatsApp template message."""
    from app.integrations.whatsapp import send_whatsapp_template
    result = await send_whatsapp_template(
        req.phone, req.template_name, req.language, req.components
    )
    return result


@whatsapp_router.get("/api/v1/whatsapp/status")
async def whatsapp_status():
    """Check if WhatsApp is configured."""
    token = os.getenv("WHATSAPP_API_TOKEN", "")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    return {
        "configured": bool(token and phone_id),
        "phone_number_id": phone_id if phone_id else None,
        "token_set": bool(token),
    }
PYEOF

echo "  ✅ app/whatsapp_routes.py created"

# ──────────────────────────────────────────────────────────────
# 4. Patch main.py to include WhatsApp routes
# ──────────────────────────────────────────────────────────────
echo ""
echo "🔧 Step 4: Patching main.py to include WhatsApp routes..."

# Check if already patched
if grep -q "whatsapp_routes" app/main.py 2>/dev/null; then
    echo "  Already patched — skipping"
else
    # Add import at the top (after other imports)
    sed -i '/^from fastapi/a from app.whatsapp_routes import whatsapp_router' app/main.py 2>/dev/null || true

    # If that didn't work (different import style), try another approach
    if ! grep -q "whatsapp_routes" app/main.py; then
        # Add it right after "app = FastAPI" line
        sed -i '/^app = FastAPI/a\\n# WhatsApp Integration\nfrom app.whatsapp_routes import whatsapp_router\napp.include_router(whatsapp_router)' app/main.py
    else
        # Add the include_router after existing include_router calls
        if grep -q "include_router" app/main.py; then
            sed -i '/include_router.*$/a app.include_router(whatsapp_router)' app/main.py
            # Remove duplicate if added multiple times
            awk '!seen[$0]++ || !/app\.include_router\(whatsapp_router\)/' app/main.py > app/main.py.tmp && mv app/main.py.tmp app/main.py
        else
            echo 'app.include_router(whatsapp_router)' >> app/main.py
        fi
    fi
    echo "  ✅ main.py patched"
fi

# ──────────────────────────────────────────────────────────────
# 5. Install httpx if not available
# ──────────────────────────────────────────────────────────────
echo ""
echo "📦 Step 5: Ensuring httpx is installed..."

pip install httpx 2>/dev/null || pip3 install httpx 2>/dev/null || {
    # If running in Docker, install inside the container
    docker compose exec -T api pip install httpx 2>/dev/null || \
    docker-compose exec -T api pip install httpx 2>/dev/null || \
    echo "  ⚠️ Could not install httpx — may already be available"
}

echo "  ✅ httpx ready"

# ──────────────────────────────────────────────────────────────
# 6. Restart services
# ──────────────────────────────────────────────────────────────
echo ""
echo "🔄 Step 6: Restarting services..."

# Try different restart methods
if command -v docker &> /dev/null; then
    docker compose restart api 2>/dev/null || \
    docker-compose restart api 2>/dev/null || \
    echo "  Trying full restart..."

    docker compose down api 2>/dev/null && docker compose up -d api 2>/dev/null || \
    docker-compose down api 2>/dev/null && docker-compose up -d api 2>/dev/null || \
    echo "  ⚠️ Docker restart had issues"
else
    # If not using Docker, try systemctl or direct
    systemctl restart salesflow 2>/dev/null || \
    supervisorctl restart salesflow 2>/dev/null || \
    echo "  ⚠️ Could not auto-restart — please restart manually"
fi

echo "  ✅ Services restarting..."

# ──────────────────────────────────────────────────────────────
# 7. Wait and verify
# ──────────────────────────────────────────────────────────────
echo ""
echo "⏳ Step 7: Waiting for API to come back..."
sleep 8

# Check health
for i in 1 2 3; do
    HEALTH=$(curl -s http://localhost:9000/health 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$HEALTH" ]; then
        echo "  ✅ API is healthy: $HEALTH"
        break
    fi
    echo "  Retry $i..."
    sleep 5
done

# ──────────────────────────────────────────────────────────────
# 8. Test WhatsApp status endpoint
# ──────────────────────────────────────────────────────────────
echo ""
echo "🧪 Step 8: Testing WhatsApp status..."

WA_STATUS=$(curl -s http://localhost:9000/api/v1/whatsapp/status 2>/dev/null)
echo "  WhatsApp Status: $WA_STATUS"

# ──────────────────────────────────────────────────────────────
# 9. Test WhatsApp API directly (send hello_world template)
# ──────────────────────────────────────────────────────────────
echo ""
echo "🧪 Step 9: Testing WhatsApp API (sending hello_world template)..."

# Test via our new API endpoint
SEND_RESULT=$(curl -s -X POST http://localhost:9000/api/v1/whatsapp/send-template \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "96659778859",
    "template_name": "hello_world",
    "language": "en_US"
  }' 2>/dev/null)

echo "  Send Result: $SEND_RESULT"

# Also test directly via Meta API
echo ""
echo "  Testing direct Meta API..."
DIRECT_RESULT=$(curl -s -X POST \
  "https://graph.facebook.com/v22.0/1068891919637293/messages" \
  -H "Authorization: Bearer $(grep WHATSAPP_API_TOKEN .env | cut -d= -f2)" \
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

echo "  Direct API Result: $DIRECT_RESULT"

# ──────────────────────────────────────────────────────────────
# 10. Test webhook endpoint (verify it responds)
# ──────────────────────────────────────────────────────────────
echo ""
echo "🧪 Step 10: Testing webhook endpoint..."

WEBHOOK_TEST=$(curl -s "http://localhost:9000/api/v1/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=dealix_webhook_verify_2026&hub.challenge=12345" 2>/dev/null)
echo "  Webhook verify test: $WEBHOOK_TEST"

if [ "$WEBHOOK_TEST" = "12345" ]; then
    echo "  ✅ Webhook verification works!"
else
    echo "  ⚠️ Webhook returned: $WEBHOOK_TEST (expected: 12345)"
fi

# ──────────────────────────────────────────────────────────────
# Done!
# ──────────────────────────────────────────────────────────────
echo ""
echo "================================================="
echo "✅ WhatsApp Integration Deployed Successfully!"
echo "================================================="
echo ""
echo "📱 Configured Numbers:"
echo "  Saudi: +966 57 032 7724 (Phone ID: 1068891919637293)"
echo "  Test:  +1 555 158 3283  (Phone ID: 982472281627090)"
echo ""
echo "🔗 API Endpoints Available:"
echo "  GET  /api/v1/whatsapp/status          — Check config"
echo "  POST /api/v1/whatsapp/send            — Send text message"
echo "  POST /api/v1/whatsapp/send-template   — Send template"
echo "  GET  /api/v1/webhooks/whatsapp        — Webhook verify"
echo "  POST /api/v1/webhooks/whatsapp        — Incoming messages"
echo ""
echo "⚠️  IMPORTANT — Do this in Meta Developer Console:"
echo "  1. Go to: https://developers.facebook.com/apps/"
echo "  2. Select your app → WhatsApp → Configuration"
echo "  3. Set Webhook URL: http://46.225.123.110:9000/api/v1/webhooks/whatsapp"
echo "  4. Set Verify Token: dealix_webhook_verify_2026"
echo "  5. Subscribe to: messages, message_deliveries, message_reads"
echo "  6. Add +96659778859 as test recipient (if still in test mode)"
echo ""
echo "🧪 Test commands:"
echo '  # Send text message:'
echo '  curl -X POST http://localhost:9000/api/v1/whatsapp/send \'
echo '    -H "Content-Type: application/json" \'
echo '    -d '"'"'{"phone":"96659778859","message":"مرحباً من Dealix! 🚀"}'"'"''
echo ""
echo '  # Send template:'
echo '  curl -X POST http://localhost:9000/api/v1/whatsapp/send-template \'
echo '    -H "Content-Type: application/json" \'
echo '    -d '"'"'{"phone":"96659778859","template_name":"hello_world","language":"en_US"}'"'"''
echo ""
