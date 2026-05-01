"""Vertical service map — which services to recommend per industry vertical."""

from __future__ import annotations

from typing import Any

# 6 verticals × recommended service stack.
VERTICALS_AR: dict[str, dict[str, Any]] = {
    "b2b_saas": {
        "label_ar": "B2B SaaS",
        "primary_services": [
            "first_10_opportunities_sprint",
            "linkedin_lead_gen_setup",
            "growth_os_monthly",
        ],
        "supporting_services": [
            "meeting_booking_sprint",
            "executive_growth_brief",
        ],
        "buyer_roles": ["founder_ceo", "head_of_sales", "growth_manager"],
        "common_pains_ar": [
            "Pipeline ضعيف عند الإطلاق",
            "صعوبة الوصول لـ decision makers في المؤسسات",
            "Cold outreach يضرّ سمعة الـ domain",
        ],
        "winning_offer_ar": "Pilot 7 أيام يثبت Saudi Tone + LinkedIn Lead Forms.",
    },
    "agencies": {
        "label_ar": "الوكالات (تسويق/مبيعات/CRM)",
        "primary_services": [
            "agency_partner_program",
            "partner_sprint",
        ],
        "supporting_services": [
            "list_intelligence",
            "first_10_opportunities_sprint",
        ],
        "buyer_roles": ["agency_owner", "head_of_sales", "growth_manager"],
        "common_pains_ar": [
            "تسليم نتائج قابلة للقياس للعملاء",
            "Proof Packs للعملاء بدون فريق نمو داخلي",
            "خلق revenue stream متكرر",
        ],
        "winning_offer_ar": "Agency Partner Program مع co-branded Proof Pack.",
    },
    "training_consulting": {
        "label_ar": "التدريب والاستشارات",
        "primary_services": [
            "first_10_opportunities_sprint",
            "list_intelligence",
            "growth_os_monthly",
        ],
        "supporting_services": [
            "executive_growth_brief",
            "meeting_booking_sprint",
        ],
        "buyer_roles": ["founder_ceo", "head_of_sales", "hr_manager"],
        "common_pains_ar": [
            "اعتماد مفرط على العلاقات الشخصية",
            "Pipeline متذبذب بين الفصول الدراسية/الـ quarters",
            "صعوبة الوصول لمدراء HR في الشركات",
        ],
        "winning_offer_ar": "First 10 Opportunities Sprint للوصول لـHR managers.",
    },
    "real_estate": {
        "label_ar": "العقار",
        "primary_services": [
            "list_intelligence",
            "whatsapp_compliance_setup",
            "first_10_opportunities_sprint",
        ],
        "supporting_services": [
            "meeting_booking_sprint",
            "growth_os_monthly",
        ],
        "buyer_roles": ["founder_ceo", "head_of_sales", "branch_manager"],
        "common_pains_ar": [
            "قاعدة عملاء واتساب غير منظمة",
            "خطر حظر رقم واتساب من الإفراط",
            "leads تأتي بدون مصدر واضح",
        ],
        "winning_offer_ar": "List Intelligence + WhatsApp Compliance Setup.",
    },
    "healthcare_local": {
        "label_ar": "العيادات والخدمات المحلية",
        "primary_services": [
            "local_growth_os",
            "whatsapp_compliance_setup",
            "list_intelligence",
        ],
        "supporting_services": [
            "growth_os_monthly",
        ],
        "buyer_roles": ["clinic_manager", "founder_ceo", "operations_manager"],
        "common_pains_ar": [
            "Reviews سلبية على Google Business",
            "no-show عالي بدون متابعة",
            "Reactivation للعملاء القدامى",
        ],
        "winning_offer_ar": "Local Growth OS لإدارة Reviews + WhatsApp inbound.",
    },
    "retail_ecommerce": {
        "label_ar": "التجزئة والـ E-commerce",
        "primary_services": [
            "list_intelligence",
            "whatsapp_compliance_setup",
            "local_growth_os",
        ],
        "supporting_services": [
            "growth_os_monthly",
            "executive_growth_brief",
        ],
        "buyer_roles": ["founder_ceo", "store_manager", "marketing_manager"],
        "common_pains_ar": [
            "Customer reactivation متعب يدوياً",
            "Reviews + reputation متفرقة",
            "Payment link sharing غير منظم",
        ],
        "winning_offer_ar": "List Intelligence + Local Growth OS + Moyasar invoice flow.",
    },
}


def list_verticals() -> dict[str, Any]:
    """Return all verticals with their full service stacks."""
    return {
        "total": len(VERTICALS_AR),
        "verticals": [
            {"id": vid, **vdata} for vid, vdata in VERTICALS_AR.items()
        ],
    }


def recommend_services_for_vertical(vertical_id: str) -> dict[str, Any]:
    """Recommend the service stack for a given vertical."""
    v = VERTICALS_AR.get(vertical_id)
    if v is None:
        return {
            "error": f"unknown vertical: {vertical_id}",
            "available_verticals": list(VERTICALS_AR.keys()),
        }
    return {
        "vertical_id": vertical_id,
        "label_ar": v["label_ar"],
        "primary_services": list(v["primary_services"]),
        "supporting_services": list(v["supporting_services"]),
        "buyer_roles": list(v["buyer_roles"]),
        "common_pains_ar": list(v["common_pains_ar"]),
        "winning_offer_ar": v["winning_offer_ar"],
    }


def map_industry_to_vertical(industry: str) -> str:
    """Best-effort mapping from a free-text industry → known vertical_id."""
    s = (industry or "").lower().strip()
    if any(k in s for k in ("saas", "software", "tech", "تقنية", "برمجيات")):
        return "b2b_saas"
    if any(k in s for k in ("agency", "وكالة", "marketing", "تسويق")):
        return "agencies"
    if any(k in s for k in ("training", "تدريب", "consult", "استشار")):
        return "training_consulting"
    if any(k in s for k in ("real estate", "عقار", "property", "broker")):
        return "real_estate"
    if any(k in s for k in ("clinic", "عيادة", "doctor", "health", "medical")):
        return "healthcare_local"
    if any(k in s for k in ("retail", "store", "متجر", "shop", "ecommerce", "تجزئة")):
        return "retail_ecommerce"
    return "b2b_saas"  # safe default
