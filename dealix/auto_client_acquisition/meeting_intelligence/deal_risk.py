"""Deal risk score from meeting + objection signals."""

from __future__ import annotations

from typing import Any


def compute_deal_risk(
    *,
    objections: list[dict[str, Any]] | None = None,
    next_step_set: bool = False,
    decision_maker_present: bool = False,
    days_since_last_touch: int = 0,
    expected_value_sar: float = 0.0,
) -> dict[str, Any]:
    """
    Compute a deal-level risk score (0..100) from meeting outcomes.

    Higher = riskier. Returns deterministic Arabic risk reasons.
    """
    objections = objections or []
    score = 0
    reasons_ar: list[str] = []

    # Objection-based risk.
    categories = {str(o.get("category", "")).lower() for o in objections}
    if "price" in categories:
        score += 20
        reasons_ar.append("اعتراض على السعر — يحتاج إثبات قيمة وعينة محسوبة.")
    if "timing" in categories:
        score += 15
        reasons_ar.append("اعتراض توقيت — احفظ الفرصة لربع لاحق.")
    if "authority" in categories:
        score += 25
        reasons_ar.append("صاحب القرار غير حاضر — يلزم اجتماع ثانٍ معه.")
    if "trust" in categories:
        score += 20
        reasons_ar.append("قلق أمان/خصوصية — أرفق DPA و PDPL.")
    if "integration" in categories:
        score += 10
        reasons_ar.append("قلق تكامل — حضّر مخطط ربط CRM.")
    if "competitor" in categories:
        score += 15
        reasons_ar.append("بديل قائم — جهّز battlecard مقارنة.")

    # Process risk.
    if not next_step_set:
        score += 25
        reasons_ar.append("لم يتم تحديد خطوة تالية بتاريخ — أعلى مؤشر فقدان.")
    if not decision_maker_present:
        score += 10
        reasons_ar.append("صانع القرار لم يحضر الاجتماع.")
    if days_since_last_touch > 14:
        score += 10
        reasons_ar.append(
            f"مرّ {days_since_last_touch} يوم على آخر تواصل — فرصة باردة."
        )

    # Cap.
    score = max(0, min(100, score))

    if score >= 70:
        risk_level = "high"
    elif score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "reasons_ar": reasons_ar,
        "expected_value_sar": expected_value_sar,
        "recommended_action_ar": (
            "اجتماع ثانٍ مع صاحب القرار خلال 5 أيام + مادة إثبات قيمة قصيرة."
            if risk_level == "high" else
            "متابعة خلال 3 أيام مع خطوة تالية محددة."
            if risk_level == "medium" else
            "تنفيذ الخطوة التالية المتفق عليها كما هي."
        ),
    }
