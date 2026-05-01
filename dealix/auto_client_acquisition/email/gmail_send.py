"""
Gmail OAuth send adapter — uses refresh-token flow, no password.

Flow:
1. Sami runs OAuth consent ONCE in browser → gets refresh_token.
2. We store refresh_token in Railway env: GMAIL_REFRESH_TOKEN.
3. Each send: POST refresh_token to Google → access_token (1h TTL).
4. Build RFC822 message → base64url encode → POST to gmail.googleapis.com.

Env required:
    GMAIL_CLIENT_ID
    GMAIL_CLIENT_SECRET
    GMAIL_REFRESH_TOKEN
    GMAIL_SENDER_EMAIL  (the @ address messages are sent from)

Scope: gmail.send (single-purpose, lowest privilege).

We DO NOT cache the access token globally — refresh per send. ~50 sends/day
is well within Google's quota.
"""

from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Any

import httpx

log = logging.getLogger(__name__)

OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
GMAIL_DRAFTS_URL = "https://gmail.googleapis.com/gmail/v1/users/me/drafts"


@dataclass
class GmailSendResult:
    status: str  # ok | no_keys | auth_error | http_error | quota_exceeded
    gmail_message_id: str | None = None
    error: str | None = None


def is_configured() -> bool:
    return all(
        os.getenv(k, "").strip()
        for k in (
            "GMAIL_CLIENT_ID",
            "GMAIL_CLIENT_SECRET",
            "GMAIL_REFRESH_TOKEN",
            "GMAIL_SENDER_EMAIL",
        )
    )


async def _refresh_access_token(client: httpx.AsyncClient) -> str | None:
    cid = os.getenv("GMAIL_CLIENT_ID", "").strip()
    csec = os.getenv("GMAIL_CLIENT_SECRET", "").strip()
    rtok = os.getenv("GMAIL_REFRESH_TOKEN", "").strip()
    if not (cid and csec and rtok):
        return None
    data = {
        "client_id": cid,
        "client_secret": csec,
        "refresh_token": rtok,
        "grant_type": "refresh_token",
    }
    try:
        r = await client.post(OAUTH_TOKEN_URL, data=data, timeout=10.0)
    except Exception as exc:  # noqa: BLE001
        log.warning("gmail_oauth_refresh_failed err=%s", exc)
        return None
    if r.status_code != 200:
        log.warning("gmail_oauth_refresh_status=%s body=%s", r.status_code, r.text[:200])
        return None
    payload = r.json() or {}
    return payload.get("access_token")


def _build_rfc822(
    *,
    sender_name: str,
    sender_email: str,
    to_email: str,
    subject: str,
    body_plain: str,
    reply_to: str | None = None,
    list_unsubscribe_email: str | None = None,
) -> bytes:
    """
    Build a minimal RFC822 message including List-Unsubscribe header (Gmail
    bulk-sender requirement for one-click opt-out).
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr((sender_name, sender_email))
    msg["To"] = to_email
    if reply_to:
        msg["Reply-To"] = reply_to
    if list_unsubscribe_email:
        # RFC 8058 one-click unsubscribe
        msg["List-Unsubscribe"] = f"<mailto:{list_unsubscribe_email}?subject=unsubscribe>"
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg.attach(MIMEText(body_plain, "plain", "utf-8"))
    return msg.as_bytes()


async def send_email(
    *,
    to_email: str,
    subject: str,
    body_plain: str,
    reply_to: str | None = None,
    sender_name: str = "Sami | Dealix",
) -> GmailSendResult:
    """Send a single email via Gmail OAuth. Returns GmailSendResult."""
    if not is_configured():
        return GmailSendResult(status="no_keys", error="GMAIL_* env vars not set")

    sender_email = os.getenv("GMAIL_SENDER_EMAIL", "").strip()
    list_unsub = os.getenv("GMAIL_LIST_UNSUBSCRIBE", sender_email)

    async with httpx.AsyncClient() as client:
        access_token = await _refresh_access_token(client)
        if not access_token:
            return GmailSendResult(status="auth_error", error="failed_to_refresh_access_token")

        raw = _build_rfc822(
            sender_name=sender_name,
            sender_email=sender_email,
            to_email=to_email,
            subject=subject,
            body_plain=body_plain,
            reply_to=reply_to,
            list_unsubscribe_email=list_unsub,
        )
        b64 = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

        try:
            r = await client.post(
                GMAIL_SEND_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json={"raw": b64},
                timeout=15.0,
            )
        except Exception as exc:  # noqa: BLE001
            return GmailSendResult(status="http_error", error=str(exc))

    if r.status_code == 200:
        body = r.json() or {}
        return GmailSendResult(status="ok", gmail_message_id=body.get("id"))
    if r.status_code in (429, 403):
        return GmailSendResult(status="quota_exceeded", error=f"HTTP {r.status_code}: {r.text[:300]}")
    return GmailSendResult(status="http_error", error=f"HTTP {r.status_code}: {r.text[:300]}")


@dataclass
class GmailDraftResult:
    status: str  # ok | no_keys | auth_error | http_error
    draft_id: str | None = None
    message_id: str | None = None
    error: str | None = None


async def create_draft(
    *,
    to_email: str,
    subject: str,
    body_plain: str,
    sender_name: str = "Sami | Dealix",
    reply_to: str | None = None,
) -> GmailDraftResult:
    """
    Create a Gmail draft via users.drafts.create. Sami reviews + sends manually.
    Per Gmail API: requires gmail.compose or gmail.modify scope (gmail.send alone
    is insufficient for drafts.create).
    """
    if not is_configured():
        return GmailDraftResult(status="no_keys", error="GMAIL_* env vars not set")

    sender_email = os.getenv("GMAIL_SENDER_EMAIL", "").strip()
    list_unsub = os.getenv("GMAIL_LIST_UNSUBSCRIBE", sender_email)

    async with httpx.AsyncClient() as client:
        access_token = await _refresh_access_token(client)
        if not access_token:
            return GmailDraftResult(status="auth_error", error="failed_to_refresh_access_token")

        raw = _build_rfc822(
            sender_name=sender_name,
            sender_email=sender_email,
            to_email=to_email,
            subject=subject,
            body_plain=body_plain,
            reply_to=reply_to,
            list_unsubscribe_email=list_unsub,
        )
        b64 = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

        try:
            r = await client.post(
                GMAIL_DRAFTS_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json={"message": {"raw": b64}},
                timeout=15.0,
            )
        except Exception as exc:  # noqa: BLE001
            return GmailDraftResult(status="http_error", error=str(exc))

    if r.status_code == 200:
        body = r.json() or {}
        msg = body.get("message") or {}
        return GmailDraftResult(
            status="ok",
            draft_id=body.get("id"),
            message_id=msg.get("id"),
        )
    return GmailDraftResult(status="http_error", error=f"HTTP {r.status_code}: {r.text[:300]}")


# ── OAuth setup helper (Sami runs once locally) ────────────────────
def get_oauth_setup_instructions() -> dict[str, Any]:
    """
    Returns the exact steps Sami follows once to mint a Gmail refresh token.
    Used by /api/v1/email/connect/gmail when keys aren't configured yet.
    """
    return {
        "needed_scope": "https://www.googleapis.com/auth/gmail.compose",
        "steps": [
            "1. Open https://console.cloud.google.com/apis/credentials",
            "2. Create OAuth 2.0 Client ID — type: Desktop app — name: Dealix Gmail Sender",
            "3. Download client_secret.json. Note CLIENT_ID + CLIENT_SECRET.",
            "4. Run on your laptop: pip install google-auth-oauthlib",
            "5. Mint refresh_token via the snippet below — copy the printed refresh_token.",
            "6. In Railway → service web → Variables, add:",
            "     GMAIL_CLIENT_ID=<step 3>",
            "     GMAIL_CLIENT_SECRET=<step 3>",
            "     GMAIL_REFRESH_TOKEN=<step 5>",
            "     GMAIL_SENDER_EMAIL=<your @gmail address>",
            "     GMAIL_LIST_UNSUBSCRIBE=<unsubscribe@yourdomain or same Gmail>",
            "7. Click Review → Deploy.",
            "8. Verify with: GET /api/v1/email/status",
        ],
        "snippet": (
            "from google_auth_oauthlib.flow import InstalledAppFlow\n"
            "flow = InstalledAppFlow.from_client_secrets_file(\n"
            "    'client_secret.json',\n"
            "    scopes=['https://www.googleapis.com/auth/gmail.compose'],\n"
            ")\n"
            "creds = flow.run_local_server(port=0, prompt='consent', access_type='offline')\n"
            "print('REFRESH_TOKEN:', creds.refresh_token)"
        ),
    }
