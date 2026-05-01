"""Sellable platform services — static catalog metadata."""

from __future__ import annotations

from typing import Any

_SERVICES: list[dict[str, Any]] = [
    {
        "id": "unified_inbox",
        "name_ar": "صندوق وارد موحّد",
        "tier": "platform",
        "description_ar": "بطاقات قرار عربية من أحداث موحّدة مع حد ثلاثة إجراءات.",
    },
    {
        "id": "action_policy_engine",
        "name_ar": "محرك سياسة الإجراءات",
        "tier": "platform",
        "description_ar": "قواعد موافقة واتساب بارد ودفع — deterministic.",
    },
    {
        "id": "tool_gateway_safe",
        "name_ar": "بوابة أدوات آمنة",
        "tier": "platform",
        "description_ar": "لا إرسال حي — مسودات وحالات موافقة فقط.",
    },
    {
        "id": "growth_intelligence_mvp",
        "name_ar": "ذكاء نمو MVP",
        "tier": "intelligence",
        "description_ar": "Trust Score وRevenue DNA وموجز مجلس — JSON جاهز للعرض.",
    },
    {
        "id": "integrations_draft_pack",
        "name_ar": "حزمة مسودات تكامل",
        "tier": "integrations",
        "description_ar": "Gmail / Calendar / Moyasar — payloads تحقق فقط بدون OAuth.",
    },
    {
        "id": "growth_operator_subscription",
        "name_ar": "اشتراك Growth Operator",
        "tier": "subscription",
        "pricing_model": "monthly_sar",
        "target_customer_ar": "B2B سعودي",
        "outcome_ar": "Daily brief + command feed + موافقات + Proof Pack أسبوعي.",
        "proof_metric_ar": "عدد الموافقات والمسودات والأثر المقدّر.",
    },
    {
        "id": "channel_setup_service",
        "name_ar": "خدمة إعداد القنوات",
        "tier": "services",
        "pricing_model": "setup_fee",
        "target_customer_ar": "فرق مبيعات وعمليات",
        "outcome_ar": "ربط واتساب/بريد/تقويم ضمن سياسات آمنة.",
        "required_integrations": ["whatsapp", "gmail", "google_calendar", "moyasar"],
    },
    {
        "id": "lead_intelligence_service",
        "name_ar": "ذكاء قوائم العملاء",
        "tier": "services",
        "pricing_model": "per_project",
        "outcome_ar": "تطبيع، إزالة تكرار، تصنيف contactability.",
    },
    {
        "id": "partnership_sprint",
        "name_ar": "Partner Sprint — ١٤ يوم",
        "tier": "services",
        "pricing_model": "fixed_sprint",
        "outcome_ar": "قائمة شركاء + رسائل + اجتماعات مقترحة.",
    },
    {
        "id": "email_revenue_rescue",
        "name_ar": "إنقاذ إيراد البريد",
        "tier": "services",
        "pricing_model": "pilot_then_monthly",
        "outcome_ar": "فرص ضائعة + مسودات متابعة — بدون إرسال حتى موافقة.",
    },
    {
        "id": "social_growth_os",
        "name_ar": "نمو اجتماعي (رسمي فقط)",
        "tier": "services",
        "pricing_model": "monthly_sar",
        "outcome_ar": "تحويل تعليقات/نماذج رسمية إلى كروت قرار.",
    },
    {
        "id": "local_business_growth",
        "name_ar": "نمو محلي (عيادات/متاجر)",
        "tier": "vertical",
        "pricing_model": "monthly_sar",
        "outcome_ar": "تقييمات Google + واتساب inbound + روابط دفع draft.",
    },
    {
        "id": "aeo_sprint",
        "name_ar": "AI Visibility / AEO Sprint",
        "tier": "services",
        "pricing_model": "fixed_sprint",
        "outcome_ar": "فجوات ظهور وأسئلة مقترحة — بدون وعود زائفة.",
    },
    {
        "id": "customer_success_operator",
        "name_ar": "مشغّل نجاح العملاء",
        "tier": "subscription",
        "pricing_model": "add_on",
        "outcome_ar": "تنبيه at-risk + QBR draft — بدون إرسال تلقائي.",
    },
]


def get_service_catalog() -> dict[str, Any]:
    return {"services": list(_SERVICES), "version": 2}
