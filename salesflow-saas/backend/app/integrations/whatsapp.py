import re
import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

WHATSAPP_API_URL = "https://graph.facebook.com/v22.0"

# E.164 phone format: + followed by 1-15 digits
E164_PATTERN = re.compile(r"^\+[1-9]\d{1,14}$")


def _normalize_phone(phone: str) -> str:
    """Normalize phone number to E.164 format."""
    phone = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    # Saudi numbers: 05xxxxxxxx → +9665xxxxxxxx
    if phone.startswith("05") and len(phone) == 10:
        phone = "+966" + phone[1:]
    elif phone.startswith("5") and len(phone) == 9:
        phone = "+966" + phone
    elif phone.startswith("966") and not phone.startswith("+"):
        phone = "+" + phone
    elif not phone.startswith("+"):
        phone = "+" + phone
    return phone


def _validate_phone(phone: str) -> str:
    """Validate and normalize phone number. Raises ValueError if invalid."""
    phone = _normalize_phone(phone)
    if not E164_PATTERN.match(phone):
        raise ValueError(f"Invalid phone number format: {phone}. Must be E.164 format (e.g. +966501234567)")
    return phone


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
async def send_whatsapp_message(phone: str, message: str) -> dict:
    """Send a text message via WhatsApp Business API."""
    if not settings.WHATSAPP_API_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        logger.error("WhatsApp not configured: missing API_TOKEN or PHONE_NUMBER_ID")
        return {"status": "error", "detail": "WhatsApp not configured — set WHATSAPP_API_TOKEN and WHATSAPP_PHONE_NUMBER_ID in .env"}

    try:
        phone = _validate_phone(phone)
    except ValueError as e:
        logger.error(f"WhatsApp send failed: {e}")
        return {"status": "error", "detail": str(e)}

    url = f"{WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": message},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            error_data = response.json()
            logger.error(f"WhatsApp API error {response.status_code}: {error_data}")
            return {"status": "error", "http_code": response.status_code, "detail": error_data}
        result = response.json()
        logger.info(f"WhatsApp message sent to {phone}: message_id={result.get('messages', [{}])[0].get('id', 'unknown')}")
        return {"status": "success", **result}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
async def send_whatsapp_template(phone: str, template_name: str, language: str = "ar", components: list = None) -> dict:
    """Send a template message via WhatsApp Business API."""
    if not settings.WHATSAPP_API_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        logger.error("WhatsApp not configured: missing API_TOKEN or PHONE_NUMBER_ID")
        return {"status": "error", "detail": "WhatsApp not configured — set WHATSAPP_API_TOKEN and WHATSAPP_PHONE_NUMBER_ID in .env"}

    try:
        phone = _validate_phone(phone)
    except ValueError as e:
        logger.error(f"WhatsApp template send failed: {e}")
        return {"status": "error", "detail": str(e)}

    url = f"{WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
        },
    }
    if components:
        payload["template"]["components"] = components

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            error_data = response.json()
            logger.error(f"WhatsApp template API error {response.status_code}: {error_data}")
            return {"status": "error", "http_code": response.status_code, "detail": error_data}
        result = response.json()
        logger.info(f"WhatsApp template '{template_name}' sent to {phone}")
        return {"status": "success", **result}
