"""
Vertical OS Base — schema for productized sector modules.

Each vertical bundles: ICP, signals, objections, KPIs, message library,
proposal template, QBR template, ROI model, compliance notes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ── KPI definition ────────────────────────────────────────────────
@dataclass(frozen=True)
class KPI:
    metric_id: str
    name_ar: str
    description_ar: str
    unit: str
    higher_is_better: bool = True
    target_p50: float | None = None  # sector benchmark
    target_p90: float | None = None


# ── Message template ─────────────────────────────────────────────
@dataclass(frozen=True)
class MessageTemplate:
    template_id: str
    channel: str               # whatsapp / email / linkedin
    purpose: str               # cold / followup_3d / followup_7d / objection_response
    subject_ar: str | None
    body_ar: str
    variables: tuple[str, ...] = ()  # {company_name}, {city}, {pain_point}, etc.
    expected_reply_rate: float = 0.0


# ── Full vertical bundle ─────────────────────────────────────────
@dataclass(frozen=True)
class VerticalOS:
    vertical_id: str
    sector_ar: str
    sector_en: str

    # ICP
    icp_company_size: tuple[str, ...]
    icp_cities: tuple[str, ...]
    icp_keywords: tuple[str, ...]

    # Pain & objections
    pain_points_ar: tuple[str, ...]
    top_objection_ids: tuple[str, ...]   # ids from revenue_graph.objection_library

    # Signals to watch (from market_intelligence.signal_detectors taxonomy)
    priority_signals: tuple[str, ...]

    # KPIs surfaced on the per-vertical dashboard
    dashboard_kpis: tuple[KPI, ...]

    # Message library
    message_templates: tuple[MessageTemplate, ...]

    # Proposal & QBR templates
    proposal_template_ar: str
    qbr_section_template_ar: str

    # ROI model — what to plug into the simulator
    avg_deal_value_sar: int
    avg_cycle_days: int
    benchmark_reply_rate: float
    benchmark_meeting_rate: float
    benchmark_win_rate: float

    # Compliance notes specific to the sector
    compliance_notes_ar: tuple[str, ...] = ()

    # Recommended channel mix (must sum ~ 1.0)
    recommended_channel_mix: dict[str, float] = field(default_factory=dict)


# ── Registry helpers ─────────────────────────────────────────────
_REGISTRY: dict[str, VerticalOS] = {}


def _register(v: VerticalOS) -> None:
    _REGISTRY[v.vertical_id] = v


def get_vertical(vertical_id: str) -> VerticalOS | None:
    return _REGISTRY.get(vertical_id)


def list_vertical_summaries() -> list[dict[str, Any]]:
    """Compact summary for the verticals overview tile."""
    return [
        {
            "vertical_id": v.vertical_id,
            "sector_ar": v.sector_ar,
            "sector_en": v.sector_en,
            "avg_deal_value_sar": v.avg_deal_value_sar,
            "avg_cycle_days": v.avg_cycle_days,
            "n_pain_points": len(v.pain_points_ar),
            "n_message_templates": len(v.message_templates),
            "n_kpis": len(v.dashboard_kpis),
            "primary_channel": (
                max(v.recommended_channel_mix.items(), key=lambda x: x[1])[0]
                if v.recommended_channel_mix else None
            ),
            "benchmark_reply_rate": v.benchmark_reply_rate,
        }
        for v in _REGISTRY.values()
    ]


# Will be populated by clinics.py / real_estate.py / logistics.py imports
ALL_VERTICALS: dict[str, VerticalOS] = _REGISTRY
