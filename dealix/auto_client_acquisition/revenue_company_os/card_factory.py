"""Deterministic role-scoped command cards for Revenue OS (demo / in-process)."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.revenue_company_os.cards import (
    MAX_CARDS_VISIBLE,
    CardType,
    UserRole,
    normalize_card,
)


def _btn(label_ar: str, action: str) -> dict[str, str]:
    return {"label_ar": label_ar, "action": action}


def _card(
    *,
    card_id: str,
    role: str,
    ctype: str,
    title_ar: str,
    why_now_ar: str,
    recommended_action_ar: str,
    risk_level: str,
    buttons: list[dict[str, str]],
    action_mode: str,
    proof_impact: list[str],
    context: dict[str, Any] | None = None,
    status: str = "pending",
) -> dict[str, Any]:
    return normalize_card(
        {
            "card_id": card_id,
            "tenant_id": "demo_tenant",
            "role": role,
            "type": ctype,
            "title_ar": title_ar,
            "why_now_ar": why_now_ar,
            "context": context or {},
            "recommended_action_ar": recommended_action_ar,
            "risk_level": risk_level,
            "buttons": buttons,
            "action_mode": action_mode,
            "proof_impact": proof_impact,
            "status": status,
        }
    )


def _ceo_cards() -> list[dict[str, Any]]:
    r = UserRole.CEO.value
    return [
        _card(
            card_id=f"{r}_brief_1",
            role=r,
            ctype=CardType.CEO_BRIEF.value,
            title_ar="👑 أهم ٣ قرارات اليوم",
            why_now_ar="تغيّر نشاط الوكالات أعلى من شركات SaaS في السجل الأخير.",
            recommended_action_ar="ركّز لمسات اليوم على الوكالات؛ أرسل Pilot ٤٩٩ لعميلين جاهزين؛ لا تستخدم واتساب بارد.",
            risk_level="medium",
            buttons=[
                _btn("اعتمد الخطة", "approve_daily_plan"),
                _btn("اعرض التفاصيل", "expand_brief"),
                _btn("أرسل للمدير", "delegate_sales_manager"),
            ],
            action_mode="approval_required",
            proof_impact=["executive_brief_created", "decisions_recommended"],
        ),
        _card(
            card_id=f"{r}_partner_1",
            role=r,
            ctype=CardType.PARTNER.value,
            title_ar="🤝 شريك محتمل — وكالة Riyadh SMB",
            why_now_ar="لديها عملاء SMB وتحتاج Proof متكرر لعملائها.",
            recommended_action_ar="رسالة شراكة + Agency Partner Pilot على عميل واحد.",
            risk_level="low",
            buttons=[
                _btn("جهّز رسالة", "draft_partner_message"),
                _btn("احجز اجتماع", "draft_meeting_invite"),
                _btn("تخطي", "skip"),
            ],
            action_mode="draft_only",
            proof_impact=["partner_suggested", "partner_scorecard_created"],
        ),
        _card(
            card_id=f"{r}_risk_1",
            role=r,
            ctype=CardType.RISK.value,
            title_ar="⛔ قناة عالية المخاطر",
            why_now_ar="اقتراح حملة واتساب لقائمة باردة ظهر في المسودات.",
            recommended_action_ar="استخدم إيميل أو LinkedIn يدوي مع opt-in؛ لا إرسال واتساب بارد.",
            risk_level="high",
            buttons=[
                _btn("اعرض السياسة", "show_policy"),
                _btn("مسودة بديلة", "draft_safe_alternative"),
                _btn("إغلاق", "dismiss"),
            ],
            action_mode="blocked",
            proof_impact=["risks_blocked"],
            context={"channel": "whatsapp", "policy": "no_cold_whatsapp"},
        ),
        _card(
            card_id=f"{r}_proof_1",
            role=r,
            ctype=CardType.PROOF.value,
            title_ar="📊 Proof Pack — جاهز للمراجعة",
            why_now_ar="اكتمل أسبوع تشغيل؛ جمع لقطات وموافقة عميل.",
            recommended_action_ar="أرسل الملخص + عرض الترقية إلى Growth Starter.",
            risk_level="low",
            buttons=[
                _btn("اعرض التقرير", "open_proof"),
                _btn("أرسل للعميل", "draft_client_email"),
                _btn("حضّر عرض الترقية", "draft_upgrade_offer"),
            ],
            action_mode="approval_required",
            proof_impact=["proof_generated", "upgrade_recommended"],
        ),
    ]


def _sales_cards() -> list[dict[str, Any]]:
    r = UserRole.SALES_MANAGER.value
    return [
        _card(
            card_id=f"{r}_deal_1",
            role=r,
            ctype=CardType.DEAL_FOLLOWUP.value,
            title_ar="📌 صفقة تحتاج متابعة",
            why_now_ar="اكتمل الديمو قبل ٣ أيام ولا يوجد follow-up مسجّل.",
            recommended_action_ar="إرسال follow-up يختصر القيمة ويقترح Pilot ٤٩٩.",
            risk_level="medium",
            buttons=[
                _btn("جهّز Follow-up", "draft_followup_email"),
                _btn("حوّل للـ CEO", "escalate_ceo"),
                _btn("تخطي", "skip"),
            ],
            action_mode="approval_required",
            proof_impact=["deal_risk_detected", "followup_created", "approval_requested"],
        ),
        _card(
            card_id=f"{r}_neg_1",
            role=r,
            ctype=CardType.NEGOTIATION.value,
            title_ar="💬 اعتراض: السعر مرتفع",
            why_now_ar="العميل لم يرَ Proof كافياً بعد؛ الخصم المباشر يضعف القيمة.",
            recommended_action_ar="اقترح Pilot ٤٩٩ بدل خصم على الاشتراك الشهري.",
            risk_level="medium",
            buttons=[
                _btn("استخدم الرد", "use_objection_reply"),
                _btn("عدّل النبرة", "edit_tone"),
                _btn("جهّز عرض بديل", "draft_counter_offer"),
            ],
            action_mode="draft_only",
            proof_impact=["objection_handled", "draft_created"],
        ),
        _card(
            card_id=f"{r}_close_1",
            role=r,
            ctype=CardType.CLOSE.value,
            title_ar="💰 فرصة إغلاق",
            why_now_ar="العميل طلب تفاصيل بعد الديمو.",
            recommended_action_ar="أرسل نص الدفع + نموذج intake (يدوي) الآن.",
            risk_level="low",
            buttons=[
                _btn("أرسل نص الدفع", "draft_payment_message"),
                _btn("جهّز intake", "draft_intake_form"),
                _btn("تخطي", "skip"),
            ],
            action_mode="approval_required",
            proof_impact=["payment_link_drafted", "approval_requested"],
        ),
    ]


def _growth_cards() -> list[dict[str, Any]]:
    r = UserRole.GROWTH_MANAGER.value
    return [
        _card(
            card_id=f"{r}_plan_1",
            role=r,
            ctype=CardType.GROWTH_PLAN.value,
            title_ar="📣 خطة النمو اليوم",
            why_now_ar="ردود الوكالات أعلى من شركات SaaS في آخر أسبوع.",
            recommended_action_ar="١٠ رسائل لوكالات B2B + ٥ متابعات + منشور LinkedIn واحد.",
            risk_level="low",
            buttons=[
                _btn("اعتمد الخطة", "approve_daily_plan"),
                _btn("غيّر الشريحة", "change_segment"),
                _btn("اعرض scorecard", "open_scorecard"),
            ],
            action_mode="approval_required",
            proof_impact=["daily_growth_plan_created", "channel_insight_created"],
        ),
        _card(
            card_id=f"{r}_opp_1",
            role=r,
            ctype=CardType.OPPORTUNITY.value,
            title_ar="🟢 فرصة — قطاع تدريب",
            why_now_ar="إعلان توظيف مبيعات + توسع فرع.",
            recommended_action_ar="مسودة إيميل تعريفي + عرض Diagnostic (بدون إرسال حي).",
            risk_level="low",
            buttons=[
                _btn("اعتمد المسودة", "approve_draft"),
                _btn("عدّل", "edit_draft"),
                _btn("تخطي", "skip"),
            ],
            action_mode="draft_only",
            proof_impact=["opportunity_created", "draft_created"],
        ),
    ]


def _agency_cards() -> list[dict[str, Any]]:
    r = UserRole.AGENCY_PARTNER.value
    return [
        _card(
            card_id=f"{r}_client_1",
            role=r,
            ctype=CardType.DELIVERY.value,
            title_ar="➕ عميل جديد للوكالة",
            why_now_ar="إضافة عميل تفعّل Diagnostic وProof Pack باسم الوكالة.",
            recommended_action_ar="شغّل intake قصير ثم Diagnostic على القطاع المختار.",
            risk_level="low",
            buttons=[
                _btn("ابدأ intake", "start_intake"),
                _btn("شغّل diagnostic", "run_diagnostic"),
                _btn("تخطي", "skip"),
            ],
            action_mode="suggest_only",
            proof_impact=["partner_client_onboarded", "opportunity_created"],
        ),
        _card(
            card_id=f"{r}_proof_1",
            role=r,
            ctype=CardType.PROOF.value,
            title_ar="📊 Co-branded Proof Pack",
            why_now_ar="العميل أنهى أسبوعاً؛ جاهز لتسليم تقرير مختوم باسم الوكالة.",
            recommended_action_ar="راجع الأرقام واطلب موافقة العميل قبل الإرسال.",
            risk_level="low",
            buttons=[
                _btn("اعرض المسودة", "open_proof_draft"),
                _btn("اطلب موافقة", "request_client_approval"),
                _btn("تخطي", "skip"),
            ],
            action_mode="approval_required",
            proof_impact=["proof_generated", "partner_revenue_event"],
        ),
    ]


def _support_cards() -> list[dict[str, Any]]:
    r = UserRole.SUPPORT.value
    return [
        _card(
            card_id=f"{r}_ticket_1",
            role=r,
            ctype=CardType.SUPPORT.value,
            title_ar="🛠️ طلب دعم — ربط Gmail",
            why_now_ar="العميل لم يكمل OAuth؛ التذكرة P2.",
            recommended_action_ar="أرسل رابط الدليل + تحقق من صلاحيات المسودة فقط.",
            risk_level="low",
            buttons=[
                _btn("افتح دليل الربط", "open_connector_doc"),
                _btn("صعّد", "escalate_p1"),
                _btn("أغلق", "resolve"),
            ],
            action_mode="suggest_only",
            proof_impact=["support_ticket_created", "sla_started"],
        ),
    ]


def _delivery_cards() -> list[dict[str, Any]]:
    r = UserRole.SERVICE_DELIVERY.value
    return [
        _card(
            card_id=f"{r}_sla_1",
            role=r,
            ctype=CardType.DELIVERY.value,
            title_ar="⏱️ تسليم — بيانات ناقصة",
            why_now_ar="Pilot يوم ٣: لم يُرفع ملف القطاع.",
            recommended_action_ar="طلب الملف قبل توليد الفرص التالية.",
            risk_level="medium",
            buttons=[
                _btn("اطلب بيانات", "draft_data_request"),
                _btn("إشعار العميل", "draft_client_nudge"),
                _btn("تخطي", "skip"),
            ],
            action_mode="draft_only",
            proof_impact=["delivery_blocked_input", "draft_created"],
        ),
        _card(
            card_id=f"{r}_proof_done",
            role=r,
            ctype=CardType.PROOF.value,
            title_ar="✅ Proof Pack — جاهز للتسليم",
            why_now_ar="اكتملت المهام المتفق عليها للأسبوع.",
            recommended_action_ar="مراجعة داخلية ثم إرسال يدوي للعميل (بدون إرسال تلقائي).",
            risk_level="low",
            buttons=[
                _btn("اعرض الملخص", "open_proof"),
                _btn("سجّل التسليم", "log_delivery"),
                _btn("تخطي", "skip"),
            ],
            action_mode="approval_required",
            proof_impact=["proof_generated", "approval_requested"],
        ),
    ]


_ROLE_BUILDERS: dict[str, list[dict[str, Any]]] = {
    UserRole.CEO.value: _ceo_cards(),
    UserRole.SALES_MANAGER.value: _sales_cards(),
    UserRole.GROWTH_MANAGER.value: _growth_cards(),
    UserRole.AGENCY_PARTNER.value: _agency_cards(),
    UserRole.SUPPORT.value: _support_cards(),
    UserRole.SERVICE_DELIVERY.value: _delivery_cards(),
}


def build_role_command_feed(role: str) -> dict[str, Any]:
    """Return up to MAX_CARDS_VISIBLE normalized cards for ``role``."""
    cards = list(_ROLE_BUILDERS.get(role, []))
    visible = cards[:MAX_CARDS_VISIBLE]
    return {
        "role": role,
        "cards": visible,
        "card_count": len(visible),
        "max_visible": MAX_CARDS_VISIBLE,
        "demo": True,
    }


def build_whatsapp_daily_brief_lines(role: str) -> list[str]:
    """Short lines suitable for WhatsApp (approval-first; no auto-send)."""
    feed = build_role_command_feed(role)
    lines: list[str] = []
    for c in feed["cards"][:3]:
        lines.append(f"• {c['title_ar']}")
    if not lines:
        lines = ["• لا توجد قرارات معروضة لهذا الدور."]
    lines.append("")
    lines.append("افتح لوحة الموافقات للتفاصيل — لا يُرسل شيء تلقائياً من المنصة.")
    return lines
