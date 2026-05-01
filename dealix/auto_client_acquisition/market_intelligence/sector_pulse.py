"""
Sector Pulse Builder — aggregates signals into sector-level momentum.

Outputs a SectorPulse object: how many active signals, trend direction,
top signal types, recommended sales angle for the week.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from auto_client_acquisition.market_intelligence.signal_detectors import SignalDetection


@dataclass
class SectorPulse:
    """Per-sector momentum snapshot."""

    sector: str
    week_label: str
    active_signals: int
    n_companies_with_signals: int
    trend: str                        # rising / steady / cooling
    pct_change_vs_prior_week: float
    top_signal_types: list[tuple[str, int]]
    recommended_angle_ar: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "sector": self.sector,
            "week_label": self.week_label,
            "active_signals": self.active_signals,
            "n_companies_with_signals": self.n_companies_with_signals,
            "trend": self.trend,
            "pct_change_vs_prior_week": self.pct_change_vs_prior_week,
            "top_signal_types": [
                {"type": t, "count": c} for t, c in self.top_signal_types
            ],
            "recommended_angle_ar": self.recommended_angle_ar,
        }


# Heuristic sales angles per top signal in each sector
_ANGLES: dict[str, dict[str, str]] = {
    "real_estate": {
        "hiring_sales_rep": "تسليم 50 lead مؤهل في 60 يوم — قبل ramp-up الموظف الجديد.",
        "new_branch_opened": "60 يوم. 50 lead. اجتماع أسبوعياً. مضمون.",
        "tender_published": "ملف pre-qualification + 5 موردين بدائل قبل deadline.",
        "ads_volume_increased": "نقطّع CAC الحالي بنسبة 35%.",
    },
    "clinics": {
        "whatsapp_business_added": "نوصل WhatsApp Business بـ Dealix — كل رسالة تتحول إلى حجز.",
        "booking_page_added": "نملأ صفحة الحجز بـ leads مؤهلة + reminder ينقص no-show 40%.",
        "new_service_launched": "Go-to-market 30 يوم: 100 patient lead لخدمتكم الجديدة.",
    },
    "logistics": {
        "tender_published": "نسلم pre-qualification + 5 موردين بدائل قبل deadline.",
        "hiring_sales_rep": "نقطّع زمن الـ quote من 3 أيام إلى ساعة — 100 RFQ مؤهل شهرياً.",
    },
    # Generic fallback
    "_default": {
        "_default": "تجربة 30 يوم — تدفع فقط على الـ qualified leads.",
    },
}


def _angle_for(sector: str, top_signal: str) -> str:
    sector_angles = _ANGLES.get(sector, {})
    if top_signal in sector_angles:
        return sector_angles[top_signal]
    if "_default" in sector_angles:
        return sector_angles["_default"]
    return _ANGLES["_default"]["_default"]


def build_sector_pulse(
    *,
    sector: str,
    signals_this_week: list[SignalDetection],
    signals_prior_week: list[SignalDetection],
    week_label: str = "",
) -> SectorPulse:
    """Build a sector pulse from this and prior week's signals."""
    types_count: dict[str, int] = defaultdict(int)
    companies = set()
    for s in signals_this_week:
        types_count[s.signal_type] += 1
        companies.add(s.company_id)
    n_this = len(signals_this_week)
    n_prior = len(signals_prior_week) or 1
    pct = round((n_this / n_prior - 1) * 100, 1) if n_prior else 0.0

    trend = "steady"
    if pct >= 15:
        trend = "rising"
    elif pct <= -15:
        trend = "cooling"

    top = sorted(types_count.items(), key=lambda x: -x[1])[:3]
    top_signal = top[0][0] if top else ""
    angle = _angle_for(sector, top_signal)

    return SectorPulse(
        sector=sector,
        week_label=week_label or datetime.now(timezone.utc).strftime("%Y-W%U"),
        active_signals=n_this,
        n_companies_with_signals=len(companies),
        trend=trend,
        pct_change_vs_prior_week=pct,
        top_signal_types=top,
        recommended_angle_ar=angle,
    )


def rank_hot_sectors(
    *,
    pulses: list[SectorPulse],
    top_n: int = 5,
) -> list[SectorPulse]:
    """Sort sectors by trend strength × volume — for the radar dashboard."""
    def score(p: SectorPulse) -> float:
        trend_w = {"rising": 1.0, "steady": 0.5, "cooling": 0.1}.get(p.trend, 0.3)
        return (p.active_signals * 0.6 + p.n_companies_with_signals * 0.4) * trend_w
    return sorted(pulses, key=score, reverse=True)[:top_n]
