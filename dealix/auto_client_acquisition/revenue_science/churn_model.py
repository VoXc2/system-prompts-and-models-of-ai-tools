"""
Churn prediction — flags customers likely to churn within 60 days.

Inputs are signals from the Revenue Memory + Customer Success layer:
  - days_since_last_login
  - drop in monthly engagement
  - support ticket spike
  - billing issues
  - low NPS
  - drop in pipeline added by Dealix

Each signal gets a weight; the composite score is mapped to a band.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChurnPrediction:
    customer_id: str
    score: float                      # 0..1 — higher = more likely to churn
    band: str                         # safe / watch / at_risk / critical
    drivers: list[str] = field(default_factory=list)
    recommended_action_ar: str = ""
    confidence: float = 0.7


def predict_churn(
    *,
    customer_id: str,
    days_since_last_login: int = 0,
    monthly_engagement_drop_pct: float = 0,    # 0..1 (drop vs prior month)
    support_tickets_open: int = 0,
    billing_failures_last_90d: int = 0,
    nps: int | None = None,
    pipeline_added_drop_pct: float = 0,        # 0..1 (drop vs prior month)
    months_as_customer: int = 6,
) -> ChurnPrediction:
    """
    Compute churn probability + drivers + recommendation.

    Weights tuned to the early-pilot cohort. As more data flows in,
    these can be re-fit by the AI Quality module.
    """
    score = 0.0
    drivers: list[str] = []

    # Engagement: huge weight
    if days_since_last_login > 30:
        score += 0.35
        drivers.append(f"لم يدخل المنتج منذ {days_since_last_login} يوم")
    elif days_since_last_login > 14:
        score += 0.20
        drivers.append(f"دخوله متباعد ({days_since_last_login} يوم)")

    if monthly_engagement_drop_pct > 0.5:
        score += 0.20
        drivers.append(f"انخفاض الاستخدام {monthly_engagement_drop_pct*100:.0f}%")
    elif monthly_engagement_drop_pct > 0.3:
        score += 0.10

    # Support tickets
    if support_tickets_open >= 3:
        score += 0.15
        drivers.append(f"{support_tickets_open} تذاكر دعم مفتوحة")
    elif support_tickets_open >= 1:
        score += 0.05

    # Billing
    if billing_failures_last_90d >= 2:
        score += 0.15
        drivers.append("فشل في الدفع متكرر")
    elif billing_failures_last_90d >= 1:
        score += 0.07

    # NPS
    if nps is not None:
        if nps <= 6:
            score += 0.20
            drivers.append(f"NPS منخفض ({nps})")
        elif nps == 7:
            score += 0.05

    # Outcome — Dealix's job
    if pipeline_added_drop_pct > 0.5:
        score += 0.15
        drivers.append("Dealix لا يجلب pipeline كما كان")
    elif pipeline_added_drop_pct > 0.3:
        score += 0.07

    # New customers cushion: <3 months gets a -0.1 because honeymoon
    if months_as_customer < 3:
        score = max(0, score - 0.10)

    score = min(1.0, score)

    if score >= 0.65:
        band = "critical"
        action = "اتصل بالعميل اليوم. أعرض QBR + offer to extend pilot. هذا يكلف $0 إذا أنقذناه."
    elif score >= 0.45:
        band = "at_risk"
        action = "حدد call مع decision-maker. أرسل Proof Pack + roadmap للنصف القادم."
    elif score >= 0.25:
        band = "watch"
        action = "راقب أسبوعياً + أرسل insights مخصصة. لا تدخل عاجل."
    else:
        band = "safe"
        action = "صحي — فكّر في expansion / upsell."

    confidence = 0.6 if len(drivers) <= 1 else min(0.95, 0.6 + len(drivers) * 0.07)

    return ChurnPrediction(
        customer_id=customer_id,
        score=round(score, 3),
        band=band,
        drivers=drivers,
        recommended_action_ar=action,
        confidence=round(confidence, 3),
    )
