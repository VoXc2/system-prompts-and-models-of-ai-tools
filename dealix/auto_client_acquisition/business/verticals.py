"""Vertical playbooks — deterministic."""

from __future__ import annotations

from typing import Any, Literal

VerticalKey = Literal[
    "clinics",
    "real_estate",
    "logistics",
    "training",
    "agencies",
    "restaurants",
    "hospitality",
    "construction",
    "b2b_saas",
]


def get_vertical_playbooks() -> dict[str, Any]:
    base = {
        "clinics": {
            "pain_ar": "زحمة المواعيد وتأخر المتابعة على واتساب.",
            "buyer": "مدير العيادة أو المالك",
            "why_now_signals": ["hiring_sales", "booking_link", "review_spike"],
            "message_angle_ar": "تحسين التحويل والمتابعة بدون إزعاج للمرضى.",
            "roi_metric": "no_show_rate_reduction",
            "compliance": "PDPL + healthcare marketing sensitivity",
            "pricing_sensitivity": "medium",
        },
        "real_estate": {
            "pain_ar": "تأهيل العملاء والمتابعة بين الوسيط والمهتم.",
            "buyer": "مدير المبيعات أو المؤسس",
            "why_now_signals": ["new_branch", "website_change", "ad_activity"],
            "message_angle_ar": "سرعة الرد على الاستفسارات وفرز الجادين.",
            "roi_metric": "qualified_tours_booked",
            "compliance": "Opt-in for marketing WhatsApp",
            "pricing_sensitivity": "medium-high",
        },
        "logistics": {
            "pain_ar": "متابعة العروض وRFQs عبر قنوات متعددة.",
            "buyer": "مدير التجاري",
            "why_now_signals": ["hiring_sales", "tender_opportunity", "new_partnership"],
            "message_angle_ar": "تسريع دورة الاقتباس والمتابعة.",
            "roi_metric": "quote_to_win_rate",
            "compliance": "B2B outreach policies",
            "pricing_sensitivity": "medium",
        },
        "training": {
            "pain_ar": "تحويل الاستفسار إلى تسجيل دورة.",
            "buyer": "مدير الأكاديمية",
            "why_now_signals": ["booking_link", "event_participation", "website_change"],
            "message_angle_ar": "متابعة مهذبة عربية بعد الاهتمام الأولي.",
            "roi_metric": "enrollment_conversion",
            "compliance": "Marketing consent",
            "pricing_sensitivity": "low-medium",
        },
        "agencies": {
            "pain_ar": "إثبات العائد للعميل وتكرار العمليات.",
            "buyer": "شريك أو مدير حسابات",
            "why_now_signals": ["hiring_sales", "new_product_launch"],
            "message_angle_ar": "Dealix كطبقة إيرادات فوق خدماتكم.",
            "roi_metric": "client_retention_and_upsell",
            "compliance": "Partner agreements + rev share clarity",
            "pricing_sensitivity": "partner_model",
        },
        "restaurants": {
            "pain_ar": "حجوزات واتساب وتجربة ضيف.",
            "buyer": "المالك أو مدير التشغيل",
            "why_now_signals": ["booking_link", "review_spike", "ad_activity"],
            "message_angle_ar": "تنظيم الطلب العالي دون أخطاء بشرية.",
            "roi_metric": "booking_conversion",
            "compliance": "Consumer messaging rules",
            "pricing_sensitivity": "high",
        },
        "hospitality": {
            "pain_ar": "مبيعات المجموعات والفعاليات.",
            "buyer": "مدير المبيعات",
            "why_now_signals": ["event_participation", "new_partnership", "website_change"],
            "message_angle_ar": "متابعة B2B للمجموعات والشركات.",
            "roi_metric": "group_bookings",
            "compliance": "B2B opt-in",
            "pricing_sensitivity": "medium",
        },
        "construction": {
            "pain_ar": "مناقصات وموردين وتنسيق عروض.",
            "buyer": "مدير التطوير التجاري",
            "why_now_signals": ["tender_opportunity", "new_branch", "hiring_sales"],
            "message_angle_ar": "تنبيهات فرص ومتابعة آمنة.",
            "roi_metric": "bid_participation_rate",
            "compliance": "Tender ethics + PDPL",
            "pricing_sensitivity": "low",
        },
        "b2b_saas": {
            "pain_ar": "توسعة الحساب وتسريب الإيرادات.",
            "buyer": "Revenue leader / CS lead",
            "why_now_signals": ["crm_detected", "funding", "hiring_sales"],
            "message_angle_ar": "إشارات تمديد وفرص ترقية خطة.",
            "roi_metric": "expansion_pipeline",
            "compliance": "Data processing agreements",
            "pricing_sensitivity": "medium",
        },
    }
    return {"verticals": base}


def recommend_vertical(*, industry: str, city: str, goal: str) -> dict[str, Any]:
    ind = industry.lower().strip()
    mapping = {
        "clinic": "clinics",
        "عيادة": "clinics",
        "real": "real_estate",
        "عقار": "real_estate",
        "logistics": "logistics",
        "شحن": "logistics",
        "training": "training",
        "تدريب": "training",
        "agency": "agencies",
        "وكالة": "agencies",
    }
    key = next((v for k, v in mapping.items() if k in ind), "b2b_saas")
    pb = get_vertical_playbooks()["verticals"][key]
    return {
        "recommended_vertical": key,
        "city": city,
        "goal": goal,
        "playbook": pb,
    }


def vertical_roi_metric(vertical: VerticalKey) -> str:
    pb = get_vertical_playbooks()["verticals"].get(vertical, {})
    return str(pb.get("roi_metric", "pipeline_velocity"))
