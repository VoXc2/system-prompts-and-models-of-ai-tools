"""Arabic CEO / growth manager cards — max 3 buttons, approval flags."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import list_tower_services


def _card(
    title_ar: str,
    summary_ar: str,
    buttons: list[str],
    approval_required: bool,
) -> dict[str, Any]:
    btns = (buttons or [])[:3]
    return {
        "title_ar": title_ar,
        "summary_ar": summary_ar,
        "buttons": btns,
        "approval_required": approval_required,
        "live_send": False,
    }


def build_ceo_daily_service_brief() -> dict[str, Any]:
    data = list_tower_services()
    n = int(data.get("count") or 0)
    return {
        "greeting_ar": "صباح الخير — موجز خدمات Dealix.",
        "highlights_ar": [
            f"عدد الخدمات في البرج: {n}.",
            "٣ مسودات بانتظار موافقتك (تجريبي).",
            "لا إرسال حي من النظام افتراضياً.",
        ],
        "cards": [
            _card(
                "اعتماد مسودات",
                "هناك مسودات جاهزة للمراجعة قبل أي تواصل خارجي.",
                ["اعرض المسودات", "لاحقاً", "تخطي"],
                True,
            ),
            _card(
                "مخاطر قناة",
                "قناة واحدة تحتاج تهدئة حسب سمعة الإرسال (تجريبي).",
                ["افتح التفاصيل", "خفّض الحجم", "تجاهل"],
                True,
            ),
        ],
        "demo": True,
    }


def build_service_approval_card(service_id: str, action: str) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "action": action,
        "card": _card(
            f"موافقة: {service_id}",
            f"الإجراء المقترح: {action} — لن يُنفَّذ إلا بعد اعتمادك.",
            ["اعتمد", "عدّل", "ألغِ"],
            True,
        ),
        "demo": True,
    }


def build_risk_alert_card() -> dict[str, Any]:
    return {
        "card": _card(
            "تنبيه مخاطر",
            "تم رصد أرقام بحاجة مراجعة مصدر قبل واتساب.",
            ["راجع القائمة", "صدّر الممنوع", "لاحقاً"],
            True,
        ),
        "demo": True,
    }


def build_end_of_day_service_report() -> dict[str, Any]:
    return {
        "title_ar": "تقرير نهاية اليوم — الخدمات",
        "lines_ar": [
            "المسودات المعتمدة: ٢ (تجريبي).",
            "الاجتماعات المقترحة: ١.",
            "المخاطر التي تم منعها: ٤.",
        ],
        "live_send": False,
        "demo": True,
    }
