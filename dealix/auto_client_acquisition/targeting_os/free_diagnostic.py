"""Free Growth Diagnostic — العرض المجاني الذي يجلب pilots."""

from __future__ import annotations

from typing import Any

from .account_finder import recommend_accounts
from .contact_source_policy import classify_source
from .contactability_matrix import evaluate_contactability


def build_free_growth_diagnostic(
    company_profile: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a free 5-section Arabic growth diagnostic for a prospect.

    Inputs: company_profile = {sector, city, offer, goal, has_list?, channels?}
    Outputs: 3 opportunities + 1 message + 1 risk + 1 mini proof plan + paid pilot offer.
    """
    sector = company_profile.get("sector", "saas")
    city = company_profile.get("city", "Riyadh")
    offer = company_profile.get("offer", "")

    accounts = recommend_accounts(
        sector=sector, city=city, offer=offer, goal="diagnostic", limit=3,
    )["accounts"]

    sample_message = (
        f"هلا، لاحظت توسعكم في قطاع {sector}. "
        "نشتغل على Dealix كمدير نمو عربي للشركات السعودية. "
        "خلال 7 أيام نطلع لكم 10 فرص B2B + رسائل + خطة متابعة. "
        "يناسبكم ديمو 12 دقيقة هذا الأسبوع؟"
    )

    risk_summary = {
        "label_ar": "احتمال إضرار سمعة الـdomain أو رقم واتساب",
        "why_ar": (
            "لو أرسلت لقائمة بدون opt-in، تتجاوز PDPL ويمكن أن تُحظر القناة. "
            "الحل: ابدأ بمصادر آمنة فقط."
        ),
        "mitigation_ar": [
            "صنّف كل contact حسب المصدر.",
            "أوقف أي رقم بدون opt-in.",
            "ابدأ بـ Free Diagnostic ثم Pilot.",
        ],
    }

    mini_proof = build_mini_proof_plan()

    return {
        "company_profile": {"sector": sector, "city": city, "offer": offer},
        "delivered_at": "draft",
        "approval_required": True,
        "sections": {
            "opportunities_ar": accounts,
            "sample_message_ar": sample_message,
            "risk_summary_ar": risk_summary,
            "mini_proof_plan_ar": mini_proof,
            "paid_pilot_offer": recommend_paid_pilot_offer({"sector": sector}),
        },
        "next_step_ar": (
            "إذا أعجبتك العينة، نكمل Pilot 7 أيام بـ499 ريال "
            "أو مجاناً مقابل case study بعد انتهاء الـPilot."
        ),
    }


def analyze_uploaded_list_preview(
    contacts: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Preview-only analysis of a customer-uploaded list.

    Classifies sources + contactability without storing. Returns aggregate.
    """
    if not contacts:
        return {"total": 0, "by_status": {}, "preview": []}

    by_status: dict[str, int] = {"safe": 0, "needs_review": 0, "blocked": 0}
    preview: list[dict[str, Any]] = []

    for i, c in enumerate(contacts[:20]):  # only first 20 for preview
        verdict = evaluate_contactability(c)
        status = verdict["status"]
        by_status[status] = by_status.get(status, 0) + 1
        preview.append({
            "index": i,
            "source": classify_source(c.get("source", "unknown_source"))["source"],
            "contactability": status,
            "allowed_channels": verdict.get("allowed_channels", []),
        })

    # Aggregate over the FULL list
    full_by_status = dict(by_status)
    if len(contacts) > 20:
        # Project remaining proportionally — deterministic.
        scale = len(contacts) / 20
        full_by_status = {k: int(v * scale) for k, v in by_status.items()}

    return {
        "total": len(contacts),
        "by_status": full_by_status,
        "preview": preview,
        "recommendations_ar": [
            "ابدأ بالـsafe contacts فقط في الأسبوع الأول.",
            "راجع الـneeds_review يدوياً قبل أي إرسال.",
            "تخطّ الـblocked تماماً (opt-out).",
        ],
    }


def recommend_paid_pilot_offer(diagnostic: dict[str, Any]) -> dict[str, Any]:
    """Recommend a paid Pilot offer based on diagnostic context."""
    return {
        "offer_id": "first_10_opportunities_pilot_7d",
        "name_ar": "Pilot 7 أيام: 10 فرص + رسائل + متابعة + Proof Pack",
        "price_sar_min": 499,
        "price_sar_max": 1500,
        "free_alternative_ar": "مجاني مقابل case study بعد انتهاء الـPilot.",
        "deliverables_ar": [
            "10 فرص B2B مع why-now.",
            "10 رسائل عربية جاهزة.",
            "خطة متابعة 7 أيام.",
            "Proof Pack تفصيلي.",
        ],
        "approval_required": True,
    }


def build_mini_proof_plan() -> dict[str, Any]:
    """A small Proof Pack template anyone can run in their head."""
    return {
        "metrics_to_track": [
            "leads_created",
            "drafts_approved",
            "positive_replies",
            "meetings_drafted",
            "pipeline_influenced_sar",
            "risks_blocked",
        ],
        "how_to_count_ar": (
            "كل metric يُحسب يومياً عبر Proof Ledger. "
            "في نهاية الأسبوع، نولّد PDF/JSON ونشاركه مع الإدارة."
        ),
        "review_frequency": "weekly",
    }
