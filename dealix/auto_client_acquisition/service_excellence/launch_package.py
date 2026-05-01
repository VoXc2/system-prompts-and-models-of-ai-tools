"""Launch package — لكل خدمة: landing page outline + sales script + demo + onboarding."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower import get_service


def build_landing_page_outline(service_id: str) -> dict[str, Any]:
    """Outline of a landing page for the service (Arabic, RTL)."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    return {
        "service_id": service_id,
        "title_ar": s.name_ar,
        "sections_ar": [
            "Hero: العرض في جملة + CTA",
            "وعد المنتج: ماذا سيحصل العميل عليه؟",
            "كيف تعمل الخدمة (3 خطوات)",
            "Deliverables — قائمة بالمخرجات",
            "Pricing — السعر بوضوح",
            "Proof — ما الذي نقيسه",
            "Safety — لا live send، Approval-first",
            "Trust — للوكالات / B2B سعودي",
            "FAQ",
            "CTA النهائي",
        ],
        "cta_ar": "ابدأ الآن" if s.pricing_max_sar > 0 else "احجز التشخيص المجاني",
        "must_include_ar": [
            "Approval-first.",
            "لا cold WhatsApp.",
            "PDPL-aware.",
            "لا وعود بنتائج مضمونة.",
        ],
    }


def build_sales_script(service_id: str) -> dict[str, Any]:
    """Sales script (Arabic) — discovery → pitch → close."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    return {
        "service_id": service_id,
        "discovery_questions_ar": [
            "وش أكبر تحدي نمو لديكم اليوم؟",
            "كيف تستهدفون اليوم؟ ما الذي يعمل؟",
            "ما الذي يأخذ وقتاً يومياً ولا يثبت قيمة؟",
            "هل عندكم قائمة عملاء قدامى لم تتم متابعتهم؟",
            "من يوافق على الرسائل قبل الإرسال؟",
        ],
        "pitch_ar": (
            f"بناءً على ما شاركته، {s.name_ar} مناسبة لكم. "
            f"خلال {('7 أيام' if s.pricing_model == 'sprint' else 'الشهر الأول')}، "
            f"سنطلع لكم: {', '.join(s.deliverables_ar)}."
        ),
        "objection_handling_ar": {
            "price": "نقدم Free Diagnostic أولاً — تشوفون النتائج قبل الدفع.",
            "timing": "Pilot 7 أيام لا يحتاج التزام طويل — جرّبوه ثم قرروا.",
            "trust": "Approval-first: لا نرسل أي شيء بدون موافقتكم.",
            "complexity": "نتولى الإعداد كاملاً في 3 أيام عمل.",
        },
        "close_ar": (
            "إذا الفكرة منطقية، أحدد لكم Pilot يبدأ يوم الأحد. "
            "أرسل لي تأكيد + اسم منسّق Approvals."
        ),
    }


def build_demo_script(service_id: str) -> dict[str, Any]:
    """12-minute Arabic demo script."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    return {
        "service_id": service_id,
        "duration_minutes": 12,
        "minute_by_minute_ar": [
            "0–2: الفكرة الكبرى — Dealix ليس CRM ولا أداة واتساب.",
            f"2–4: عرض {s.name_ar} — Daily Brief / Command Feed.",
            "4–6: مثال حي — 10 فرص في 10 دقائق.",
            "6–8: Trust Score + Simulator + Proof Pack.",
            "8–10: الأمان والتكاملات (security + connectors).",
            "10–12: العرض والـ CTA.",
        ],
        "do_not_do_ar": [
            "لا تكشف API keys على الشاشة.",
            "لا تشغّل live WhatsApp في الـdemo.",
            "لا تعد بأرقام لم تُحقَّق.",
        ],
    }


def build_onboarding_checklist(service_id: str) -> dict[str, Any]:
    """Onboarding checklist for the customer (first 5 days)."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    return {
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "first_5_days_ar": [
            "يوم 1: kick-off + جمع الـ intake + توقيع DPA draft.",
            "يوم 2: ربط القنوات الآمنة (Gmail drafts / Sheets / website forms).",
            "يوم 3: توليد أول Proof Pack template + تدريب على Approval Center.",
            "يوم 4: إطلاق أول mission (10 فرص في 10 دقائق).",
            "يوم 5: مراجعة النتائج + تخطيط الأسبوع الثاني.",
        ],
        "approval_required": True,
        "live_send_allowed": False,
    }


def build_service_launch_package(service_id: str) -> dict[str, Any]:
    """Full launch package = landing + sales + demo + onboarding."""
    return {
        "service_id": service_id,
        "landing": build_landing_page_outline(service_id),
        "sales_script": build_sales_script(service_id),
        "demo_script": build_demo_script(service_id),
        "onboarding": build_onboarding_checklist(service_id),
        "approval_required": True,
    }
