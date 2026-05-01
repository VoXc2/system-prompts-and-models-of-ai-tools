"""Event → Arabic inbox card (≤3 actions)."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.innovation.command_feed import build_demo_command_feed
from auto_client_acquisition.platform_services.event_bus import EventType


def _trim_actions(actions: list[dict[str, str]], max_n: int = 3) -> list[dict[str, str]]:
    return actions[:max_n]


def event_to_inbox_card(event: dict[str, Any], *, merge_demo_hint: bool = False) -> dict[str, Any]:
    """Build ``title_ar``, ``summary_ar``, and up to three action buttons."""
    et_raw = event.get("event_type")
    try:
        et = EventType(str(et_raw))
    except (ValueError, TypeError):
        return {
            "title_ar": "حدث غير صالح",
            "summary_ar": "تعذر بناء البطاقة — نوع الحدث غير معروف.",
            "actions": _trim_actions([{"action_id": "dismiss", "label_ar": "إغلاق"}]),
        }

    actions: list[dict[str, str]] = []
    title_ar = ""
    summary_ar = ""

    if et == EventType.LEAD_RECEIVED:
        src = str(event.get("source") or "")
        name = str(event.get("lead_name") or "جهة جديدة")
        title_ar = "عميل محتمل جديد"
        summary_ar = f"مصدر: {src}. الاسم: {name}."
        actions = [
            {"action_id": "qualify", "label_ar": "تأهيل سريع"},
            {"action_id": "assign_owner", "label_ar": "تعيين مالك"},
            {"action_id": "archive", "label_ar": "أرشفة"},
        ]
    elif et == EventType.EXTERNAL_SEND_REQUESTED:
        title_ar = "طلب إرسال خارجي"
        summary_ar = f"القناة: {event.get('channel_id')}. الإجراء: {event.get('action')}."
        actions = [
            {"action_id": "approve_send", "label_ar": "موافقة مشروطة"},
            {"action_id": "edit_draft", "label_ar": "تعديل المسودة"},
            {"action_id": "reject", "label_ar": "رفض"},
        ]
    elif et == EventType.PAYMENT_INTENT:
        title_ar = "نية دفع"
        summary_ar = f"المبلغ (هللات): {event.get('amount_halalas')} {event.get('currency', 'SAR')}."
        actions = [
            {"action_id": "confirm_payment", "label_ar": "تأكيد المشغّل"},
            {"action_id": "adjust_amount", "label_ar": "تعديل المبلغ"},
            {"action_id": "cancel", "label_ar": "إلغاء"},
        ]
    elif et == EventType.WHATSAPP_MESSAGE_REQUESTED:
        title_ar = "طلب رسالة واتساب"
        summary_ar = f"النية: {event.get('intent')} — الجمهور: {event.get('audience')}."
        actions = [
            {"action_id": "preview_template", "label_ar": "معاينة القالب"},
            {"action_id": "require_optin_proof", "label_ar": "طلب إثبات opt-in"},
            {"action_id": "block", "label_ar": "إيقاف"},
        ]
    elif et == EventType.REVIEW_REQUIRED:
        title_ar = "مراجعة يدوية"
        summary_ar = f"السبب: {event.get('reason_code')}."
        actions = [
            {"action_id": "open_queue", "label_ar": "فتح الطابور"},
            {"action_id": "assign", "label_ar": "إسناد"},
            {"action_id": "snooze", "label_ar": "تأجيل"},
        ]
    elif et == EventType.EMAIL_RECEIVED:
        title_ar = "إيميل شركة جديد"
        summary_ar = f"الموضوع: {event.get('subject_ar')} — القناة: {event.get('channel_id')}."
        actions = [
            {"action_id": "gmail_draft_reply", "label_ar": "جهّز مسودة رد"},
            {"action_id": "classify_lead", "label_ar": "صنّف كفرصة"},
            {"action_id": "snooze_email", "label_ar": "تأجيل"},
        ]
    elif et == EventType.CALENDAR_MEETING_SCHEDULED:
        title_ar = "اجتماع في التقويم"
        summary_ar = f"{event.get('title_ar')} — {event.get('channel_id')}."
        actions = [
            {"action_id": "meeting_prep", "label_ar": "تحضير"},
            {"action_id": "calendar_draft", "label_ar": "مسودة تعديل"},
            {"action_id": "ignore_meeting", "label_ar": "تخطي"},
        ]
    elif et == EventType.SOCIAL_COMMENT_RECEIVED:
        title_ar = "تعليق على منشور"
        summary_ar = str(event.get("snippet_ar") or "")[:200]
        actions = [
            {"action_id": "draft_reply", "label_ar": "رد مسودة"},
            {"action_id": "escalate", "label_ar": "تصعيد"},
            {"action_id": "dismiss_social", "label_ar": "تجاهل"},
        ]
    elif et == EventType.SOCIAL_DM_RECEIVED:
        title_ar = "رسالة خاصة (سوشيال)"
        summary_ar = f"من: {event.get('sender_hint')} — {event.get('channel_id')}."
        actions = [
            {"action_id": "policy_check", "label_ar": "فحص سياسة"},
            {"action_id": "draft_dm", "label_ar": "مسودة رد"},
            {"action_id": "block_channel", "label_ar": "إيقاف القناة"},
        ]
    elif et == EventType.LEAD_FORM_SUBMITTED:
        title_ar = "نموذج ليد جديد"
        summary_ar = f"مصدر: {event.get('source')} — قناة: {event.get('channel_id')}."
        actions = [
            {"action_id": "qualify", "label_ar": "تأهيل"},
            {"action_id": "import_crm", "label_ar": "مسودة CRM"},
            {"action_id": "archive", "label_ar": "أرشفة"},
        ]
    elif et == EventType.PAYMENT_PAID:
        title_ar = "دفعة مؤكدة"
        summary_ar = f"المبلغ (هللات): {event.get('amount_halalas')} {event.get('currency', 'SAR')}."
        actions = [
            {"action_id": "proof_ledger", "label_ar": "سجّل في Proof"},
            {"action_id": "thank_you_draft", "label_ar": "شكر مسودة"},
            {"action_id": "upsell_draft", "label_ar": "عرض ترقية"},
        ]
    elif et == EventType.PAYMENT_FAILED:
        title_ar = "دفعة فاشلة"
        summary_ar = f"السبب: {event.get('reason_code')} — المبلغ: {event.get('amount_halalas')}."
        actions = [
            {"action_id": "retry_draft", "label_ar": "مسودة متابعة"},
            {"action_id": "support_ticket", "label_ar": "تذكرة دعم"},
            {"action_id": "close_payment", "label_ar": "إغلاق"},
        ]
    elif et == EventType.REVIEW_CREATED:
        title_ar = "تقييم جديد (سمعة محلية)"
        summary_ar = f"التقييم: {event.get('rating')} — {event.get('channel_id')}."
        actions = [
            {"action_id": "draft_review_reply", "label_ar": "رد مسودة"},
            {"action_id": "escalate_mgr", "label_ar": "تصعيد مدير"},
            {"action_id": "monitor", "label_ar": "مراقبة"},
        ]
    elif et == EventType.PARTNER_SUGGESTED:
        title_ar = "اقتراح شريك"
        summary_ar = f"{event.get('partner_name_ar')} — قطاع {event.get('sector')}."
        actions = [
            {"action_id": "partner_draft", "label_ar": "رسالة شريك"},
            {"action_id": "schedule_call", "label_ar": "مسودة اجتماع"},
            {"action_id": "skip_partner", "label_ar": "تخطي"},
        ]
    elif et == EventType.ACTION_APPROVED:
        title_ar = "تمت الموافقة على إجراء"
        summary_ar = f"{event.get('action_id')} — بواسطة {event.get('actor')}."
        actions = [
            {"action_id": "view_ledger", "label_ar": "عرض السجل"},
            {"action_id": "notify_team", "label_ar": "إشعار داخلي"},
            {"action_id": "done", "label_ar": "تم"},
        ]
    elif et == EventType.ACTION_BLOCKED:
        title_ar = "إجراء ممنوع"
        summary_ar = f"{event.get('action_id')} — {event.get('reason_code')}."
        actions = [
            {"action_id": "edit_policy", "label_ar": "مراجعة سياسة"},
            {"action_id": "appeal", "label_ar": "طلب استثناء"},
            {"action_id": "dismiss", "label_ar": "إغلاق"},
        ]
    elif et == EventType.DRAFT_CREATED:
        title_ar = "مسودة جاهزة"
        summary_ar = f"النوع: {event.get('draft_kind')}."
        actions = [
            {"action_id": "open_draft", "label_ar": "فتح المسودة"},
            {"action_id": "share", "label_ar": "مشاركة داخلية"},
            {"action_id": "discard", "label_ar": "تجاهل"},
        ]
    else:
        title_ar = "حدث داخلي"
        summary_ar = "نوع مسجّل لكن بدون قالب عرض — راجع الإعدادات."
        actions = [
            {"action_id": "dismiss", "label_ar": "إغلاق"},
            {"action_id": "log", "label_ar": "تسجيل"},
            {"action_id": "help", "label_ar": "مساعدة"},
        ]

    card: dict[str, Any] = {
        "title_ar": title_ar,
        "summary_ar": summary_ar,
        "actions": _trim_actions(actions),
        "event_type": et.value,
    }
    if merge_demo_hint:
        demo = build_demo_command_feed()
        cards = demo.get("cards") if isinstance(demo.get("cards"), list) else []
        if cards and isinstance(cards[0], dict):
            card["demo_hint_ar"] = str(cards[0].get("title_ar") or "")
    return card
