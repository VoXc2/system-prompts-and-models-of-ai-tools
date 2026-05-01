"""Opportunity Simulator — forward simulation before sending."""

from __future__ import annotations

from typing import Any


# Sector benchmarks (anchored to Saudi B2B Pulse figures)
SECTOR_RATES: dict[str, dict[str, float]] = {
    "real_estate":  {"reply": 0.074, "meeting": 0.32, "win": 0.18},
    "clinics":      {"reply": 0.138, "meeting": 0.40, "win": 0.28},
    "logistics":    {"reply": 0.068, "meeting": 0.30, "win": 0.22},
    "hospitality":  {"reply": 0.124, "meeting": 0.38, "win": 0.24},
    "restaurants":  {"reply": 0.115, "meeting": 0.42, "win": 0.30},
    "training":     {"reply": 0.112, "meeting": 0.36, "win": 0.25},
    "agencies":     {"reply": 0.059, "meeting": 0.28, "win": 0.20},
    "construction": {"reply": 0.032, "meeting": 0.25, "win": 0.15},
    "saas":         {"reply": 0.047, "meeting": 0.30, "win": 0.20},
}


def simulate_opportunity(
    *,
    target_count: int,
    sector: str = "saas",
    avg_deal_value_sar: float = 25_000,
    channel: str = "whatsapp",
    cold_pct: float = 0.0,
    quality_lift: float = 1.0,    # multiplier (Dealix lift on baseline)
) -> dict[str, Any]:
    """
    Forward-simulate a campaign before launching.

    Returns expected replies / meetings / pipeline + risk flags.
    """
    rates = SECTOR_RATES.get(sector.lower(), SECTOR_RATES["saas"])

    # Channel adjustment
    if channel == "whatsapp":
        reply_rate = rates["reply"] * 1.6 * quality_lift
    elif channel == "email":
        reply_rate = rates["reply"] * 0.9 * quality_lift
    else:
        reply_rate = rates["reply"] * quality_lift

    # Cold contacts hurt the rate dramatically
    cold_pct = max(0.0, min(1.0, cold_pct))
    if cold_pct > 0:
        reply_rate *= max(0.10, 1.0 - cold_pct * 0.85)

    expected_replies = round(target_count * reply_rate)
    expected_meetings = round(expected_replies * rates["meeting"])
    expected_deals = round(expected_meetings * rates["win"])
    expected_pipeline = expected_deals * avg_deal_value_sar

    # Risk flags
    risks: list[str] = []
    if cold_pct >= 0.5:
        risks.append("نسبة cold عالية — احتمال opt-out مرتفع.")
    if channel == "whatsapp" and cold_pct > 0:
        risks.append("WhatsApp + cold = خطر PDPL — راجع الـ contactability.")
    if target_count > 500 and channel == "whatsapp":
        risks.append("حملة WhatsApp كبيرة — اعتمد على templates معتمدة.")

    risk_score = min(100, int(50 + cold_pct * 50 + (10 if target_count > 500 else 0)))

    return {
        "inputs": {
            "target_count": target_count,
            "sector": sector,
            "avg_deal_value_sar": avg_deal_value_sar,
            "channel": channel,
            "cold_pct": cold_pct,
            "quality_lift": quality_lift,
        },
        "rates_used": rates,
        "expected_replies": expected_replies,
        "expected_meetings": expected_meetings,
        "expected_deals": expected_deals,
        "expected_pipeline_sar": expected_pipeline,
        "risk_score": risk_score,
        "risks_ar": risks,
        "recommendation_ar": (
            "ابدأ بالـ safe-only segment + معدّل أسبوعي محدود."
            if risk_score >= 50
            else "آمن للإطلاق بعد approval."
        ),
        "approval_required": True,
    }
