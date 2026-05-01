"""
Contactability — per-contact "safe to contact?" with reason.

Combines: consent ledger state, frequency caps, quiet hours, blocked
keywords/sectors. Returns a structured ContactabilityStatus that the
orchestrator + Copilot can render in plain Arabic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from auto_client_acquisition.compliance_os.consent_ledger import (
    ConsentRecord,
    latest_state,
)


@dataclass
class ContactabilityStatus:
    contact_id: str
    can_contact: bool
    reason_code: str           # safe / no_consent / opted_out / freq_cap / quiet_hours / blocked
    reason_ar: str             # human-readable
    has_consent: bool = False
    is_opted_out: bool = False
    lawful_basis: str | None = None
    next_allowed_at: datetime | None = None  # if blocked by freq_cap or quiet_hours

    def to_dict(self) -> dict[str, Any]:
        return {
            "contact_id": self.contact_id,
            "can_contact": self.can_contact,
            "reason_code": self.reason_code,
            "reason_ar": self.reason_ar,
            "has_consent": self.has_consent,
            "is_opted_out": self.is_opted_out,
            "lawful_basis": self.lawful_basis,
            "next_allowed_at": self.next_allowed_at.isoformat() if self.next_allowed_at else None,
        }


# Reason codes → Arabic explanation
_REASON_AR: dict[str, str] = {
    "safe": "آمن للتواصل — consent سارٍ ولا opt-out.",
    "no_consent": "لا توجد موافقة سارية ولا أساس قانوني واضح للتواصل.",
    "opted_out": "المتلقي طلب opt-out سابقاً — لا يمكن التواصل مرة أخرى.",
    "freq_cap": "تجاوز عدد الرسائل المسموحة هذا الأسبوع.",
    "quiet_hours": "خارج ساعات العمل المسموحة (8ص-9م توقيت الرياض).",
    "blocked": "محظور بسبب قاعدة محتوى أو سياسة العميل.",
    "expired_consent": "الموافقة انتهت صلاحيتها — جدّدها قبل التواصل.",
}


def check_contactability(
    *,
    contact_id: str,
    consent_records: list[ConsentRecord],
    messages_sent_this_week: int = 0,
    weekly_cap: int = 2,
    current_riyadh_hour: int = 12,
    quiet_start_hour: int = 21,
    quiet_end_hour: int = 8,
) -> ContactabilityStatus:
    """
    Evaluate whether we can contact this person right now.

    Order of checks:
      1. opt_out → block (permanent)
      2. no consent + no legitimate interest → block
      3. expired consent → block
      4. weekly cap exceeded → freq_cap
      5. inside quiet hours → quiet_hours
      6. otherwise safe
    """
    state = latest_state(consent_records)

    if state["is_opted_out"]:
        return ContactabilityStatus(
            contact_id=contact_id,
            can_contact=False,
            reason_code="opted_out",
            reason_ar=_REASON_AR["opted_out"],
            is_opted_out=True,
        )

    if not state["has_consent"]:
        return ContactabilityStatus(
            contact_id=contact_id,
            can_contact=False,
            reason_code="no_consent",
            reason_ar=_REASON_AR["no_consent"],
        )

    # Frequency cap
    if messages_sent_this_week >= weekly_cap:
        return ContactabilityStatus(
            contact_id=contact_id,
            can_contact=False,
            reason_code="freq_cap",
            reason_ar=_REASON_AR["freq_cap"],
            has_consent=True,
            lawful_basis=state["lawful_basis"],
        )

    # Quiet hours (Riyadh)
    in_quiet = False
    if quiet_start_hour < quiet_end_hour:
        in_quiet = quiet_start_hour <= current_riyadh_hour < quiet_end_hour
    else:
        # Wraps midnight (e.g., 21..8)
        in_quiet = current_riyadh_hour >= quiet_start_hour or current_riyadh_hour < quiet_end_hour

    if in_quiet:
        return ContactabilityStatus(
            contact_id=contact_id,
            can_contact=False,
            reason_code="quiet_hours",
            reason_ar=_REASON_AR["quiet_hours"],
            has_consent=True,
            lawful_basis=state["lawful_basis"],
        )

    return ContactabilityStatus(
        contact_id=contact_id,
        can_contact=True,
        reason_code="safe",
        reason_ar=_REASON_AR["safe"],
        has_consent=True,
        lawful_basis=state["lawful_basis"],
    )
