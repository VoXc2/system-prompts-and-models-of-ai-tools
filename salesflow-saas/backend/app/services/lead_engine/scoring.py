"""Weighted scoring — dimensions 0-100, explainable reason codes."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.models.lead import Lead


def _clamp(n: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, n))


def compute_lead_dimensions(lead: Lead, icp_slug: str, meta: Dict[str, Any]) -> Tuple[int, str, Dict[str, float], List[str]]:
    """
    Returns: total_score 0-100, priority_band, dimension_scores, reason_codes.
    """
    reasons: List[str] = []
    d: Dict[str, float] = {}

    # ICP fit (from sector keywords + slug match)
    sector = (lead.source or "") + " " + str(meta.get("sector", ""))
    icp_fit = 55.0
    if icp_slug and any(k in sector.lower() for k in ("google", "maps", "website", "referral")):
        icp_fit += 10.0
        reasons.append("icp_source_positive")
    d["icp_fit"] = _clamp(icp_fit)

    # Intent (from status + metadata)
    intent = 45.0
    st = (lead.status or "new").lower()
    if st in ("qualified", "proposal"):
        intent += 25.0
        reasons.append("intent_pipeline_stage")
    if meta.get("urgency"):
        intent += 15.0
        reasons.append("intent_metadata_urgency")
    d["intent"] = _clamp(intent)

    # Geography (Saudi signals)
    geo = 60.0
    city = str(meta.get("city", "") or "")
    if any(c in city for c in ("Riyadh", "الرياض", "Jeddah", "جدة")):
        geo += 15.0
        reasons.append("geo_tier1_city")
    d["geo"] = _clamp(geo)

    # Data quality / accessibility
    dq = 40.0
    if lead.phone:
        dq += 25.0
        reasons.append("has_phone")
    if lead.email:
        dq += 15.0
        reasons.append("has_email")
    d["data_quality"] = _clamp(dq)

    # Revenue potential (heuristic from notes length / score field)
    rev = float(lead.score or 50)
    d["revenue_potential"] = _clamp(rev)

    # Strategic / expansion
    strat = 50.0
    if "enterprise" in str(meta).lower():
        strat += 20.0
        reasons.append("enterprise_signal")
    d["strategic"] = _clamp(strat)

    weights = {
        "icp_fit": 0.18,
        "intent": 0.22,
        "geo": 0.12,
        "data_quality": 0.15,
        "revenue_potential": 0.18,
        "strategic": 0.15,
    }
    total = sum(d.get(k, 50.0) * weights[k] for k in weights)
    total_i = int(round(_clamp(total, 0, 100)))

    if total_i >= 85:
        band = "P0"
    elif total_i >= 70:
        band = "P1"
    elif total_i >= 50:
        band = "P2"
    elif total_i >= 30:
        band = "P3"
    else:
        band = "reject"

    return total_i, band, d, reasons


def priority_to_motion(band: str, meta: Dict[str, Any]) -> str:
    if band in ("reject", "P3"):
        return "nurture"
    if meta.get("enterprise"):
        return "abm"
    if band == "P0":
        return "whatsapp_first"
    return "sdr_outbound"
