"""
Expansion prediction — flags customers ready for upsell / cross-sell.

Drivers (positive signals):
  - High health score (>= 75)
  - High engagement growth
  - Hitting plan limits (e.g., quota of leads/month)
  - Multiple sectors targeted
  - Strong pipeline added
  - Good NPS

Output: ExpansionSignal with recommended package + estimated upsell SAR.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ExpansionSignal:
    customer_id: str
    likelihood: float                # 0..1
    recommended_plan: str            # Growth / Scale / Enterprise
    estimated_upsell_sar: float      # additional MRR
    drivers: list[str] = field(default_factory=list)
    pitch_angle_ar: str = ""


def predict_expansion(
    *,
    customer_id: str,
    current_plan: str = "Growth",
    health_score: float = 0,
    monthly_engagement_growth_pct: float = 0,
    sectors_targeted: int = 1,
    pct_of_quota_used: float = 0,    # 0..1 (close to 1 means hitting limits)
    nps: int | None = None,
    pipeline_added_growth_pct: float = 0,
) -> ExpansionSignal:
    """Score expansion likelihood + recommend the next plan."""
    score = 0.0
    drivers: list[str] = []

    if health_score >= 80:
        score += 0.30
        drivers.append("Health score ممتاز")
    elif health_score >= 65:
        score += 0.15

    if monthly_engagement_growth_pct >= 0.30:
        score += 0.20
        drivers.append(f"نمو استخدام {monthly_engagement_growth_pct*100:.0f}%")

    if pct_of_quota_used >= 0.85:
        score += 0.25
        drivers.append("يقترب من حد الباقة")
    elif pct_of_quota_used >= 0.70:
        score += 0.12

    if sectors_targeted >= 3:
        score += 0.10
        drivers.append("يستهدف قطاعات متعددة")

    if nps is not None and nps >= 9:
        score += 0.10
        drivers.append(f"NPS {nps} (promoter)")

    if pipeline_added_growth_pct >= 0.30:
        score += 0.15
        drivers.append("Pipeline ينمو شهرياً")

    score = min(1.0, score)

    # Plan ladder
    plans_order = ["Starter", "Growth", "Scale", "Enterprise"]
    plan_prices = {"Starter": 999, "Growth": 2999, "Scale": 7999, "Enterprise": 15000}
    try:
        idx = plans_order.index(current_plan)
        next_plan = plans_order[min(idx + 1, len(plans_order) - 1)]
    except ValueError:
        next_plan = "Growth"
    upsell_sar = max(0, plan_prices.get(next_plan, 0) - plan_prices.get(current_plan, 0))

    if score >= 0.65:
        pitch = (
            f"العميل ينمو + يقترب من حد الباقة الحالية. ترقية إلى {next_plan} "
            f"تفتح: integrations إضافية، multi-sector، QBR شهري. "
            f"upsell {upsell_sar:,.0f} ريال/شهر."
        )
    elif score >= 0.40:
        pitch = (
            "ركّز على إثبات ROI أولاً عبر Proof Pack — ثم اقترح الترقية في QBR القادم."
        )
    else:
        pitch = "ليس الوقت المناسب — ركّز على retention قبل expansion."

    return ExpansionSignal(
        customer_id=customer_id,
        likelihood=round(score, 3),
        recommended_plan=next_plan if score >= 0.5 else current_plan,
        estimated_upsell_sar=upsell_sar if score >= 0.5 else 0,
        drivers=drivers,
        pitch_angle_ar=pitch,
    )
