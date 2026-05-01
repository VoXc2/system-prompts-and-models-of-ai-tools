"""تحليل غرفة صفقة تجريبي — derivation بسيط من الجسم."""

from __future__ import annotations


def analyze_deal_room(payload: dict[str, object] | None = None) -> dict[str, object]:
    """
    يُحلّل جسم الطلب بشكل بسيط (deterministic).

    الحقول: deal_id, risk_score, missing_info, next_action_ar, stakeholders_hint.
    """
    body = payload or {}
    deal_id = str(body.get("deal_id") or "demo-deal-unknown")
    stage = str(body.get("stage") or "discovery")
    notes = str(body.get("notes") or "")

    risk_score = 35
    if "تأجيل" in notes or "later" in notes.lower():
        risk_score += 25
    if stage in ("proposal", "negotiation"):
        risk_score -= 10
    risk_score = max(0, min(100, risk_score))

    missing_info: list[str] = []
    if not body.get("budget_range"):
        missing_info.append("نطاق الميزانية أو سلطة القرار المالية")
    if not body.get("decision_date"):
        missing_info.append("تاريخ قرار متوقع أو حد أقصى للمناقصة")
    if len(notes) < 10:
        missing_info.append("ملخص محضر آخر اجتماع")

    stakeholders_hint = ["مالك قرار تقني", "مشتري/مالية"]
    if stage == "discovery":
        stakeholders_hint.append("مستخدم نهائي محتمل")

    next_action_ar = (
        "أرسل ملخصاً قصيراً مع خطوة تالية وتاريخاً مقترحاً؛ اطلب تأكيداً خطّياً."
        if risk_score >= 50
        else "ثبّت جلسة معرضاً تقنياً قصيراً خلال ٧ أيام مع قائمة أسئلة مغلقة."
    )

    return {
        "deal_id": deal_id,
        "risk_score": risk_score,
        "missing_info": missing_info,
        "next_action_ar": next_action_ar,
        "stakeholders_hint": stakeholders_hint,
        "stage_echo": stage,
    }
