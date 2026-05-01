"""مهام نمو قابلة للعرض — deterministic."""

from __future__ import annotations

_KILL_TITLE = "10 فرص في 10 دقائق"


def list_growth_missions() -> dict[str, object]:
    """
    مهام نمو تجريبية تشمل Kill feature صريحاً.

    Kill feature: «10 فرص في 10 دقائق» — خطوات وحقول إدخال متوقعة دون تنفيذ شبكة.
    """
    missions: list[dict[str, object]] = [
        {
            "id": "book_three_meetings",
            "title_ar": "احجز ٣ اجتماعات مؤهّلة هذا الأسبوع",
            "steps_ar": [
                "حدّد قطاعاً ومدينة واحدة.",
                "صفِّ الفرص حسب إشارة Why Now.",
                "أرسل مسودات مع موافقة؛ تابع خلال ٤٨ ساعة.",
            ],
            "expected_inputs": ["sector", "city", "offer_summary"],
            "is_kill_feature": False,
        },
        {
            "id": "fix_pipeline_leaks",
            "title_ar": "أصلح تسريبات خط الأنابيب",
            "steps_ar": [
                "امسح المراحل بدون خطوة تالية خلال ٧ أيام.",
                "ولِّد مسودات متابعة قصيرة.",
                "سجّل كل إجراء في Proof Ledger.",
            ],
            "expected_inputs": ["pipeline_snapshot_or_manual_stage_list"],
            "is_kill_feature": False,
        },
        {
            "id": "expand_vertical",
            "title_ar": "توسّع قطاع واحد بجدول ١٤ يوماً",
            "steps_ar": [
                "اختر قطاعاً ذا صلة بالعرض الحالي.",
                "اضبط playbook قطاعي من Vertical OS.",
                "شغّل تجربة رسالة واحدة وقيّم الأسبوع القادم.",
            ],
            "expected_inputs": ["vertical_key", "weekly_capacity"],
            "is_kill_feature": False,
        },
        {
            "id": "ten_opps_ten_minutes",
            "title_ar": _KILL_TITLE,
            "steps_ar": [
                "أدخل: اسم الشركة أو الموقع، القطاع، المدينة، العرض، الهدف.",
                "يُولَّد قائمة ١٠ فرص مع Why Now ومستوى مخاطرة ولغة عربية مهنية.",
                "راجع المسودات؛ وافق أو تخطَّ؛ خطّط متابعة أسبوعية.",
                "صدّر قالب proof للأسبوع الأول.",
            ],
            "expected_inputs": [
                "company_name_or_url",
                "sector",
                "city",
                "offer_one_liner",
                "goal_meetings_or_replies",
            ],
            "is_kill_feature": True,
            "api_hint": "/api/v1/innovation/growth-missions",
        },
    ]
    return {"missions": missions, "kill_feature_title": _KILL_TITLE}
