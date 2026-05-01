"""
Enrichment Agent — augments lead data with public info.
وكيل الإثراء — يثري بيانات العميل من مصادر عامة.

Note: production enrichment typically uses providers like Clearbit, Apollo,
or company-domain lookups. This agent provides:
1. Domain-based inference (guess company size / sector from email domain)
2. LLM-based inference from company name (best effort)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from auto_client_acquisition.agents.intake import Lead
from core.agents.base import BaseAgent
from core.config.models import Task
from core.llm.base import Message


@dataclass
class EnrichmentData:
    inferred_sector: str | None = None
    inferred_size: str | None = None
    inferred_region: str | None = None
    website: str | None = None
    linkedin_handle: str | None = None
    notes: list[str] = field(default_factory=list)
    confidence: float = 0.0  # 0-1

    def to_dict(self) -> dict[str, Any]:
        return {
            "inferred_sector": self.inferred_sector,
            "inferred_size": self.inferred_size,
            "inferred_region": self.inferred_region,
            "website": self.website,
            "linkedin_handle": self.linkedin_handle,
            "notes": self.notes,
            "confidence": round(self.confidence, 2),
        }


# Domain → sector hints (extend as needed)
DOMAIN_HINTS: dict[str, str] = {
    ".edu.sa": "education",
    ".gov.sa": "government",
    ".med.sa": "healthcare",
    "aramco.com": "oil_gas",
    "sabic.com": "manufacturing",
    "stc.com.sa": "technology",
    "alrajhibank.com.sa": "finance",
    "saudiairlines.com": "tourism",
}


class EnrichmentAgent(BaseAgent):
    """Enriches lead data using heuristics + LLM inference."""

    name = "enrichment"

    async def run(
        self,
        *,
        lead: Lead,
        use_llm: bool = True,
        **_: Any,
    ) -> EnrichmentData:
        data = EnrichmentData()
        confidence = 0.0

        # 1. Email-domain hints
        if lead.contact_email and "@" in lead.contact_email:
            domain = lead.contact_email.split("@", 1)[1].lower()
            data.website = f"https://{domain}"
            for key, sector in DOMAIN_HINTS.items():
                if key in domain:
                    data.inferred_sector = sector
                    confidence = max(confidence, 0.8)
                    data.notes.append(f"Sector from domain: {domain} → {sector}")
                    break
            if domain.endswith(".sa") or domain.endswith(".ksa"):
                data.inferred_region = "Saudi Arabia"
                confidence = max(confidence, 0.7)

        # 2. Phone country hint
        if lead.contact_phone and lead.contact_phone.startswith("+966"):
            data.inferred_region = data.inferred_region or "Saudi Arabia"
            confidence = max(confidence, 0.7)
        elif lead.contact_phone and lead.contact_phone.startswith("+971"):
            data.inferred_region = data.inferred_region or "UAE"
            confidence = max(confidence, 0.7)

        # 3. LLM inference from company name
        if use_llm and lead.company_name and not data.inferred_sector:
            try:
                prompt = (
                    f"Given the Saudi/GCC company name '{lead.company_name}', "
                    f"infer the most likely sector from this list: "
                    f"technology, real_estate, healthcare, education, logistics, "
                    f"retail, finance, manufacturing, consulting, construction, "
                    f"oil_gas, tourism, other. "
                    f'Respond with JSON: {{"sector": str, "confidence": 0-1, "note": str}}. '
                    f"If you don't know, say 'other' with low confidence."
                )
                response = await self.router.run(
                    task=Task.CLASSIFICATION,
                    messages=[Message(role="user", content=prompt)],
                    max_tokens=200,
                    temperature=0.1,
                )
                parsed = self.parse_json_response(response.content)
                if parsed.get("sector") and parsed["sector"] != "other":
                    data.inferred_sector = parsed["sector"]
                    confidence = max(confidence, float(parsed.get("confidence", 0.3)))
                    data.notes.append(f"Sector from name: {lead.company_name} → {parsed['sector']}")
            except Exception as e:
                self.log.warning("enrichment_llm_failed", error=str(e))

        data.confidence = confidence
        self.log.info(
            "enriched",
            lead_id=lead.id,
            sector=data.inferred_sector,
            region=data.inferred_region,
            confidence=confidence,
        )
        return data
