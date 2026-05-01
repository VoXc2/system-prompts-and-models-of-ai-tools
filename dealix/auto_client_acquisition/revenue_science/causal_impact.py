"""
Causal Impact Simulator — "what if I changed X, what would change?"

The user adjusts knobs (response time, follow-up cadence, sector focus,
channel mix), Dealix projects the delta in pipeline / meetings / revenue
based on Pulse benchmarks + historical lift coefficients.

This is the engine behind the Revenue Impact Simulator dashboard widget.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Historical lift coefficients (calibrated from pilot data + Pulse)
RESPONSE_TIME_LIFT_PER_HOUR_REDUCTION = 0.014  # +1.4% reply per hour faster
FOLLOWUP_LIFT_PER_EXTRA_TOUCH = 0.025          # +2.5% reply per extra follow-up (cap 3)
WHATSAPP_VS_EMAIL_LIFT = 1.6                   # WhatsApp gets 1.6x reply rate vs email in B2B Saudi
SECTOR_FOCUS_LIFT_PER_SECTOR_DROPPED = 0.04    # +4% conversion per sector you stop chasing


@dataclass
class ImpactScenario:
    """Result of one simulation: baseline vs scenario, delta."""

    scenario_name: str
    baseline_revenue_sar: float
    scenario_revenue_sar: float
    delta_sar: float
    delta_pct: float
    explanation_ar: str
    confidence: float
    risk_warnings_ar: list[str] = field(default_factory=list)


def simulate_impact(
    *,
    current_baseline_revenue_sar: float,
    response_time_reduction_hours: float = 0,
    extra_followup_touches: int = 0,
    shift_to_whatsapp_pct: float = 0,           # 0..1 fraction shifted from email
    drop_n_sectors: int = 0,
    scenario_name: str = "scenario_1",
) -> ImpactScenario:
    """
    Project incremental revenue from a set of operational changes.

    Each lever is applied multiplicatively to the baseline revenue.
    Returns the new total + delta + explanation.
    """
    multiplier = 1.0
    explanation_parts: list[str] = []

    if response_time_reduction_hours > 0:
        lift = response_time_reduction_hours * RESPONSE_TIME_LIFT_PER_HOUR_REDUCTION
        multiplier *= 1 + lift
        explanation_parts.append(
            f"تقليل وقت الرد {response_time_reduction_hours} ساعة → +{lift*100:.1f}% إيراد"
        )

    if extra_followup_touches > 0:
        capped = min(extra_followup_touches, 3)
        lift = capped * FOLLOWUP_LIFT_PER_EXTRA_TOUCH
        multiplier *= 1 + lift
        explanation_parts.append(
            f"+{capped} متابعة إضافية → +{lift*100:.1f}% إيراد"
        )

    if shift_to_whatsapp_pct > 0:
        # Shifting from email to WhatsApp: each shifted % gets 1.6x reply rate
        # Approx incremental lift = shift_pct × (WHATSAPP_VS_EMAIL_LIFT - 1) × 0.4 (conversion factor)
        lift = shift_to_whatsapp_pct * (WHATSAPP_VS_EMAIL_LIFT - 1) * 0.4
        multiplier *= 1 + lift
        explanation_parts.append(
            f"تحويل {shift_to_whatsapp_pct*100:.0f}% للـ WhatsApp → +{lift*100:.1f}% إيراد"
        )

    if drop_n_sectors > 0:
        lift = drop_n_sectors * SECTOR_FOCUS_LIFT_PER_SECTOR_DROPPED
        multiplier *= 1 + lift
        explanation_parts.append(
            f"التخلي عن {drop_n_sectors} قطاع أقل → +{lift*100:.1f}% إيراد"
        )

    new_revenue = current_baseline_revenue_sar * multiplier
    delta = new_revenue - current_baseline_revenue_sar
    delta_pct = (multiplier - 1) * 100

    explanation = (
        "السيناريو لن يحدث فرقاً قابلاً للقياس."
        if not explanation_parts
        else " · ".join(explanation_parts)
    )

    # Confidence drops as cumulative lift exceeds 50% (less reliable extrapolation)
    confidence = max(0.4, 1.0 - max(0, multiplier - 1) * 1.2)

    risks: list[str] = []
    if shift_to_whatsapp_pct > 0.7:
        risks.append("تحويل 70%+ للـ WhatsApp قد يخلق opt-out مرتفع — اختبر تدريجياً.")
    if drop_n_sectors > 3:
        risks.append("التخلي عن 3+ قطاعات يحد TAM — تأكد من concentration risk.")
    if extra_followup_touches > 5:
        risks.append("5+ متابعات قد تُعتبر spam — احرص على تنويع القنوات.")
    if multiplier > 2.0:
        risks.append("الـ uplift المقترح كبير جداً (2x+). اختبر السيناريو على عينة محدودة أولاً.")

    return ImpactScenario(
        scenario_name=scenario_name,
        baseline_revenue_sar=current_baseline_revenue_sar,
        scenario_revenue_sar=round(new_revenue, 2),
        delta_sar=round(delta, 2),
        delta_pct=round(delta_pct, 2),
        explanation_ar=explanation,
        confidence=round(confidence, 3),
        risk_warnings_ar=risks,
    )
