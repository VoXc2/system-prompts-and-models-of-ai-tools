"""
Intake Agent — captures leads from multiple sources and normalizes them.
وكيل الاستقبال — يلتقط العملاء من مصادر متعددة ويوحّد صيغتهم.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from core.agents.base import BaseAgent
from core.utils import (
    detect_locale,
    generate_id,
    hash_text,
    normalize_email,
    normalize_phone,
    utcnow,
)


class LeadSource(StrEnum):
    """Lead source channels | مصادر العملاء."""

    WEBSITE = "website"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    REFERRAL = "referral"
    LINKEDIN = "linkedin"
    COLD_OUTREACH = "cold_outreach"
    MANUAL = "manual"
    API = "api"


class LeadStatus(StrEnum):
    """Lead stages through the funnel | مراحل العميل في القمع."""

    NEW = "new"
    QUALIFIED = "qualified"
    DISCOVERY = "discovery"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"
    DISQUALIFIED = "disqualified"


@dataclass
class Lead:
    """A captured lead | عميل محتمل ملتقط."""

    id: str
    source: LeadSource
    company_name: str = ""
    contact_name: str = ""
    contact_email: str | None = None
    contact_phone: str | None = None
    contact_channel: str = ""
    sector: str | None = None
    company_size: str | None = None
    region: str | None = None
    budget: float | None = None
    message: str | None = None
    urgency_score: float = 0.0
    fit_score: float = 0.0
    status: LeadStatus = LeadStatus.NEW
    pain_points: list[str] = field(default_factory=list)
    locale: str = "ar"
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    dedup_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage / API response."""
        return {
            "id": self.id,
            "source": self.source.value,
            "company_name": self.company_name,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "contact_channel": self.contact_channel,
            "sector": self.sector,
            "company_size": self.company_size,
            "region": self.region,
            "budget": self.budget,
            "message": self.message,
            "urgency_score": self.urgency_score,
            "fit_score": self.fit_score,
            "status": self.status.value,
            "pain_points": self.pain_points,
            "locale": self.locale,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "dedup_hash": self.dedup_hash,
        }


class IntakeAgent(BaseAgent):
    """
    Receives raw lead payloads and produces normalized Lead objects.
    Does: validation, phone/email normalization, locale detection, dedup hashing.
    """

    name = "intake"

    def __init__(self) -> None:
        super().__init__()
        self._seen_hashes: set[str] = set()

    async def run(
        self,
        *,
        payload: dict[str, Any],
        source: LeadSource | str = LeadSource.WEBSITE,
        **_: Any,
    ) -> Lead:
        """Normalize a raw payload into a Lead."""
        if isinstance(source, str):
            source = LeadSource(source)

        company = str(payload.get("company") or payload.get("company_name") or "").strip()
        name = str(payload.get("name") or payload.get("contact_name") or "").strip()
        email = normalize_email(str(payload.get("email") or ""))
        phone = normalize_phone(str(payload.get("phone") or ""))
        message = str(payload.get("message") or "").strip() or None
        locale = str(payload.get("locale") or "").strip()
        if not locale:
            locale = detect_locale(message or company or name)

        contact_channel = email or phone or str(payload.get("channel") or source.value)

        # Dedup based on (email or phone) + company
        dedup_source = f"{email or phone or ''}|{company.lower()}"
        dedup_hash = hash_text(dedup_source) if dedup_source.strip("|") else ""
        is_duplicate = dedup_hash and dedup_hash in self._seen_hashes
        if dedup_hash:
            self._seen_hashes.add(dedup_hash)

        lead = Lead(
            id=generate_id("lead"),
            source=source,
            company_name=company,
            contact_name=name,
            contact_email=email,
            contact_phone=phone,
            contact_channel=contact_channel,
            sector=payload.get("sector"),
            company_size=payload.get("company_size"),
            region=payload.get("region"),
            budget=self._parse_float(payload.get("budget")),
            message=message,
            status=LeadStatus.NEW,
            locale=locale,
            dedup_hash=dedup_hash,
            metadata={
                "is_duplicate": is_duplicate,
                "raw_payload": payload,
            },
        )

        self.log.info(
            "lead_intake",
            lead_id=lead.id,
            source=source.value,
            company=company,
            duplicate=is_duplicate,
        )
        return lead

    @staticmethod
    def _parse_float(value: Any) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
