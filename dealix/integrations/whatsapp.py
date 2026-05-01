"""
WhatsApp Business Cloud API (Meta) integration.
تكامل واتساب للأعمال — Meta Cloud API.

Docs: https://developers.facebook.com/docs/whatsapp/cloud-api
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.config.settings import get_settings
from core.errors import IntegrationError
from core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class WhatsAppMessageResult:
    success: bool
    message_id: str | None = None
    error: str | None = None
    raw: dict[str, Any] | None = None


class WhatsAppClient:
    """Thin async client for WhatsApp Cloud API."""

    BASE_URL = "https://graph.facebook.com/v20.0"

    def __init__(self) -> None:
        self.settings = get_settings()

    # ── Config check ────────────────────────────────────────────
    @property
    def configured(self) -> bool:
        return (
            self.settings.whatsapp_access_token is not None
            and self.settings.whatsapp_phone_number_id is not None
        )

    def _headers(self) -> dict[str, str]:
        if not self.settings.whatsapp_access_token:
            raise IntegrationError("WHATSAPP_ACCESS_TOKEN not configured")
        token = self.settings.whatsapp_access_token.get_secret_value()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    # ── Outbound ────────────────────────────────────────────────
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def send_text(self, to: str, body: str) -> WhatsAppMessageResult:
        """Send a plain-text WhatsApp message."""
        if not self.configured:
            return WhatsAppMessageResult(success=False, error="WhatsApp not configured")
        if not self.settings.whatsapp_allow_live_send:
            logger.info("whatsapp_meta_send_blocked_by_policy", to_prefix=to[:6])
            return WhatsAppMessageResult(success=False, error="whatsapp_allow_live_send_false")

        phone_id = self.settings.whatsapp_phone_number_id
        url = f"{self.BASE_URL}/{phone_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to.lstrip("+"),
            "type": "text",
            "text": {"body": body, "preview_url": False},
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload, headers=self._headers())
                response.raise_for_status()
                data = response.json()

            message_id = None
            messages = data.get("messages", [])
            if messages:
                message_id = messages[0].get("id")
            logger.info("whatsapp_sent", to=to, message_id=message_id)
            return WhatsAppMessageResult(success=True, message_id=message_id, raw=data)
        except httpx.HTTPStatusError as e:
            logger.exception("whatsapp_send_failed", status=e.response.status_code)
            return WhatsAppMessageResult(success=False, error=str(e))
        except Exception as e:
            logger.exception("whatsapp_send_error", error=str(e))
            return WhatsAppMessageResult(success=False, error=str(e))

    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "ar",
        components: list[dict[str, Any]] | None = None,
    ) -> WhatsAppMessageResult:
        """Send a pre-approved template message."""
        if not self.configured:
            return WhatsAppMessageResult(success=False, error="WhatsApp not configured")
        if not self.settings.whatsapp_allow_live_send:
            logger.info("whatsapp_meta_template_blocked_by_policy", to_prefix=to[:6])
            return WhatsAppMessageResult(success=False, error="whatsapp_allow_live_send_false")

        phone_id = self.settings.whatsapp_phone_number_id
        url = f"{self.BASE_URL}/{phone_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to.lstrip("+"),
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": components or [],
            },
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload, headers=self._headers())
                response.raise_for_status()
                data = response.json()
            messages = data.get("messages", [])
            message_id = messages[0].get("id") if messages else None
            return WhatsAppMessageResult(success=True, message_id=message_id, raw=data)
        except Exception as e:
            return WhatsAppMessageResult(success=False, error=str(e))

    # ── Inbound webhook verification ────────────────────────────
    def verify_webhook(self, mode: str, token: str, challenge: str) -> str | None:
        """GET webhook verification step (return challenge if token matches)."""
        if not self.settings.whatsapp_verify_token:
            return None
        expected = self.settings.whatsapp_verify_token.get_secret_value()
        if mode == "subscribe" and hmac.compare_digest(token, expected):
            return challenge
        return None

    def verify_signature(self, payload: bytes, signature_header: str) -> bool:
        """Verify X-Hub-Signature-256 header from Meta."""
        if not self.settings.whatsapp_app_secret:
            return False
        app_secret = self.settings.whatsapp_app_secret.get_secret_value().encode()
        expected = "sha256=" + hmac.new(app_secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature_header)

    @staticmethod
    def parse_incoming(payload: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract incoming messages from a webhook payload."""
        messages: list[dict[str, Any]] = []
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []) or []:
                    messages.append(
                        {
                            "from": msg.get("from"),
                            "id": msg.get("id"),
                            "timestamp": msg.get("timestamp"),
                            "type": msg.get("type"),
                            "text": msg.get("text", {}).get("body"),
                            "contact_name": (
                                value.get("contacts", [{}])[0].get("profile", {}).get("name")
                                if value.get("contacts")
                                else None
                            ),
                        }
                    )
        return messages
