"""
Compliance gate — runs BEFORE every email send.

Returns a `ComplianceCheck` with allowed:bool + blocked_reason. Caller MUST
honor allowed=False. Used by:
- /api/v1/email/send-approved
- /api/v1/email/send-batch
- the daily targeting auto-pilot
- the follow-up engine

Hard rules (PDPL + Gmail bulk-sender guidelines):
- Suppression hits → blocked
- opt_out=True on contact → blocked
- bounced before → blocked
- email format invalid → blocked
- risk_score > 50 → blocked
- allowed_use missing/unknown → blocked
- daily-limit hit → blocked (rate)
- batch-size limit hit → blocked (rate)
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import Any

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PERSONAL_DOMAINS = {"gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "icloud.com", "live.com"}
DAILY_DEFAULT = 50
BATCH_DEFAULT = 10
INTERVAL_MIN_DEFAULT = 90


@dataclass
class ComplianceCheck:
    allowed: bool
    blocked_reasons: list[str]
    risk_score: float
    requires_human_review: bool
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def check_outreach(
    *,
    to_email: str | None,
    contact_opt_out: bool = False,
    risk_score: float = 0.0,
    allowed_use: str | None = None,
    suppression_emails: set[str] | None = None,
    suppression_domains: set[str] | None = None,
    suppression_phones: set[str] | None = None,
    bounced_before: bool = False,
    sent_today_count: int = 0,
    sent_in_current_batch: int = 0,
    seconds_since_last_batch: float | None = None,
    is_partner_warm: bool = False,
) -> ComplianceCheck:
    """
    Run the compliance gate on a single outbound candidate.

    All inputs are explicit — no env reads inside (so it's testable in pure unit tests).
    Daily/batch limits read from env at endpoint level then passed in here.
    """
    reasons: list[str] = []
    notes: list[str] = []
    requires_review = False

    # 1. Email shape
    if not to_email:
        reasons.append("no_recipient_email")
    elif not EMAIL_RE.match(to_email):
        reasons.append("invalid_email_format")

    # 2. Opt-out + suppression
    if contact_opt_out:
        reasons.append("contact_opt_out_true")
    if to_email and suppression_emails and to_email.lower() in suppression_emails:
        reasons.append("email_suppressed")
    if to_email:
        domain = to_email.split("@", 1)[1].lower() if "@" in to_email else ""
        if suppression_domains and domain in suppression_domains:
            reasons.append("domain_suppressed")
        if domain in PERSONAL_DOMAINS and not is_partner_warm:
            # Personal domain → demote to manual review unless explicitly partner-warm
            requires_review = True
            notes.append("personal_email_domain_review_required")

    # 3. Bounce history
    if bounced_before:
        reasons.append("bounced_before")

    # 4. Risk score
    if risk_score > 50:
        reasons.append(f"risk_score_too_high:{risk_score:.0f}")

    # 5. Allowed use
    if not allowed_use or allowed_use in {"unknown", "", None}:
        reasons.append("allowed_use_missing")

    # 6. Rate limits
    if sent_today_count >= DAILY_DEFAULT:
        reasons.append(f"daily_limit_hit:{sent_today_count}/{DAILY_DEFAULT}")
    if sent_in_current_batch >= BATCH_DEFAULT:
        reasons.append(f"batch_size_hit:{sent_in_current_batch}/{BATCH_DEFAULT}")
    if seconds_since_last_batch is not None and seconds_since_last_batch < (INTERVAL_MIN_DEFAULT * 60):
        wait_s = (INTERVAL_MIN_DEFAULT * 60) - seconds_since_last_batch
        reasons.append(f"batch_cooldown:{int(wait_s)}s_remaining")

    return ComplianceCheck(
        allowed=(len(reasons) == 0 and not requires_review),
        blocked_reasons=reasons,
        risk_score=risk_score,
        requires_human_review=requires_review,
        notes=notes,
    )


# ── Email body formatter — adds opt-out line ──────────────────────
def append_opt_out_line(body: str) -> str:
    """
    Required by Gmail bulk-sender guidelines: every cold email must include an
    obvious opt-out mechanism. Caller MUST use this before sending.
    """
    if "STOP" in body or "OPT OUT" in body or "إيقاف" in body or "إلغاء الاستلام" in body:
        return body  # already present
    return body.rstrip() + (
        "\n\n— لإلغاء الاستلام، ردّ بـ STOP أو OPT OUT. "
        "To unsubscribe, reply STOP."
    )


# ── Limits from env (server-side helpers) ─────────────────────────
def get_daily_limit() -> int:
    try:
        return int(os.getenv("DAILY_EMAIL_LIMIT", str(DAILY_DEFAULT)))
    except ValueError:
        return DAILY_DEFAULT


def get_batch_size() -> int:
    try:
        return int(os.getenv("EMAIL_BATCH_SIZE", str(BATCH_DEFAULT)))
    except ValueError:
        return BATCH_DEFAULT


def get_batch_interval_seconds() -> int:
    try:
        return int(os.getenv("EMAIL_BATCH_INTERVAL_MINUTES", str(INTERVAL_MIN_DEFAULT))) * 60
    except ValueError:
        return INTERVAL_MIN_DEFAULT * 60
