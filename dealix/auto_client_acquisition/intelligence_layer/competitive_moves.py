"""Competitive Move Detector — analyze competitor activity → suggest action."""

from __future__ import annotations

from typing import Any


MOVE_TYPES: tuple[str, ...] = (
    "price_change",
    "new_offer",
    "hiring",
    "event",
    "content_campaign",
    "rebrand",
    "funding",
    "expansion",
)


def analyze_competitive_move(
    *,
    competitor_name: str,
    move_type: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Take one observed competitor signal → return Arabic recommended action.

    Pure deterministic; no live competitor scraping.
    """
    p = payload or {}
    if move_type not in MOVE_TYPES:
        return {
            "error": f"unknown move_type: {move_type}",
            "valid_types": list(MOVE_TYPES),
        }

    if move_type == "price_change":
        delta_pct = float(p.get("price_delta_pct", -10))
        action_ar = (
            "حملة مضادة + ROI breakdown مقارن — لا تخفّض السعر."
            if delta_pct < 0 else
            "ميزة تنافسية: عرضنا أرخص — اطلق ROI proof."
        )
        urgency = "high" if abs(delta_pct) >= 15 else "medium"
    elif move_type == "new_offer":
        action_ar = (
            "حلّل العرض الجديد + اقتباس مزاياك المختلفة + offer comparison."
        )
        urgency = "medium"
    elif move_type == "hiring":
        action_ar = (
            "إشارة توسع — استهدف نفس عملائهم بعرضك المختلف."
        )
        urgency = "low"
    elif move_type == "event":
        action_ar = (
            "حضّر أنت محتوى/ندوة في نفس الفترة — استفد من اهتمام السوق."
        )
        urgency = "medium"
    elif move_type == "content_campaign":
        action_ar = (
            "اقرأ زاويتهم + اطلق رد منشور / dialog بحجة مدعومة بأرقام."
        )
        urgency = "low"
    elif move_type == "rebrand":
        action_ar = "احتفظ بهويتك — أعلن استمرار وعدك للعملاء."
        urgency = "low"
    elif move_type == "funding":
        action_ar = (
            "إشارة سرعة في السوق — ركّز على retention + speed-to-value."
        )
        urgency = "medium"
    else:  # expansion
        action_ar = "نبّه فريق المبيعات + رسالة احتفاظ للعملاء الكبار."
        urgency = "medium"

    return {
        "competitor_name": competitor_name,
        "move_type": move_type,
        "urgency": urgency,
        "recommended_action_ar": action_ar,
        "next_step_ar": "جهّز draft رد + موافقة المشغّل قبل الإطلاق.",
        "approval_required": True,
        "payload_received": p,
    }
