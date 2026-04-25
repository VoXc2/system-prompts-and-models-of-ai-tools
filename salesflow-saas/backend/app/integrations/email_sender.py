"""Email Sender — SMTP with rate limiting, HTML wrapper, and compliance headers.

Supports Gmail app passwords. Adds professional HTML wrapper for Arabic
RTL emails and List-Unsubscribe header for compliance.
"""

import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.config import get_settings

logger = logging.getLogger("dealix.email")
settings = get_settings()

UNSUBSCRIBE_AR = "\n\n---\nإذا ما يناسبكم، اكتبوا \"إيقاف\" ولن نتواصل مرة ثانية."
UNSUBSCRIBE_EN = "\n\n---\nTo stop receiving these emails, reply with \"STOP\"."


def _wrap_html(body: str, direction: str = "rtl", lang: str = "ar") -> str:
    """Wrap plain text or simple HTML in a professional email template."""
    body_html = body.replace("\n", "<br>") if "<" not in body else body
    return f"""<!DOCTYPE html>
<html lang="{lang}" dir="{direction}">
<head><meta charset="UTF-8"></head>
<body style="font-family: 'Segoe UI', Tahoma, sans-serif; font-size: 15px;
  line-height: 1.7; color: #1a1a1a; max-width: 600px; margin: 0 auto;
  padding: 20px; direction: {direction};">
{body_html}
<div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #e5e5e5;
  font-size: 12px; color: #999;">
  Dealix — dealix.me
</div>
</body></html>"""


async def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    from_name: Optional[str] = None,
    language: str = "ar",
    add_unsubscribe: bool = True,
    delay_seconds: float = 0,
) -> dict:
    """Send email via SMTP with compliance headers.

    Args:
        to_email: Recipient email
        subject: Email subject
        body_html: Email body (plain text or HTML)
        from_name: Sender display name
        language: 'ar' or 'en' — affects direction and unsubscribe text
        add_unsubscribe: Whether to append unsubscribe line
        delay_seconds: Wait before sending (for rate limiting in batch)
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return {"status": "error", "detail": "SMTP_USER and SMTP_PASSWORD not configured. Add Gmail app password in Railway env."}

    if delay_seconds > 0:
        await asyncio.sleep(delay_seconds)

    if add_unsubscribe:
        unsub = UNSUBSCRIBE_AR if language == "ar" else UNSUBSCRIBE_EN
        body_html = body_html + unsub

    direction = "rtl" if language == "ar" else "ltr"
    wrapped = _wrap_html(body_html, direction=direction, lang=language)

    sender_name = from_name or settings.EMAIL_FROM_NAME or settings.APP_NAME
    from_addr = getattr(settings, "EMAIL_FROM_ADDRESS", settings.SMTP_USER)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{sender_name} <{from_addr}>"
    msg["To"] = to_email
    msg["List-Unsubscribe"] = f"<mailto:{from_addr}?subject=unsubscribe>"
    msg["X-Mailer"] = "Dealix/1.0"

    msg.attach(MIMEText(body_html, "plain", "utf-8"))
    msg.attach(MIMEText(wrapped, "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(from_addr, to_email, msg.as_string())
        logger.info("Email sent to %s: %s", to_email, subject[:50])
        return {"status": "sent", "to": to_email}
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP auth failed — check SMTP_USER and SMTP_PASSWORD (Gmail app password)")
        return {"status": "error", "detail": "SMTP authentication failed. Use Gmail App Password, not regular password."}
    except Exception as e:
        logger.error("Email send failed: %s", e)
        return {"status": "error", "detail": str(e)[:200]}


async def send_email_batch(
    emails: list[dict],
    delay_between: float = 2.0,
    max_batch: int = 10,
) -> dict:
    """Send a batch of emails with delays between each.

    Args:
        emails: List of dicts with {to, subject, body, language}
        delay_between: Seconds between each email (default 2)
        max_batch: Max emails per batch (default 10)

    Returns: {sent, failed, results}
    """
    sent = 0
    failed = 0
    results = []

    for i, email in enumerate(emails[:max_batch]):
        delay = delay_between if i > 0 else 0
        result = await send_email(
            to_email=email["to"],
            subject=email["subject"],
            body_html=email["body"],
            language=email.get("language", "ar"),
            delay_seconds=delay,
        )
        results.append({"to": email["to"], **result})
        if result["status"] == "sent":
            sent += 1
        else:
            failed += 1

    return {"sent": sent, "failed": failed, "total": len(results), "results": results}
