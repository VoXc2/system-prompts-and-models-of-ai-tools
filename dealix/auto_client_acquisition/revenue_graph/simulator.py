"""
Client Acquisition Simulator — pre-purchase ROI calculator.

A prospect enters their sector / city / deal size / target / current close rate,
and gets back an honest projection: how many leads they need, how many
meetings, how many months to hit their goal, recommended plan, expected ROI.

Used on /landing/simulator.html and inside onboarding to set realistic
expectations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ── Sector benchmark constants — anchored from Pulse data ─────────
SECTOR_BENCHMARKS: dict[str, dict[str, float]] = {
    "real_estate":    {"reply_rate": 0.074, "meeting_rate": 0.32, "win_rate": 0.18, "cycle_days": 45},
    "clinics":        {"reply_rate": 0.138, "meeting_rate": 0.40, "win_rate": 0.28, "cycle_days": 28},
    "logistics":      {"reply_rate": 0.068, "meeting_rate": 0.30, "win_rate": 0.22, "cycle_days": 35},
    "hospitality":    {"reply_rate": 0.124, "meeting_rate": 0.38, "win_rate": 0.24, "cycle_days": 30},
    "restaurants":    {"reply_rate": 0.115, "meeting_rate": 0.42, "win_rate": 0.30, "cycle_days": 21},
    "training":       {"reply_rate": 0.112, "meeting_rate": 0.36, "win_rate": 0.25, "cycle_days": 35},
    "agencies":       {"reply_rate": 0.059, "meeting_rate": 0.28, "win_rate": 0.20, "cycle_days": 45},
    "construction":   {"reply_rate": 0.032, "meeting_rate": 0.25, "win_rate": 0.15, "cycle_days": 90},
    "saas":           {"reply_rate": 0.047, "meeting_rate": 0.30, "win_rate": 0.20, "cycle_days": 60},
    "events":         {"reply_rate": 0.153, "meeting_rate": 0.45, "win_rate": 0.35, "cycle_days": 18},
}

# Multiplier for Dealix lift (validated from pilot data)
DEALIX_LIFT_MULTIPLIERS: dict[str, float] = {
    "reply_rate": 2.4,
    "meeting_rate": 1.4,
    "win_rate": 1.2,
}


@dataclass
class SimulatorInputs:
    sector: str
    city: str
    avg_deal_value_sar: float
    target_revenue_sar: float
    target_period_days: int = 90
    current_close_rate: float | None = None  # if known
    current_monthly_meetings: int = 0


@dataclass
class FunnelProjection:
    """Forward-projected funnel for the requested period."""

    leads_needed: int
    replies_expected: int
    meetings_expected: int
    proposals_expected: int
    deals_won_expected: int
    revenue_expected_sar: float
    cycle_days_avg: float
    confidence_band_low: float
    confidence_band_high: float


@dataclass
class PlanRecommendation:
    plan_name: str             # Starter / Growth / Scale
    monthly_price_sar: float
    fits_target: bool
    expected_payback_months: float
    rationale_ar: str


@dataclass
class SimulatorResult:
    inputs: SimulatorInputs
    baseline: FunnelProjection
    with_dealix: FunnelProjection
    plan: PlanRecommendation
    expected_roi_x: float
    risks_ar: list[str] = field(default_factory=list)
    assumptions_ar: list[str] = field(default_factory=list)


def _compute_funnel(
    *,
    inputs: SimulatorInputs,
    bench: dict[str, float],
    with_dealix: bool,
) -> FunnelProjection:
    reply = bench["reply_rate"] * (DEALIX_LIFT_MULTIPLIERS["reply_rate"] if with_dealix else 1.0)
    meet = bench["meeting_rate"] * (DEALIX_LIFT_MULTIPLIERS["meeting_rate"] if with_dealix else 1.0)
    win = bench["win_rate"] * (DEALIX_LIFT_MULTIPLIERS["win_rate"] if with_dealix else 1.0)

    deals_needed = max(1, round(inputs.target_revenue_sar / inputs.avg_deal_value_sar))
    proposals_needed = round(deals_needed / max(0.05, win))
    meetings_needed = round(proposals_needed / max(0.10, meet))
    replies_needed = round(meetings_needed * 1.6)
    leads_needed = round(replies_needed / max(0.005, reply))

    band = 0.25  # ±25% confidence interval
    revenue_expected = deals_needed * inputs.avg_deal_value_sar
    return FunnelProjection(
        leads_needed=leads_needed,
        replies_expected=replies_needed,
        meetings_expected=meetings_needed,
        proposals_expected=proposals_needed,
        deals_won_expected=deals_needed,
        revenue_expected_sar=revenue_expected,
        cycle_days_avg=bench["cycle_days"] * (0.8 if with_dealix else 1.0),
        confidence_band_low=revenue_expected * (1 - band),
        confidence_band_high=revenue_expected * (1 + band),
    )


def _recommend_plan(*, inputs: SimulatorInputs, with_dealix: FunnelProjection) -> PlanRecommendation:
    monthly_revenue = with_dealix.revenue_expected_sar / max(1, inputs.target_period_days / 30)

    if inputs.avg_deal_value_sar < 5000 or with_dealix.leads_needed < 200:
        plan = PlanRecommendation(
            plan_name="Starter",
            monthly_price_sar=999,
            fits_target=monthly_revenue > 999 * 3,
            expected_payback_months=999 / max(1, monthly_revenue) * 12,
            rationale_ar=(
                "حجم الصفقات وعدد الـ leads المطلوبة يناسب باقة Starter — "
                "تبدأ بسرعة + ترفّع لاحقاً."
            ),
        )
    elif inputs.avg_deal_value_sar < 50000 or with_dealix.leads_needed < 1000:
        plan = PlanRecommendation(
            plan_name="Growth",
            monthly_price_sar=2999,
            fits_target=monthly_revenue > 2999 * 3,
            expected_payback_months=2999 / max(1, monthly_revenue) * 12,
            rationale_ar=(
                "الباقة الأنسب — autopilot discovery + WhatsApp chain + "
                "AI personalization + monthly proof pack."
            ),
        )
    else:
        plan = PlanRecommendation(
            plan_name="Scale",
            monthly_price_sar=7999,
            fits_target=monthly_revenue > 7999 * 3,
            expected_payback_months=7999 / max(1, monthly_revenue) * 12,
            rationale_ar=(
                "صفقات كبيرة + multi-sector + integrations + customer success — "
                "Scale هو المسار الصحيح."
            ),
        )
    return plan


def simulate(*, inputs: SimulatorInputs) -> SimulatorResult:
    """Run the full simulation and return everything for the result page."""
    bench = SECTOR_BENCHMARKS.get(
        inputs.sector,
        # Default = SaaS-ish moderate benchmark
        {"reply_rate": 0.05, "meeting_rate": 0.30, "win_rate": 0.20, "cycle_days": 45},
    )
    if inputs.current_close_rate is not None:
        bench = dict(bench)
        bench["win_rate"] = inputs.current_close_rate

    baseline = _compute_funnel(inputs=inputs, bench=bench, with_dealix=False)
    with_dx = _compute_funnel(inputs=inputs, bench=bench, with_dealix=True)
    plan = _recommend_plan(inputs=inputs, with_dealix=with_dx)

    # ROI: revenue achieved with Dealix vs cost of Dealix.
    # Both funnels produce the same deal count (since deals_needed is derived
    # from the target), so we measure ROI as full-revenue / total-cost — i.e.,
    # how many multiples of the Dealix plan does the achieved revenue cover.
    months = max(1.0, inputs.target_period_days / 30)
    cost = plan.monthly_price_sar * months
    roi_x = round(with_dx.revenue_expected_sar / cost, 2) if cost else 0

    risks = []
    if inputs.target_period_days < 30:
        risks.append("الفترة قصيرة جداً (<30 يوم) — توقع رؤية النتائج بعد 45-60 يوم.")
    if inputs.avg_deal_value_sar < 1000:
        risks.append("صفقة بأقل من 1,000 ريال — تأكد من unit economics قبل الاستثمار.")
    if with_dx.leads_needed > 5000:
        risks.append(f"تحتاج {with_dx.leads_needed:,} lead — ابني capacity الفريق أولاً.")

    assumptions = [
        f"benchmark القطاع ({inputs.sector}) من Saudi B2B Pulse — ربع سنوي.",
        "Dealix lift متوسط 2.4× في الـ reply rate (مبني على pilot data).",
        f"متوسط الدورة: {with_dx.cycle_days_avg:.0f} يوم — قد تختلف حسب حجم الشركة.",
        "الأرقام indicative — ليست ضمان قانوني.",
    ]

    return SimulatorResult(
        inputs=inputs,
        baseline=baseline,
        with_dealix=with_dx,
        plan=plan,
        expected_roi_x=roi_x,
        risks_ar=risks,
        assumptions_ar=assumptions,
    )
