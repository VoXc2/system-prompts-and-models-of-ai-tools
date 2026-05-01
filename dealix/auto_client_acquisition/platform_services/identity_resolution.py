"""
Identity Resolution — reconcile signals from many channels into one Identity.

Inputs: phone, email, company, social handles, CRM ids.
Output: a single Identity record with confidence per matched signal.

Pure deterministic — production version would hit a graph DB.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Identity:
    """A reconciled identity across channels."""

    identity_id: str
    primary_phone: str | None = None
    primary_email: str | None = None
    company: str | None = None
    crm_id: str | None = None
    social_handles: dict[str, str] = field(default_factory=dict)
    confidence: float = 0.0           # 0..1
    sources: list[str] = field(default_factory=list)


def _hash_id(*parts: str) -> str:
    """Deterministic ID from any combination of stable identifiers."""
    seed = "|".join(p.lower().strip() for p in parts if p)
    if not seed:
        return ""
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"id_{h}"


def resolve_identity(*, signals: list[dict[str, Any]]) -> Identity:
    """
    Merge a list of signals (from different channels) into one Identity.

    Each signal can be: {phone, email, company, crm_id, social_handles, source}.
    """
    phones: dict[str, int] = {}
    emails: dict[str, int] = {}
    companies: dict[str, int] = {}
    crm_ids: list[str] = []
    socials: dict[str, str] = {}
    sources: list[str] = []

    for s in signals:
        ph = (s.get("phone") or "").strip()
        em = (s.get("email") or "").strip().lower()
        co = (s.get("company") or "").strip()
        crm = (s.get("crm_id") or "").strip()
        if ph:
            phones[ph] = phones.get(ph, 0) + 1
        if em:
            emails[em] = emails.get(em, 0) + 1
        if co:
            companies[co] = companies.get(co, 0) + 1
        if crm:
            crm_ids.append(crm)
        for k, v in (s.get("social_handles") or {}).items():
            if k not in socials and v:
                socials[k] = v
        if s.get("source"):
            sources.append(str(s["source"]))

    # Pick most-frequent canonical values
    primary_phone = max(phones, key=phones.get) if phones else None
    primary_email = max(emails, key=emails.get) if emails else None
    company = max(companies, key=companies.get) if companies else None
    crm_id = crm_ids[0] if crm_ids else None

    # Confidence: proportional to number of independent strong signals
    strong_signals = sum(1 for x in (primary_phone, primary_email, crm_id) if x)
    confidence = min(1.0, 0.30 * strong_signals + 0.10 * (1 if socials else 0))

    return Identity(
        identity_id=_hash_id(primary_phone or "", primary_email or "", crm_id or ""),
        primary_phone=primary_phone,
        primary_email=primary_email,
        company=company,
        crm_id=crm_id,
        social_handles=dict(socials),
        confidence=round(confidence, 3),
        sources=list(dict.fromkeys(sources)),  # dedupe preserve order
    )
