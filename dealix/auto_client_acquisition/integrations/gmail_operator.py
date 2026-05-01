"""Gmail API-shaped draft payloads — no OAuth, no HTTP."""

from __future__ import annotations

import base64
from email.message import EmailMessage
from typing import Any


def build_gmail_draft_payload(params: dict[str, Any]) -> dict[str, Any]:
    """
    Returns ``{"message": {"raw": "<urlsafe base64 RFC822>"}}`` subset compatible with
    Gmail ``users.drafts.create`` — encoding only, no API call.
    """
    to = str(params.get("to") or "prospect@example.com")
    subject = str(params.get("subject_ar") or params.get("subject") or "مسودة — Dealix")
    body_text = str(params.get("body_ar") or params.get("body") or "نص المسودة الداخلي.")
    msg = EmailMessage()
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body_text, charset="utf-8")
    raw_bytes = msg.as_bytes()
    raw_b64 = base64.urlsafe_b64encode(raw_bytes).decode("ascii").rstrip("=")
    return {
        "approval_required": True,
        "message": {"raw": raw_b64},
        "note_ar": "هيكل مسودة فقط — لا يُرسل عبر Gmail API في MVP.",
    }
