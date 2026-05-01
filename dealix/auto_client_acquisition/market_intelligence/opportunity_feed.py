"""
Opportunity Feed — the unified "act-now" stream the dashboard reads.

Combines: detected signals + sector pulse + city heat + ICP match score
into prioritized Opportunity rows with rationale.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from auto_client_acquisition.market_intelligence.signal_detectors import SignalDetection


@dataclass
class Opportunity:
    """A specific company × signal × angle ready for action."""

    company_id: str
    company_name: str
    sector: str
    city: str
    priority_score: float           # 0..100
    primary_signal: str
    why_now_ar: str
    suggested_angle_ar: str
    suggested_channel: str          # whatsapp / email / linkedin / phone
    estimated_deal_value_sar: float
    confidence: float               # 0..1

    def to_dict(self) -> dict[str, Any]:
        return {
            "company_id": self.company_id,
            "company_name": self.company_name,
            "sector": self.sector,
            "city": self.city,
            "priority_score": self.priority_score,
            "primary_signal": self.primary_signal,
            "why_now_ar": self.why_now_ar,
            "suggested_angle_ar": self.suggested_angle_ar,
            "suggested_channel": self.suggested_channel,
            "estimated_deal_value_sar": self.estimated_deal_value_sar,
            "confidence": self.confidence,
        }


# Channel preference per sector (matches sector_playbooks recommendations)
_DEFAULT_CHANNEL_BY_SECTOR: dict[str, str] = {
    "real_estate": "whatsapp",
    "clinics": "whatsapp",
    "logistics": "email",
    "hospitality": "email",
    "restaurants": "whatsapp",
    "training": "linkedin",
    "agencies": "email",
    "construction": "email",
}


def build_opportunity_feed(
    *,
    signals: list[SignalDetection],
    company_metadata: dict[str, dict[str, Any]],
    why_now_explainer,            # callable(company_id, signals, sector, trend) → WhyNowExplanation|None
    sector_trends: dict[str, str] | None = None,
    top_n: int = 20,
) -> list[Opportunity]:
    """
    Roll up signals into ranked opportunities.

    `why_now_explainer` is injected (revenue_graph.why_now.explain_why_now)
    so this module stays decoupled from that one.
    """
    sector_trends = sector_trends or {}
    by_company: dict[str, list[SignalDetection]] = {}
    for s in signals:
        by_company.setdefault(s.company_id, []).append(s)

    opps: list[Opportunity] = []
    for company_id, sigs in by_company.items():
        meta = company_metadata.get(company_id) or {}
        sector = meta.get("sector", "saas")
        city = meta.get("city", "—")
        explanation = why_now_explainer(
            company_id=company_id,
            signals=sigs,
            sector=sector,
            sector_pulse_trend=sector_trends.get(sector),
        )
        if explanation is None:
            continue
        primary = explanation.primary_signals[0] if explanation.primary_signals else ""
        channel = _DEFAULT_CHANNEL_BY_SECTOR.get(sector, "email")
        opps.append(Opportunity(
            company_id=company_id,
            company_name=meta.get("name", company_id),
            sector=sector,
            city=city,
            priority_score=explanation.score,
            primary_signal=primary,
            why_now_ar=explanation.headline_ar,
            suggested_angle_ar=explanation.suggested_angle_ar,
            suggested_channel=channel,
            estimated_deal_value_sar=meta.get("estimated_deal_value_sar", 25000),
            confidence=min(1.0, sum(s.confidence for s in sigs) / max(1, len(sigs))),
        ))
    opps.sort(key=lambda o: o.priority_score, reverse=True)
    return opps[:top_n]
