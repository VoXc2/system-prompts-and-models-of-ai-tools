"""Deterministic policy — no network."""

from __future__ import annotations

from typing import Any, Literal

from core.config.settings import get_settings

PolicyState = Literal["approved", "blocked", "approval_required", "review"]


def evaluate_action(
    *,
    action: str,
    channel_id: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Rules:
    - External-ish sends → approval_required unless explicitly internal draft.
    - Cold WhatsApp → blocked when ``intent`` is cold/campaign_cold.
    - Payment → approval_required + confirm flag if amount present.
    - Unknown channel → review.
    """
    ctx = context or {}
    reason_ar = ""
    state: PolicyState = "approval_required"

    known = {
        "whatsapp",
        "email",
        "linkedin_lead_form",
        "website_form",
        "google_business",
        "x_twitter",
        "instagram",
        "moyasar",
    }
    if channel_id not in known:
        return {
            "state": "review",
            "reason_ar": "قناة غير معروفة في السجل — يلزم مراجعة يدوية.",
            "action": action,
            "channel_id": channel_id,
        }

    if channel_id == "whatsapp" and action in ("send", "send_live", "external_send"):
        intent = str(ctx.get("intent") or "").lower()
        audience = str(ctx.get("audience") or "").lower()
        cold_markers = ("cold", "campaign_cold", "purchased_list", "unknown_opt_in")
        if intent in cold_markers or audience in cold_markers:
            return {
                "state": "blocked",
                "reason_ar": "الواتساب البارد أو قوائم غير موثقة محظور حتى موافقة امتثال وتسجيل opt-in.",
                "action": action,
                "channel_id": channel_id,
            }
        settings = get_settings()
        if action == "send_live" and not settings.whatsapp_allow_live_send:
            return {
                "state": "blocked",
                "reason_ar": "الإرسال الحي للواتساب معطّل في الإعدادات (WHATSAPP_ALLOW_LIVE_SEND=false).",
                "action": action,
                "channel_id": channel_id,
            }

    if action in ("send", "send_live", "external_send", "smtp_send"):
        state = "approval_required"
        reason_ar = "أي إرسال خارجي يتطلب موافقة بشرية في هذا الإصدار."

    if action in ("payment_charge", "payment_capture", "moyasar_charge"):
        state = "approval_required"
        if not ctx.get("user_confirmed"):
            reason_ar = "عمليات الدفع تتطلب تأكيداً صريحاً من المشغّل قبل التنفيذ."
        else:
            reason_ar = "تم تسجيل تأكيد المشغّل — ما زال التنفيذ الفعلي معطّلاً في MVP."

    if action in ("draft_only", "draft_message", "draft_email"):
        state = "approved"
        reason_ar = "مسودة داخلية — مسموح للعرض فقط."

    return {"state": state, "reason_ar": reason_ar or "قرار سياسة افتراضي.", "action": action, "channel_id": channel_id}
