"""Safe Tool Gateway matrix — execution modes per tool (deterministic)."""

from __future__ import annotations

from typing import Any, Final

MODE_SUGGEST_ONLY: Final = "suggest_only"
MODE_DRAFT_ONLY: Final = "draft_only"
MODE_APPROVAL_REQUIRED: Final = "approval_required"
MODE_APPROVED_EXECUTE: Final = "approved_execute"
MODE_BLOCKED: Final = "blocked"

# tool_id -> default mode when autonomy is draft_and_approve (Dealix beta default)
_TOOL_MATRIX: dict[str, dict[str, Any]] = {
    "gmail_send": {"mode": MODE_BLOCKED, "reason_ar": "إرسال Gmail مباشر محظور افتراضياً."},
    "gmail_draft": {"mode": MODE_DRAFT_ONLY, "reason_ar": "مسودات Gmail مسموحة للمراجعة."},
    "linkedin_scrape": {"mode": MODE_BLOCKED, "reason_ar": "scraping LinkedIn محظور."},
    "linkedin_auto_dm": {"mode": MODE_BLOCKED, "reason_ar": "رسائل LinkedIn آلية محظورة."},
    "cold_whatsapp": {"mode": MODE_BLOCKED, "reason_ar": "واتساب بارد / غير موافق عليه محظور."},
    "whatsapp_opt_in_template": {"mode": MODE_DRAFT_ONLY, "reason_ar": "قوالب opt-in كمسودات."},
    "moyasar_charge": {"mode": MODE_BLOCKED, "reason_ar": "شحن بطاقة من API غير مفعّل."},
    "moyasar_payment_link_draft": {"mode": MODE_DRAFT_ONLY, "reason_ar": "مسودة رابط دفع مسموحة."},
    "google_calendar_insert": {"mode": MODE_APPROVAL_REQUIRED, "reason_ar": "إدراج تقويم يحتاج موافقة."},
    "crm_update": {"mode": MODE_APPROVAL_REQUIRED, "reason_ar": "تحديث CRM بعد موافقة."},
    "google_sheets_export": {"mode": MODE_APPROVAL_REQUIRED, "reason_ar": "تصدير مع موافقة عند الحساسية."},
    "meeting_transcript_read": {"mode": MODE_APPROVAL_REQUIRED, "reason_ar": "قراءة محضر تتطلب نطاقاً وموافقة."},
}


def evaluate_tool(tool_id: str, autonomy_mode: str = "draft_and_approve") -> dict[str, Any]:
    tid = (tool_id or "").strip().lower()
    row = _TOOL_MATRIX.get(tid, {"mode": MODE_APPROVAL_REQUIRED, "reason_ar": "أداة غير مسجّلة — موافقة افتراضية."})
    mode = row["mode"]
    if autonomy_mode in ("manual", "suggest_only") and mode == MODE_APPROVED_EXECUTE:
        mode = MODE_SUGGEST_ONLY
    return {"tool_id": tid, "mode": mode, "reason_ar": row["reason_ar"], "demo": True}


def list_tool_matrix() -> dict[str, Any]:
    return {"tools": [{**{"tool_id": k}, **v} for k, v in _TOOL_MATRIX.items()], "demo": True}
