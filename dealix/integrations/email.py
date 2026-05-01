"""
Email integration — supports Resend (preferred), SendGrid, or SMTP.
تكامل البريد الإلكتروني.
"""

from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.config.settings import get_settings
from core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class EmailResult:
    success: bool
    provider: str
    message_id: str | None = None
    error: str | None = None


class EmailClient:
    """Unified email client — picks provider from settings."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def send(
        self,
        *,
        to: str | list[str],
        subject: str,
        body_text: str | None = None,
        body_html: str | None = None,
        reply_to: str | None = None,
    ) -> EmailResult:
        """Send an email via configured provider."""
        provider = self.settings.email_provider
        if provider == "resend":
            return await self._send_resend(to, subject, body_text, body_html, reply_to)
        if provider == "sendgrid":
            return await self._send_sendgrid(to, subject, body_text, body_html, reply_to)
        if provider == "smtp":
            return await self._send_smtp(to, subject, body_text, body_html, reply_to)
        return EmailResult(success=False, provider=provider, error="Unknown provider")

    # ── Resend ──────────────────────────────────────────────────
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def _send_resend(
        self,
        to: str | list[str],
        subject: str,
        body_text: str | None,
        body_html: str | None,
        reply_to: str | None,
    ) -> EmailResult:
        if not self.settings.resend_api_key:
            return EmailResult(
                success=False, provider="resend", error="RESEND_API_KEY not configured"
            )

        api_key = self.settings.resend_api_key.get_secret_value()
        payload: dict[str, Any] = {
            "from": f"{self.settings.email_from_name} <{self.settings.email_from}>",
            "to": [to] if isinstance(to, str) else to,
            "subject": subject,
        }
        if body_html:
            payload["html"] = body_html
        if body_text:
            payload["text"] = body_text
        if reply_to:
            payload["reply_to"] = reply_to

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.resend.com/emails", json=payload, headers=headers
            )
            response.raise_for_status()
            data = response.json()

        message_id = data.get("id")
        logger.info("email_sent_resend", to=to, message_id=message_id)
        return EmailResult(success=True, provider="resend", message_id=message_id)

    # ── SendGrid ────────────────────────────────────────────────
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def _send_sendgrid(
        self,
        to: str | list[str],
        subject: str,
        body_text: str | None,
        body_html: str | None,
        reply_to: str | None,
    ) -> EmailResult:
        if not self.settings.sendgrid_api_key:
            return EmailResult(
                success=False, provider="sendgrid", error="SENDGRID_API_KEY not configured"
            )
        api_key = self.settings.sendgrid_api_key.get_secret_value()

        recipients = [to] if isinstance(to, str) else to
        personalizations = [{"to": [{"email": e} for e in recipients]}]
        content = []
        if body_text:
            content.append({"type": "text/plain", "value": body_text})
        if body_html:
            content.append({"type": "text/html", "value": body_html})
        if not content:
            return EmailResult(success=False, provider="sendgrid", error="No email body provided")

        payload: dict[str, Any] = {
            "personalizations": personalizations,
            "from": {
                "email": self.settings.email_from,
                "name": self.settings.email_from_name,
            },
            "subject": subject,
            "content": content,
        }
        if reply_to:
            payload["reply_to"] = {"email": reply_to}

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.sendgrid.com/v3/mail/send", json=payload, headers=headers
            )
            response.raise_for_status()

        message_id = response.headers.get("X-Message-Id")
        logger.info("email_sent_sendgrid", to=to, message_id=message_id)
        return EmailResult(success=True, provider="sendgrid", message_id=message_id)

    # ── SMTP (fallback) ─────────────────────────────────────────
    async def _send_smtp(
        self,
        to: str | list[str],
        subject: str,
        body_text: str | None,
        body_html: str | None,
        reply_to: str | None,
    ) -> EmailResult:
        if not (self.settings.smtp_host and self.settings.smtp_user):
            return EmailResult(success=False, provider="smtp", error="SMTP not configured")

        message = EmailMessage()
        message["From"] = f"{self.settings.email_from_name} <{self.settings.email_from}>"
        message["To"] = to if isinstance(to, str) else ", ".join(to)
        message["Subject"] = subject
        if reply_to:
            message["Reply-To"] = reply_to
        if body_text:
            message.set_content(body_text)
        if body_html:
            message.add_alternative(body_html, subtype="html")

        try:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as smtp:
                if self.settings.smtp_tls:
                    smtp.starttls()
                if self.settings.smtp_password:
                    smtp.login(
                        self.settings.smtp_user,
                        self.settings.smtp_password.get_secret_value(),
                    )
                smtp.send_message(message)
            logger.info("email_sent_smtp", to=to)
            return EmailResult(success=True, provider="smtp")
        except Exception as e:
            logger.exception("email_smtp_failed", error=str(e))
            return EmailResult(success=False, provider="smtp", error=str(e))
