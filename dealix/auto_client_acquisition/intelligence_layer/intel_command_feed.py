"""Intel-specific command cards — unified schema for Arabic decision UI."""

from __future__ import annotations

from typing import Any


def normalize_intel_card(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Unified card shape: Arabic titles, <=3 buttons, no live actions.

    Accepts either pre-normalized dicts or legacy keys (``cta_ar``, ``summary_ar``).
    """
    title_ar = str(raw.get("title_ar") or "")
    summary_ar = str(raw.get("summary_ar") or "")
    why_it_matters_ar = str(raw.get("why_it_matters_ar") or summary_ar)
    recommended_action_ar = str(
        raw.get("recommended_action_ar")
        or raw.get("suggested_action")
        or raw.get("cta_ar")
        or raw.get("cta")
        or "مراجعة المسودة"
    )
    risk_level = str(raw.get("risk_level") or "medium")
    try:
        expected_impact_sar = float(raw.get("expected_impact_sar") or 0)
    except (TypeError, ValueError):
        expected_impact_sar = 0.0

    buttons_in = raw.get("buttons")
    buttons: list[dict[str, str]] = []
    if isinstance(buttons_in, list) and buttons_in and isinstance(buttons_in[0], dict):
        for b in buttons_in[:3]:
            label = str(b.get("label_ar") or b.get("label") or "")
            aid = str(b.get("action_id") or b.get("id") or "action")
            if label:
                buttons.append({"label_ar": label, "action_id": aid})
    elif isinstance(buttons_in, list) and buttons_in and isinstance(buttons_in[0], str):
        for i, label in enumerate(buttons_in[:3]):
            buttons.append({"label_ar": str(label), "action_id": f"btn_{i}"})
    else:
        cta = str(raw.get("cta_ar") or raw.get("cta") or "مراجعة")
        buttons = [
            {"label_ar": cta, "action_id": "primary"},
            {"label_ar": "تعديل", "action_id": "edit"},
            {"label_ar": "تخطي", "action_id": "skip"},
        ]

    return {
        "type": str(raw.get("type") or "generic"),
        "title_ar": title_ar,
        "summary_ar": summary_ar,
        "why_it_matters_ar": why_it_matters_ar,
        "recommended_action_ar": recommended_action_ar,
        "risk_level": risk_level,
        "expected_impact_sar": expected_impact_sar,
        "buttons": buttons[:3],
        "approval_required": bool(raw.get("approval_required", True)),
    }


def build_intel_command_feed(context: dict[str, Any] | None = None) -> dict[str, Any]:
    ctx = context or {}
    raw_cards: list[dict[str, Any]] = [
        {
            "type": "revenue_leak",
            "title_ar": "تسرب إيراد — غياب متابعة موحّدة",
            "summary_ar": "ثلاث صفقات بدون موعد تالي خلال ٧ أيام؛ خطر فقدان ١٥٪ من القيمة الموزونة.",
            "why_it_matters_ar": "التأخير يقلل احتمال الرد والإغلاق خلال نافذة الشراء.",
            "recommended_action_ar": "جدولة متابعة قصيرة مع خيار إيقاف.",
            "risk_level": "medium",
            "expected_impact_sar": 42000.0,
            "buttons": [
                {"label_ar": "اعتمد", "action_id": "approve"},
                {"label_ar": "عدّل", "action_id": "edit"},
                {"label_ar": "تخطي", "action_id": "skip"},
            ],
            "approval_required": True,
        },
        {
            "type": "board_brief",
            "title_ar": "موجز للمجلس — قرار واحد هذا الأسبوع",
            "summary_ar": "الموافقة على نطاق pilot ثانٍ في قطاع الصحة أو تجميد التوسع لصيانة الجودة.",
            "why_it_matters_ar": "التركيز يحمي الجودة ويُسرّع إثبات القيمة للعميل.",
            "recommended_action_ar": "عرض موجز قرار واحد صفحة واحدة.",
            "risk_level": "low",
            "expected_impact_sar": 0.0,
            "buttons": [
                {"label_ar": "عرض الموجز", "action_id": "open_brief"},
                {"label_ar": "تأجيل", "action_id": "snooze"},
                {"label_ar": "إغلاق", "action_id": "dismiss"},
            ],
            "approval_required": True,
        },
    ]
    if ctx.get("append_custom") and isinstance(ctx["append_custom"], dict):
        raw_cards.append(ctx["append_custom"])
    cards = [normalize_intel_card(x) for x in raw_cards]
    return {"cards": cards, "source": "intelligence_layer", "demo": True}
