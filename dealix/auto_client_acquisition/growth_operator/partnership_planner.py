"""
Partnership Operator — propose partner types + outreach drafts + scorecard.

Keep deterministic; partner suggestions come from a curated catalog
tuned for Saudi B2B (agencies, consultants, integrators, CRM vendors,
founder communities, sector influencers).
"""

from __future__ import annotations

import hashlib
from typing import Any


PARTNER_TYPES: tuple[dict[str, Any], ...] = (
    {
        "key": "marketing_agency",
        "label_ar": "وكالة تسويق B2B",
        "rationale_ar": "لديها عملاء يحتاجون lead-gen — Dealix يكمل خدماتها (لا يستبدلها).",
        "model_ar": "Reseller / Revenue share 20-30%",
        "ideal_size": "10-50 موظف",
    },
    {
        "key": "sales_consultant",
        "label_ar": "مستشار مبيعات / مدرب",
        "rationale_ar": "يحتاج أداة عملية تثبت توصياته للعملاء.",
        "model_ar": "Affiliate fixed fee + ongoing commission",
        "ideal_size": "1-5 موظف",
    },
    {
        "key": "tech_integrator",
        "label_ar": "تكامل تقني / شريك Supabase أو Make.com",
        "rationale_ar": "ينفّذ التكاملات للعملاء الكبار.",
        "model_ar": "Implementation revenue share",
        "ideal_size": "5-20 موظف",
    },
    {
        "key": "crm_vendor",
        "label_ar": "مزود CRM (Zoho/Salla/Odoo سعودي)",
        "rationale_ar": "Dealix طبقة نمو فوق الـ CRM، لا منافس مباشر.",
        "model_ar": "Co-sell + technical alliance",
        "ideal_size": "30+ موظف",
    },
    {
        "key": "founder_community",
        "label_ar": "مجتمع مؤسسين سعوديين",
        "rationale_ar": "الوصول لـ early adopters السعوديين عبر referrals.",
        "model_ar": "Community partnership + free seats",
        "ideal_size": "50+ عضو",
    },
    {
        "key": "sector_influencer",
        "label_ar": "خبير قطاعي (عقار / صحة / لوجستيات)",
        "rationale_ar": "ثقة جاهزة في القطاع تختصر دورة البيع.",
        "model_ar": "Equity / advisory + revenue referral",
        "ideal_size": "1-3 موظف",
    },
)


def suggest_partner_types(
    *,
    sector: str = "",
    customer_size: str = "smb",
) -> dict[str, Any]:
    """Recommend ranked partner types for the given customer profile."""
    suggestions = []
    for p in PARTNER_TYPES:
        priority = 50
        if customer_size == "smb" and p["key"] in ("marketing_agency", "sales_consultant", "founder_community"):
            priority += 25
        if customer_size == "enterprise" and p["key"] in ("crm_vendor", "tech_integrator"):
            priority += 25
        if sector and sector.lower() in ("real_estate", "clinics", "logistics"):
            if p["key"] == "sector_influencer":
                priority += 20
        suggestions.append({**p, "priority": priority})

    suggestions.sort(key=lambda x: x["priority"], reverse=True)
    return {
        "sector": sector,
        "customer_size": customer_size,
        "suggestions": suggestions[:5],
        "next_action": "draft_outreach_for_top_3",
    }


def draft_partner_outreach(
    *,
    partner_type_key: str,
    partner_name: str = "",
    customer_name: str = "Dealix",
) -> dict[str, Any]:
    """Generate a warm partnership outreach draft."""
    pt = next((p for p in PARTNER_TYPES if p["key"] == partner_type_key), None)
    if pt is None:
        return {
            "error": "unknown_partner_type",
            "approval_required": True,
            "approval_status": "pending_approval",
        }

    target = partner_name or pt["label_ar"]
    seed = hashlib.md5(f"{partner_type_key}{partner_name}".encode()).digest()
    angle_idx = seed[0] % 2
    angles_ar = [
        "تكامل خدماتنا يخدم نفس عملائكم بأقل احتكاك.",
        "نموذج revenue share واضح + pilot على عميل واحد قبل الالتزام.",
    ]
    body_ar = (
        f"السلام عليكم،\n\n"
        f"أنا من فريق {customer_name}. تابعنا عملكم ووجدناه قريب جداً من جمهورنا.\n\n"
        f"الفكرة باختصار: {angles_ar[angle_idx]}\n\n"
        f"هل ١٥-٢٠ دقيقة الأسبوع الجاي مناسبة لاستكشاف فرصة شراكة؟"
    )
    return {
        "partner_type": pt,
        "channel_recommendation": "email",
        "body_ar": body_ar,
        "approval_required": True,
        "approval_status": "pending_approval",
        "suggested_next_steps": [
            "1. رسالة warm",
            "2. مكالمة 20 دقيقة",
            "3. عرض partner revenue share",
            "4. pilot على عميل واحد",
        ],
    }


def partner_scorecard(
    *,
    partner_id: str,
    intros_made: int = 0,
    deals_influenced: int = 0,
    revenue_share_paid_sar: float = 0.0,
    relationship_age_months: int = 0,
) -> dict[str, Any]:
    """Compute a simple partner-health scorecard."""
    activity_score = min(100, intros_made * 8 + deals_influenced * 15)
    longevity_bonus = min(20, relationship_age_months * 2)
    overall = min(100, activity_score + longevity_bonus)
    if overall >= 75:
        tier = "platinum"
    elif overall >= 50:
        tier = "gold"
    elif overall >= 25:
        tier = "silver"
    else:
        tier = "bronze"
    return {
        "partner_id": partner_id,
        "overall_score": overall,
        "tier": tier,
        "intros_made": intros_made,
        "deals_influenced": deals_influenced,
        "revenue_share_paid_sar": round(revenue_share_paid_sar, 2),
        "relationship_age_months": relationship_age_months,
        "next_action_ar": (
            "احتفظ بالعلاقة بنشاط ثابت — ربع سنوي." if tier in ("platinum", "gold")
            else "حفّز التفاعل — اقتراح pilot جديد أو إحالة محتملة."
        ),
    }
