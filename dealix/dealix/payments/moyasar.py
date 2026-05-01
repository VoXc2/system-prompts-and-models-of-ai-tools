"""
Moyasar client — Invoices + Payments + Webhook verification.
Ref: https://docs.moyasar.com/api/invoices/01-create-invoice
     https://docs.moyasar.com/api/other/webhooks/webhook-reference/

Security model:
  - API key in MOYASAR_SECRET_KEY (HTTP Basic auth, key is the username)
  - Webhooks authenticated via a shared secret_token included in the webhook body
    and compared in constant time against MOYASAR_WEBHOOK_SECRET.

Amount is in the smallest currency unit (SAR halalas) — 10 SAR = 1000.
"""

from __future__ import annotations

import base64
import hmac
import logging
import os
from typing import Any

import httpx

log = logging.getLogger(__name__)


class MoyasarClient:
    BASE = "https://api.moyasar.com/v1"

    def __init__(self, secret_key: str | None = None) -> None:
        self.secret_key = secret_key or os.getenv("MOYASAR_SECRET_KEY", "")
        # Moyasar uses HTTP Basic with key as username and empty password
        auth = base64.b64encode(f"{self.secret_key}:".encode()).decode()
        self._auth_header = {"Authorization": f"Basic {auth}"}

    def _headers(self) -> dict[str, str]:
        return {**self._auth_header, "Content-Type": "application/json"}

    async def create_invoice(
        self,
        amount_halalas: int,
        currency: str = "SAR",
        description: str = "",
        callback_url: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a hosted payment invoice. Returns invoice object with `url` field
        that the customer visits to pay.
        """
        if not self.secret_key:
            raise RuntimeError("MOYASAR_SECRET_KEY not set")
        payload: dict[str, Any] = {
            "amount": int(amount_halalas),
            "currency": currency,
            "description": description or "Dealix subscription",
        }
        if callback_url:
            payload["callback_url"] = callback_url
        if metadata:
            # Moyasar expects string values only
            payload["metadata"] = {k: str(v) for k, v in metadata.items()}

        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.post(f"{self.BASE}/invoices", headers=self._headers(), json=payload)
            r.raise_for_status()
            return r.json()

    async def fetch_payment(self, payment_id: str) -> dict[str, Any]:
        if not self.secret_key:
            raise RuntimeError("MOYASAR_SECRET_KEY not set")
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{self.BASE}/payments/{payment_id}", headers=self._headers())
            r.raise_for_status()
            return r.json()

    async def fetch_invoice(self, invoice_id: str) -> dict[str, Any]:
        if not self.secret_key:
            raise RuntimeError("MOYASAR_SECRET_KEY not set")
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{self.BASE}/invoices/{invoice_id}", headers=self._headers())
            r.raise_for_status()
            return r.json()


def verify_webhook(body: dict[str, Any], expected_secret: str | None = None) -> bool:
    """
    Moyasar webhook verification.
    Webhooks include a `secret_token` field in the JSON body which is the per-endpoint
    secret the merchant set when registering the webhook. Compare in constant time.
    """
    expected = expected_secret or os.getenv("MOYASAR_WEBHOOK_SECRET", "")
    if not expected:
        log.warning("moyasar_webhook_no_secret_configured")
        return False
    provided = str(body.get("secret_token") or "")
    if not provided:
        return False
    return hmac.compare_digest(provided, expected)
