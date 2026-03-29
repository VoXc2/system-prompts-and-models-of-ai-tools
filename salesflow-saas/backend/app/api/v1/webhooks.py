"""
Webhook handlers - WhatsApp incoming messages, payment callbacks, etc.
Auto-triggers AI agents to respond to incoming messages.
"""
import logging
from fastapi import APIRouter, Request, HTTPException
from app.config import get_settings
from app.workers.ai_agent_tasks import process_incoming_message

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()


@router.get("/whatsapp")
async def verify_whatsapp_webhook(request: Request):
    """WhatsApp webhook verification (GET request from Meta)."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        return int(challenge)

    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Handle incoming WhatsApp messages.
    Automatically triggers AI agent to process and respond.
    """
    body = await request.json()

    # Extract message data from WhatsApp webhook payload
    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            contacts = value.get("contacts", [])

            for i, message in enumerate(messages):
                msg_type = message.get("type")
                sender_phone = message.get("from", "")
                msg_id = message.get("id", "")

                # Get contact name
                contact_name = "عميل"
                if contacts and i < len(contacts):
                    profile = contacts[i].get("profile", {})
                    contact_name = profile.get("name", "عميل")

                # Extract message text
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
                    # Trigger AI agent to process and respond
                    lead_data = {
                        "name": contact_name,
                        "phone": sender_phone,
                        "source": "whatsapp",
                        "status": "contacted",
                    }

                    # Send to Celery for async processing
                    process_incoming_message.delay(
                        tenant_id="default",
                        message=text,
                        lead_data=lead_data,
                        industry="general",
                    )

            # Handle message status updates
            statuses = value.get("statuses", [])
            for status in statuses:
                status_type = status.get("status", "unknown")
                recipient_id = status.get("recipient_id", "unknown")
                timestamp = status.get("timestamp", "")
                msg_id = status.get("id", "")
                if status_type == "failed":
                    errors = status.get("errors", [])
                    error_detail = errors[0] if errors else {}
                    logger.error(
                        f"WhatsApp delivery FAILED to {recipient_id}: "
                        f"code={error_detail.get('code')}, title={error_detail.get('title')}, "
                        f"message={error_detail.get('message')}, msg_id={msg_id}"
                    )
                else:
                    logger.info(f"WhatsApp status: {status_type} for {recipient_id} (msg={msg_id}, ts={timestamp})")

    return {"status": "ok"}
