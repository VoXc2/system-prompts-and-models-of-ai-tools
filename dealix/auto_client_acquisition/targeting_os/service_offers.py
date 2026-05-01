"""Targeting-tier service offers — quick lookup of buyable offers."""

from __future__ import annotations

from typing import Any

# Targeting-OS-related offers. The full Service Tower has more.
TARGETING_OFFERS: tuple[dict[str, Any], ...] = (
    {
        "id": "list_intelligence",
        "name_ar": "تحليل قائمة (List Intelligence)",
        "target_customer_ar": "شركة عندها قائمة أرقام/إيميلات/عملاء قدامى",
        "outcome_ar": "أفضل 50 target من قائمتك + رسائل + خطة 7 أيام",
        "price_min_sar": 499,
        "price_max_sar": 1500,
    },
    {
        "id": "first_10_opportunities_sprint",
        "name_ar": "10 فرص في 10 دقائق",
        "target_customer_ar": "شركة B2B تحتاج فرص مؤهلة بسرعة",
        "outcome_ar": "10 فرص + رسائل + خطة متابعة + Proof Pack",
        "price_min_sar": 499,
        "price_max_sar": 1500,
    },
    {
        "id": "self_growth_operator",
        "name_ar": "مدير نمو شخصي (Self-Growth Operator)",
        "target_customer_ar": "مؤسسون / مستشارون / وكالات صغيرة",
        "outcome_ar": "Daily brief + drafts + متابعة + تقارير",
        "price_min_sar": 999,
        "price_max_sar": 999,
    },
    {
        "id": "linkedin_lead_gen_setup",
        "name_ar": "إعداد LinkedIn Lead Gen",
        "target_customer_ar": "شركات B2B تحتاج decision makers",
        "outcome_ar": "حملة Lead Gen Form + audiences + ربط CRM",
        "price_min_sar": 2000,
        "price_max_sar": 7500,
    },
    {
        "id": "whatsapp_compliance_setup",
        "name_ar": "إعداد امتثال واتساب",
        "target_customer_ar": "شركات تستخدم واتساب بشكل عشوائي",
        "outcome_ar": "تصنيف القوائم + opt-in templates + audit",
        "price_min_sar": 1500,
        "price_max_sar": 4000,
    },
    {
        "id": "partner_sprint",
        "name_ar": "سبرنت شراكات",
        "target_customer_ar": "شركات تبغى نمو عبر الشركاء",
        "outcome_ar": "20 شريك محتمل + رسائل + 5 اجتماعات",
        "price_min_sar": 3000,
        "price_max_sar": 7500,
    },
    {
        "id": "free_growth_diagnostic",
        "name_ar": "تشخيص نمو مجاني",
        "target_customer_ar": "أي شركة B2B تريد عينة قبل الـPilot",
        "outcome_ar": "3 فرص + رسالة + تقرير مخاطر + خطة Pilot",
        "price_min_sar": 0,
        "price_max_sar": 0,
    },
)


def list_targeting_services() -> dict[str, Any]:
    return {
        "total": len(TARGETING_OFFERS),
        "offers": [dict(o) for o in TARGETING_OFFERS],
    }


def recommend_service_offer(
    customer_type: str,
    *,
    goal: str = "fill_pipeline",
) -> dict[str, Any]:
    """Recommend the best-fit offer for a customer type + goal."""
    ct = (customer_type or "").lower()

    if "agency" in ct or "وكالة" in ct:
        chosen = next(o for o in TARGETING_OFFERS if o["id"] == "partner_sprint")
    elif "list" in ct or "قائمة" in ct:
        chosen = next(o for o in TARGETING_OFFERS if o["id"] == "list_intelligence")
    elif "founder" in ct or "مؤسس" in ct:
        chosen = next(o for o in TARGETING_OFFERS if o["id"] == "self_growth_operator")
    elif "saas" in ct or "b2b" in ct:
        chosen = next(o for o in TARGETING_OFFERS if o["id"] == "first_10_opportunities_sprint")
    elif "whatsapp" in ct or "واتساب" in ct:
        chosen = next(o for o in TARGETING_OFFERS if o["id"] == "whatsapp_compliance_setup")
    else:
        chosen = next(o for o in TARGETING_OFFERS if o["id"] == "free_growth_diagnostic")

    return {
        "recommended_offer": dict(chosen),
        "reasoning_ar": (
            f"بناءً على نوع العميل ({customer_type}) والهدف ({goal})، "
            f"الأنسب: {chosen['name_ar']}."
        ),
    }


def build_offer_card(service: dict[str, Any] | str) -> dict[str, Any]:
    """Build an Arabic offer card (≤3 buttons) for the inbox/feed."""
    if isinstance(service, str):
        service = next((o for o in TARGETING_OFFERS if o["id"] == service),
                       {"id": service, "name_ar": service,
                        "outcome_ar": "", "price_min_sar": 0, "price_max_sar": 0})
    price_label = (
        "مجاني"
        if service.get("price_min_sar") == 0
        else f"{service.get('price_min_sar')}–{service.get('price_max_sar')} ريال"
    )
    return {
        "type": "service_offer",
        "service_id": service.get("id"),
        "title_ar": service.get("name_ar", "خدمة"),
        "summary_ar": service.get("outcome_ar", ""),
        "price_ar": price_label,
        "buttons_ar": ["ابدأ الآن", "اطلب عرض", "تخطي"],
        "approval_required": True,
    }


def estimate_service_price(
    service_id: str,
    *,
    company_size: str = "small",
    urgency: str = "normal",
    channels_count: int = 1,
) -> dict[str, Any]:
    """Estimate a SAR price range for a service given inputs."""
    base = next((o for o in TARGETING_OFFERS if o["id"] == service_id), None)
    if base is None:
        return {"error": f"unknown service: {service_id}"}

    p_min = float(base["price_min_sar"])
    p_max = float(base["price_max_sar"])

    # Size multiplier
    size_mult = {"micro": 0.8, "small": 1.0, "medium": 1.3, "large": 1.7}.get(
        company_size, 1.0,
    )
    # Urgency multiplier
    urgency_mult = {"normal": 1.0, "rush": 1.3, "asap": 1.5}.get(urgency, 1.0)
    # Channel multiplier
    ch_mult = 1.0 + max(0, channels_count - 1) * 0.15

    return {
        "service_id": service_id,
        "estimated_min_sar": round(p_min * size_mult * urgency_mult * ch_mult),
        "estimated_max_sar": round(p_max * size_mult * urgency_mult * ch_mult),
        "currency": "SAR",
        "factors": {
            "company_size": company_size,
            "urgency": urgency,
            "channels_count": channels_count,
        },
    }
