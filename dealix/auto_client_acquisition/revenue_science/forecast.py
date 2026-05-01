"""
Revenue Forecast — best / likely / worst over 30/60/90 days.

Each open deal contributes a probability-weighted slice of revenue.
Probabilities come from stage-historical win rates × deal-specific risk.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any


# Stage → base probability of close (calibrated over Pulse cohort)
STAGE_BASE_PROBABILITY: dict[str, float] = {
    "new": 0.05,
    "qualified": 0.15,
    "discovery": 0.25,
    "demo": 0.40,
    "proposal": 0.55,
    "negotiation": 0.70,
    "verbal_yes": 0.85,
    "won": 1.0,
    "lost": 0.0,
}


@dataclass
class ForecastBand:
    """One scenario (best/likely/worst)."""

    label: str            # "best" / "likely" / "worst"
    revenue_sar: float
    n_deals_closing: int
    confidence: float


@dataclass
class Forecast:
    """Full forecast for a customer over a horizon."""

    customer_id: str
    horizon_days: int
    period_label: str
    best: ForecastBand
    likely: ForecastBand
    worst: ForecastBand
    deals_breakdown: list[dict[str, Any]] = field(default_factory=list)
    risks_ar: list[str] = field(default_factory=list)
    decisions_required_ar: list[str] = field(default_factory=list)


def _deal_close_probability(
    *, stage: str, days_in_stage: int, multi_threaded: bool, value_sar: float
) -> float:
    """Compute the probability this specific deal closes within horizon."""
    base = STAGE_BASE_PROBABILITY.get(stage, 0.10)
    # Stalled penalty
    if days_in_stage > 21:
        base *= max(0.3, 1.0 - (days_in_stage - 21) * 0.02)
    # Multi-threaded bonus (multiple decision-makers)
    if multi_threaded:
        base *= 1.15
    # Very large deals are harder
    if value_sar > 500_000:
        base *= 0.85
    return min(0.99, max(0.0, base))


def compute_forecast(
    *,
    customer_id: str,
    open_deals: list[dict[str, Any]],
    horizon_days: int = 30,
    now: datetime | None = None,
) -> Forecast:
    """
    Compute the customer's forecast over the next N days.

    Each deal is dict with: id, stage, value_sar, last_activity_at,
    days_in_stage, multi_threaded, expected_close_at (optional).
    """
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    horizon_end = n + timedelta(days=horizon_days)

    breakdown: list[dict[str, Any]] = []
    expected = 0.0
    best_total = 0.0
    likely_total = 0.0
    worst_total = 0.0
    risks: list[str] = []

    for d in open_deals:
        if d.get("stage") in ("won", "lost"):
            continue
        prob = _deal_close_probability(
            stage=d.get("stage", "new"),
            days_in_stage=d.get("days_in_stage", 0),
            multi_threaded=d.get("multi_threaded", False),
            value_sar=d.get("value_sar", 0),
        )
        value = float(d.get("value_sar", 0))
        breakdown.append({
            "deal_id": d.get("id"),
            "company_name": d.get("company_name", ""),
            "stage": d.get("stage"),
            "value_sar": value,
            "probability": round(prob, 3),
            "expected_value_sar": round(value * prob, 2),
        })
        expected += value * prob
        # Best: optimistic — assume P(close) = min(1, p+0.2)
        best_total += value * min(1.0, prob + 0.2)
        # Likely: expected
        likely_total += value * prob
        # Worst: only deals at p ≥ 0.7 contribute
        if prob >= 0.7:
            worst_total += value * (prob - 0.1)
        if prob < 0.2 and value > 100_000:
            risks.append(
                f"صفقة {d.get('company_name','—')} ({value:,.0f} ريال) احتمالها {prob*100:.0f}% فقط — قد لا تغلق هذا الشهر."
            )
        if d.get("days_in_stage", 0) > 30 and value > 50_000:
            risks.append(
                f"صفقة {d.get('company_name','—')} في نفس المرحلة منذ {d['days_in_stage']} يوم."
            )

    decisions: list[str] = []
    if best_total - likely_total > likely_total * 0.5:
        decisions.append(
            "الفجوة بين best و likely كبيرة — حدد الـ 2-3 صفقات الأهم وركّز عليها."
        )
    if not breakdown:
        decisions.append("لا صفقات مفتوحة — ابدأ Daily Growth Run الآن لبناء pipeline.")

    return Forecast(
        customer_id=customer_id,
        horizon_days=horizon_days,
        period_label=f"{n.date()} → {horizon_end.date()}",
        best=ForecastBand(
            label="best",
            revenue_sar=round(best_total, 2),
            n_deals_closing=sum(1 for b in breakdown if b["probability"] >= 0.5),
            confidence=0.5,
        ),
        likely=ForecastBand(
            label="likely",
            revenue_sar=round(likely_total, 2),
            n_deals_closing=sum(1 for b in breakdown if b["probability"] >= 0.4),
            confidence=0.7,
        ),
        worst=ForecastBand(
            label="worst",
            revenue_sar=round(worst_total, 2),
            n_deals_closing=sum(1 for b in breakdown if b["probability"] >= 0.7),
            confidence=0.85,
        ),
        deals_breakdown=breakdown,
        risks_ar=risks[:5],
        decisions_required_ar=decisions,
    )
