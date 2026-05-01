"""
Growth Missions — outcome-shaped tasks instead of features.

Each mission has: id, title_ar, goal_ar, steps (ordered, approval-gated),
expected_duration_days, kill_metric (the ONE number that proves success).

Pure deterministic. Production wires each step to the relevant agent.
"""

from __future__ import annotations

from typing import Any


GROWTH_MISSIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "first_10_opportunities",
        "title_ar": "اطلع لي 10 فرص",
        "goal_ar": "اكتشاف 10 شركات سعودية مناسبة + رسائل عربية + موافقة + متابعة أسبوع.",
        "expected_duration_days": 7,
        "kill_metric": "ten_drafts_approved",
        "steps_ar": [
            "تحديد القطاع والمدينة + المعايير الأساسية.",
            "اكتشاف 30 شركة مرشحة من المصادر المسموحة.",
            "فلترة لـ 10 بأعلى Why-Now score.",
            "كتابة 10 رسائل عربية بحالة pending_approval.",
            "موافقة المشغّل على عينة → إرسال آمن.",
            "تصنيف الردود + اقتراح متابعة لكل واحدة.",
            "Proof Pack أسبوعي عند الإغلاق.",
        ],
        "primary_endpoint": "/api/v1/innovation/opportunities/ten-in-ten",
        "approval_required": True,
    },
    {
        "id": "recover_stalled_deals",
        "title_ar": "أنقذ الصفقات المتوقفة",
        "goal_ar": "اكتشف الصفقات بدون نشاط 14+ يوم + اقترح متابعات multi-thread.",
        "expected_duration_days": 5,
        "kill_metric": "stalled_deals_revived",
        "steps_ar": [
            "قراءة pipeline الحالي + revenue_graph.leak_detector.",
            "تصنيف الصفقات: stalled / single-threaded / no-proposal.",
            "اقتراح multi-thread (DM إضافي داخل الحساب).",
            "كتابة drafts متابعة pending_approval لكل صفقة.",
            "موافقة المشغّل → إرسال + جدولة re-check بعد 7 أيام.",
        ],
        "primary_endpoint": "/api/v1/revenue-os/leaks",
        "approval_required": True,
    },
    {
        "id": "partnership_sprint",
        "title_ar": "ابدأ شراكات",
        "goal_ar": "تحديد + التواصل مع 5 شركاء محتملين خلال أسبوعين.",
        "expected_duration_days": 14,
        "kill_metric": "partner_intros_replied",
        "steps_ar": [
            "تحديد قطاع العميل + حجمه → اقتراح أنواع شركاء مناسبة.",
            "ترشيح 5 شركاء محتملين بأعلى strategic_value.",
            "كتابة outreach warm لكل واحد.",
            "موافقة المشغّل → إرسال على email.",
            "متابعة الردود + جدولة 20 دقيقة لكل ردّ إيجابي.",
            "Partner scorecard أولي بعد المكالمات.",
        ],
        "primary_endpoint": "/api/v1/growth-operator/partners/suggest",
        "approval_required": True,
    },
    {
        "id": "safe_whatsapp_campaign",
        "title_ar": "جهز حملة واتساب آمنة",
        "goal_ar": "تحويل قائمة العميل إلى حملة WhatsApp يحترم PDPL + opt-in.",
        "expected_duration_days": 3,
        "kill_metric": "safe_messages_drafted",
        "steps_ar": [
            "رفع قائمة الأرقام عبر contact_importer.",
            "تنظيف + dedupe + classify_source.",
            "فحص contactability — إخراج blocked/needs_review.",
            "كتابة رسائل عربية لكل segment آمن.",
            "موافقة المشغّل لكل segment على حدة.",
            "إرسال آمن مع opt-out في كل رسالة.",
        ],
        "primary_endpoint": "/api/v1/growth-operator/contacts/import-preview",
        "approval_required": True,
    },
    {
        "id": "meeting_booking_sprint",
        "title_ar": "احجز لي 3 اجتماعات",
        "goal_ar": "حجز 3 اجتماعات مع leads أعلى Why-Now خلال 5 أيام عمل.",
        "expected_duration_days": 5,
        "kill_metric": "meetings_confirmed",
        "steps_ar": [
            "اختيار أعلى 10 leads من Top-10 السابق.",
            "إعداد agenda + calendar draft لكل واحد.",
            "كتابة intro + ask مكالمة 15 دقيقة.",
            "موافقة + إرسال WhatsApp/email.",
            "تأكيد الحضور قبل الاجتماع بـ 24 ساعة.",
            "post-meeting follow-up draft.",
        ],
        "primary_endpoint": "/api/v1/growth-operator/meetings/draft",
        "approval_required": True,
    },
    {
        "id": "list_cleanup",
        "title_ar": "ارفع قائمتي ونظفها",
        "goal_ar": "تحويل ملف غير منظم إلى قائمة contactability-classified جاهزة.",
        "expected_duration_days": 1,
        "kill_metric": "safe_contacts_extracted",
        "steps_ar": [
            "رفع CSV/Excel.",
            "normalize_phone + dedupe.",
            "classify_contact_source لكل سطر.",
            "score_contactability لكل سطر.",
            "تقرير: safe / needs_review / blocked + عدد + عينة.",
            "اقتراح: ابدأ بالـ safe فقط، مع plan لـ needs_review.",
        ],
        "primary_endpoint": "/api/v1/growth-operator/contacts/import-preview",
        "approval_required": True,
    },
)


def list_missions() -> dict[str, Any]:
    """Return the canonical mission catalog."""
    return {
        "count": len(GROWTH_MISSIONS),
        "missions": list(GROWTH_MISSIONS),
        "kill_feature_id": "first_10_opportunities",
    }


def run_mission(mission_id: str, *, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Plan a mission run — returns the execution outline + first-step
    prompt for the operator. Does NOT actually execute steps; that's
    done by routing each step to its primary endpoint.
    """
    mission = next((m for m in GROWTH_MISSIONS if m["id"] == mission_id), None)
    if mission is None:
        return {
            "error": f"unknown_mission: {mission_id}",
            "available_ids": [m["id"] for m in GROWTH_MISSIONS],
        }
    return {
        "mission_id": mission_id,
        "title_ar": mission["title_ar"],
        "goal_ar": mission["goal_ar"],
        "kill_metric": mission["kill_metric"],
        "expected_duration_days": mission["expected_duration_days"],
        "current_step_index": 0,
        "next_step_ar": mission["steps_ar"][0],
        "primary_endpoint": mission["primary_endpoint"],
        "payload_received": payload or {},
        "approval_required": True,
        "approval_status": "pending_approval",
    }
