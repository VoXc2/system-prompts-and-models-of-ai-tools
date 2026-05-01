"""
Consent Ledger — append-only record of every consent / opt-out under PDPL.

Every contact has a chain of records. The latest record determines the
current state. Lawful basis (PDPL Article 5) is captured with each consent.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ── Lawful bases (PDPL Article 5 / Art. 6 of equivalent regimes) ─
class LawfulBasis:
    CONSENT = "consent"                          # Explicit user consent
    LEGITIMATE_INTEREST = "legitimate_interest"  # B2B research / outreach
    CONTRACT = "contract"                        # Required to perform a contract
    LEGAL_OBLIGATION = "legal_obligation"        # Required by law
    PUBLIC_INTEREST = "public_interest"          # Limited use cases
    VITAL_INTEREST = "vital_interest"            # Emergencies


ALL_BASES: tuple[str, ...] = (
    LawfulBasis.CONSENT,
    LawfulBasis.LEGITIMATE_INTEREST,
    LawfulBasis.CONTRACT,
    LawfulBasis.LEGAL_OBLIGATION,
    LawfulBasis.PUBLIC_INTEREST,
    LawfulBasis.VITAL_INTEREST,
)


@dataclass
class ConsentRecord:
    """One row in the ledger."""

    record_id: str
    customer_id: str
    contact_id: str            # the data subject
    record_type: str           # "consent_granted" | "opt_out" | "lawful_basis_set"
    lawful_basis: str | None
    purpose: str               # what we're doing with the data
    channel: str | None        # which channel(s) — email/whatsapp/all
    source: str                # public_directory / form_submission / explicit_email / api
    occurred_at: datetime
    expires_at: datetime | None = None  # consent can have a term
    proof_url: str | None = None        # link to the original consent capture
    metadata: dict[str, Any] = field(default_factory=dict)


def _new_id() -> str:
    return f"cons_{uuid.uuid4().hex[:24]}"


def record_consent(
    *,
    customer_id: str,
    contact_id: str,
    lawful_basis: str,
    purpose: str,
    channel: str | None = None,
    source: str = "explicit_email",
    expires_at: datetime | None = None,
    proof_url: str | None = None,
    occurred_at: datetime | None = None,
) -> ConsentRecord:
    if lawful_basis not in ALL_BASES:
        raise ValueError(f"unknown lawful_basis: {lawful_basis}")
    return ConsentRecord(
        record_id=_new_id(),
        customer_id=customer_id,
        contact_id=contact_id,
        record_type="consent_granted",
        lawful_basis=lawful_basis,
        purpose=purpose,
        channel=channel,
        source=source,
        occurred_at=occurred_at or datetime.now(timezone.utc).replace(tzinfo=None),
        expires_at=expires_at,
        proof_url=proof_url,
    )


def record_opt_out(
    *,
    customer_id: str,
    contact_id: str,
    channel: str | None = None,
    source: str = "list_unsubscribe_header",
    occurred_at: datetime | None = None,
) -> ConsentRecord:
    """Opt-out is permanent. The latest opt-out always overrides earlier consents."""
    return ConsentRecord(
        record_id=_new_id(),
        customer_id=customer_id,
        contact_id=contact_id,
        record_type="opt_out",
        lawful_basis=None,
        purpose="opt_out_request",
        channel=channel,
        source=source,
        occurred_at=occurred_at or datetime.now(timezone.utc).replace(tzinfo=None),
    )


def latest_state(records: list[ConsentRecord]) -> dict[str, Any]:
    """
    Compute the current consent state from the ledger:
      - has_consent: bool
      - is_opted_out: bool
      - lawful_basis: str | None
      - last_recorded_at: datetime | None
    """
    if not records:
        return {
            "has_consent": False,
            "is_opted_out": False,
            "lawful_basis": None,
            "last_recorded_at": None,
        }
    by_recent = sorted(records, key=lambda r: r.occurred_at, reverse=True)
    # Opt-out is permanent — if any opt-out exists, the contact is opted out
    if any(r.record_type == "opt_out" for r in records):
        last_opt_out = max(
            (r for r in records if r.record_type == "opt_out"),
            key=lambda r: r.occurred_at,
        )
        return {
            "has_consent": False,
            "is_opted_out": True,
            "lawful_basis": None,
            "last_recorded_at": last_opt_out.occurred_at,
        }
    latest = by_recent[0]
    n = datetime.now(timezone.utc).replace(tzinfo=None)
    expired = bool(latest.expires_at and latest.expires_at < n)
    return {
        "has_consent": latest.record_type == "consent_granted" and not expired,
        "is_opted_out": False,
        "lawful_basis": latest.lawful_basis if not expired else None,
        "last_recorded_at": latest.occurred_at,
    }
