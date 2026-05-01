"""Pricing tiers, plan recommendation, performance fees, ROI estimates."""

from __future__ import annotations

from typing import Any, Literal

PlanKey = Literal[
    "founder_operator",
    "growth_os",
    "scale_os",
    "performance_addon",
    "enterprise",
    "agency_partner",
]


def get_pricing_tiers() -> dict[str, Any]:
    """Product packaging aligned with docs/PRICING_STRATEGY.md (SAR/month unless noted)."""
    return {
        "currency": "SAR",
        "tiers": [
            {
                "key": "founder_operator",
                "name_ar": "مشغّل المؤسس",
                "target": "solo founders / early B2B startups",
                "price_monthly_sar_range": [299, 499],
                "price_future_sar": 999,
                "includes": [
                    "Arabic daily brief",
                    "20 strategic opportunities / month",
                    "project memory (local + Supabase path)",
                    "draft messages (approval-first)",
                    "launch readiness",
                    "limited market radar",
                ],
            },
            {
                "key": "growth_os",
                "name_ar": "نظام النمو",
                "target": "B2B SMEs",
                "price_monthly_sar": 2999,
                "includes": [
                    "Revenue Command Center",
                    "Market Radar",
                    "500 prospects / month (enrichment cap — policy)",
                    "AI message drafts",
                    "WhatsApp approval flow",
                    "Gmail draft",
                    "meeting schedule drafts",
                    "weekly proof pack",
                ],
            },
            {
                "key": "scale_os",
                "name_ar": "نظام التوسّع",
                "target": "mature B2B teams",
                "price_monthly_sar": 7999,
                "includes": [
                    "multi-seat",
                    "team performance",
                    "customer success signals",
                    "churn / expansion scoring",
                    "integrations",
                    "advanced analytics",
                    "API / webhooks",
                ],
            },
            {
                "key": "performance_addon",
                "name_ar": "طبقة الأداء",
                "target": "optional add-on",
                "fee_qualified_lead_sar_range": [25, 75],
                "fee_booked_meeting_sar_range": [150, 500],
                "success_fee_pct_range": [3, 10],
                "notes": ["Strict qualification + dispute logic required before billing."],
            },
            {
                "key": "enterprise",
                "name_ar": "المؤسسات / نشر خاص",
                "target": "enterprise",
                "pricing": "custom",
                "includes": ["SSO", "advanced PDPL", "custom integrations", "dedicated success", "private data", "SLA"],
            },
            {
                "key": "agency_partner",
                "name_ar": "شراكة وكالات",
                "setup_fee_sar_range": [3000, 25000],
                "revenue_share_pct_range": [15, 30],
                "notes": ["Dealix keeps platform subscription; agency sells implementation."],
            },
        ],
    }


def recommend_plan(
    *,
    company_size: str,
    monthly_budget_sar: float,
    goal: str,
) -> dict[str, Any]:
    """Heuristic plan recommendation — deterministic rules."""
    size = company_size.lower().strip()
    goal_l = goal.lower()
    recommended: PlanKey = "founder_operator"
    rationale_ar = "ميزانية محدودة أو مرحلة مبكرة — ابدأ بمشغّل المؤسس للتحقق السريع."

    if monthly_budget_sar >= 6500 or size in ("large", "enterprise", "scale"):
        recommended = "scale_os"
        rationale_ar = "فريق ناضج أو ميزانية عالية — Scale OS يلائم التنسيق متعدد المقاعد والتحليلات."
    elif monthly_budget_sar >= 2000 or size in ("sme", "medium", "growth"):
        recommended = "growth_os"
        rationale_ar = "شركة B2B نامية — Growth OS يوازن بين الرادار والتنفيذ الآمن ودليل العائد."

    if "performance" in goal_l or "pay per" in goal_l:
        rationale_ar += " أضف طبقة الأداء لاحقاً بعد تعريف التأهيل والنزاعات."

    tiers = get_pricing_tiers()
    tier = next((t for t in tiers["tiers"] if t["key"] == recommended), tiers["tiers"][0])
    return {
        "recommended_plan": recommended,
        "rationale_ar": rationale_ar,
        "tier_summary": tier,
        "inputs": {"company_size": company_size, "monthly_budget_sar": monthly_budget_sar, "goal": goal},
    }


def calculate_performance_fee(
    *,
    qualified_leads: int,
    booked_meetings: int,
    won_revenue_sar: float,
    lead_fee_sar: float = 40.0,
    meeting_fee_sar: float = 250.0,
    success_fee_pct: float = 5.0,
) -> dict[str, Any]:
    """Demo calculation — real contracts need legal + qualification definitions."""
    lead_component = max(0, qualified_leads) * lead_fee_sar
    meeting_component = max(0, booked_meetings) * meeting_fee_sar
    success_component = max(0.0, won_revenue_sar) * (success_fee_pct / 100.0)
    total = round(lead_component + meeting_component + success_component, 2)
    return {
        "qualified_leads": qualified_leads,
        "booked_meetings": booked_meetings,
        "won_revenue_sar": won_revenue_sar,
        "components_sar": {
            "leads": round(lead_component, 2),
            "meetings": round(meeting_component, 2),
            "success": round(success_component, 2),
        },
        "total_performance_fees_sar": total,
        "disclaimer_ar": "يجب ربط أي رسوم أداء بعقود وتأهيل واضح وتتبع نزاعات قبل الفوترة.",
    }


def estimate_roi(
    *,
    plan_price_sar: float,
    expected_pipeline_sar: float,
    expected_revenue_sar: float,
) -> dict[str, Any]:
    """Simple ROI framing — not financial advice."""
    if plan_price_sar <= 0:
        return {"error": "plan_price_must_be_positive"}
    pipeline_multiple = round(expected_pipeline_sar / plan_price_sar, 2) if plan_price_sar else 0.0
    revenue_multiple = round(expected_revenue_sar / plan_price_sar, 2) if plan_price_sar else 0.0
    return {
        "plan_price_sar": plan_price_sar,
        "expected_pipeline_sar": expected_pipeline_sar,
        "expected_revenue_sar": expected_revenue_sar,
        "pipeline_to_subscription_multiple": pipeline_multiple,
        "revenue_to_subscription_multiple": revenue_multiple,
        "verdict_ar": "إذا تعدت المضاعفات 3–5x على الأنابيب المتوقع، يصير الاشتراك منطقياً مع تتبع أسبوعي.",
    }
