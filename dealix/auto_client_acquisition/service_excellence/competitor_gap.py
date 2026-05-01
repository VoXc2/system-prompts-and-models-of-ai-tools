"""Competitor gap analysis — لا scraping، فقط مقارنة structural بفئات معروفة."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower import get_service

# Categories Dealix competes against. Strengths/limits are public knowledge.
COMPETITOR_CATEGORIES: dict[str, dict[str, list[str]]] = {
    "crm": {
        "strengths": ["تخزين بيانات", "pipeline tracking", "تكاملات واسعة"],
        "limits": ["ينتظر إدخال يدوي", "لا يقرر ما تفعل اليوم",
                   "غير مصمم للسوق العربي"],
    },
    "whatsapp_tools": {
        "strengths": ["إرسال جماعي", "templates", "broadcast"],
        "limits": ["لا approval-first", "لا proof", "خطر PDPL"],
    },
    "email_assistant": {
        "strengths": ["كتابة أسرع", "تكامل Gmail/Outlook"],
        "limits": ["لا يحول الإيميل لـ pipeline", "لا proof", "عام غير عربي"],
    },
    "linkedin_tools": {
        "strengths": ["إيجاد leads"],
        "limits": ["كثير منها يخالف ToS", "auto-DM يوقف الحسابات",
                   "لا يحترم PDPL"],
    },
    "agency": {
        "strengths": ["خبرة بشرية", "علاقات سوق"],
        "limits": ["لا تتوسع", "غير قابلة للتكرار", "تعتمد على الفريق"],
    },
    "revenue_intelligence": {
        "strengths": ["تحليل المكالمات", "deal scoring"],
        "limits": ["تبدأ بعد الـcall", "لا يصنع pipeline من الصفر"],
    },
    "generic_ai_agent": {
        "strengths": ["مرن", "يكتب أي شيء"],
        "limits": ["بدون سياق شركة", "بدون proof", "بدون امتثال محلي"],
    },
}


def compare_against_categories(service_id: str) -> dict[str, Any]:
    """Compare a Dealix service against generic competitor categories."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}

    dealix_advantages = [
        "موجّه للسوق السعودي بالعربية الطبيعية.",
        "Approval-first — لا يضرّ سمعة العميل.",
        "Proof Pack شهري قابل للقياس.",
        "Multi-channel orchestration بـ سياسة موحدة.",
        "Self-improving Curator يحسّن الرسائل أسبوعياً.",
        "PDPL-aware من اليوم الأول.",
    ]

    gaps_to_close: list[str] = []
    if "growth_os" not in service_id:
        gaps_to_close.append("Daily autopilot كامل (متاح في Growth OS).")
    if service_id == "free_growth_diagnostic":
        gaps_to_close.append("Proof Pack حقيقي بعد 30 يوم.")

    do_not_copy = [
        "auto-DM على LinkedIn (مخالف).",
        "scraping ضد ToS.",
        "وعود بنتائج مضمونة.",
        "مفاتيح API غير محمية في الواجهة.",
    ]

    return {
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "competitor_categories": COMPETITOR_CATEGORIES,
        "dealix_advantages_ar": dealix_advantages,
        "gaps_to_close_ar": gaps_to_close,
        "do_not_copy_ar": do_not_copy,
    }
