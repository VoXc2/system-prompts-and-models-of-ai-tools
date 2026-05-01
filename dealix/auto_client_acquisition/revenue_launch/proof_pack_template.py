"""Proof Pack template — client-facing summary at end of Pilot."""

from __future__ import annotations

from typing import Any


def build_private_beta_proof_pack(
    *,
    company_name: str = "",
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the private-beta Proof Pack template (Arabic)."""
    metrics = metrics or {}
    return {
        "title_ar": f"Proof Pack — {company_name or 'Pilot 7 أيام'}",
        "sections_ar": [
            "ملخص تنفيذي (5 أسطر)",
            "ما عمله Dealix هذا الأسبوع",
            "النتائج بالأرقام (vs أهداف الأسبوع)",
            "أبرز الردود والاعتراضات",
            "المخاطر التي تم منعها (PDPL/سمعة القناة)",
            "أفضل 3 رسائل (مع safety+tone scores)",
            "Action Ledger (كل فعل + مَن اعتمده)",
            "التوصية بالخطوة التالية",
        ],
        "metrics_to_include": [
            "opportunities_generated",
            "drafts_approved",
            "positive_replies",
            "meetings_drafted",
            "pipeline_influenced_sar",
            "risks_blocked",
            "time_saved_hours",
        ],
        "captured_metrics": metrics,
        "approval_required": True,
        "delivery_format": ["pdf", "json", "whatsapp_summary"],
    }


def build_client_summary(
    *,
    company_name: str = "",
    opportunities_count: int = 0,
    approved_drafts: int = 0,
    meetings: int = 0,
    pipeline_sar: float = 0.0,
    risks_blocked: int = 0,
) -> dict[str, Any]:
    """5-line Arabic executive summary for the client."""
    lines = [
        f"خلال 7 أيام، شغّل Dealix Pilot لشركة {company_name or '(العميل)'}.",
        f"تم توليد {opportunities_count} فرصة B2B + اعتماد {approved_drafts} رسالة.",
        f"نتج عن ذلك {meetings} اجتماع و pipeline متأثر بقيمة {pipeline_sar:.0f} ريال.",
        f"تم منع {risks_blocked} مخاطر تواصل تلقائياً (PDPL/cold WhatsApp/سمعة).",
        "التوصية: الترقية لـ Growth OS Pilot 30 يوم لتثبيت العائد المتكرر.",
    ]
    return {
        "company_name": company_name,
        "summary_ar": lines,
        "approval_required": True,
        "deliverable_format": "5_line_executive_summary",
    }


def build_next_step_recommendation(
    *,
    pilot_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Recommend next step based on pilot outcome metrics."""
    m = pilot_metrics or {}
    pipeline_sar = float(m.get("pipeline_sar", 0))
    meetings = int(m.get("meetings", 0))
    csat = int(m.get("csat", 0))   # 0..10

    if csat >= 8 and (pipeline_sar >= 25_000 or meetings >= 2):
        action = "upsell_growth_os_monthly"
        msg = (
            "Pilot قوي — اعرض Growth OS Monthly بـ2,999 ريال شهرياً مع "
            "خصم 15% على الاشتراك السنوي."
        )
    elif pipeline_sar < 5_000 and meetings == 0:
        action = "iterate_or_archive"
        msg = (
            "النتائج ضعيفة هذه الجولة. اقترح زاوية مختلفة (قطاع/عرض) "
            "أو أرشف العميل بدون ضغط."
        )
    else:
        action = "extend_pilot"
        msg = (
            "Pilot واعد. مدّد الأسبوع لأسبوعين بـ500 ريال إضافي، "
            "أو أضف قناة (Email + LinkedIn Lead Form)."
        )

    return {
        "next_action": action,
        "recommendation_ar": msg,
        "approval_required": True,
    }
