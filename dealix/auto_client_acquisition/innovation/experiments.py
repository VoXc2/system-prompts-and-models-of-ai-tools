"""اقتراح تجارب إيراد شهرية — deterministic من السياق وتاريخ تجارب سابقة."""

from __future__ import annotations

from typing import Any


def _past_failed(past: list[dict[str, Any]], metric_substr: str) -> bool:
    for item in past:
        m = str(item.get("metric") or "").lower()
        outcome = str(item.get("outcome") or "").lower()
        if metric_substr.lower() in m and outcome in ("fail", "failed", "failure", "negative", "no_lift"):
            return True
    return False


def recommend_experiments(context: dict[str, object] | None = None) -> dict[str, object]:
    """
    يُرجع ثلاث تجارب شهرية بصيغة موحّدة.

    الحقول لكل تجربة: hypothesis, metric, action, risk, horizon_days.

    إذا وُجدت ``past_experiments`` في السياق (قائمة من dict تحتوي outcome وmetric)،
    تُعدّل التوصيات بقواعد بسيطة دون تعلم آلي.
    """
    ctx = dict(context or {})
    sector = str(ctx.get("sector") or "القطاع الحالي")
    past_raw = ctx.get("past_experiments")
    past: list[dict[str, Any]] = list(past_raw) if isinstance(past_raw, list) else []

    base_experiments: list[dict[str, object]] = [
        {
            "hypothesis": f"اختصار الرسالة الأولى يزيد الردود في {sector}",
            "metric": "reply_rate_7d",
            "action": "قارن نسختين (<=280 حرفاً مقابل نسخة أطول) على عينة ٥٠ جهة.",
            "risk": "قد يقل الوضوح؛ راجع موافقة قبل الإرسال.",
            "horizon_days": 30,
        },
        {
            "hypothesis": "متابعة يوم ثالث بدلاً من اليوم الثاني تحسّن جودة الاجتماعات",
            "metric": "meetings_booked_per_100_outreach",
            "action": "أخرِ التذكير ٢٤ ساعة لمجموعة واحدة فقط.",
            "risk": "تأخير قد يخسر فرص حارة؛ صغّر العينة.",
            "horizon_days": 30,
        },
        {
            "hypothesis": "إرفاق جملة Why Now ترفع قبول المسودات من الموافِق",
            "metric": "approval_rate_first_pass",
            "action": "أضف سطراً واحداً من الإشارة في كل مسودة لأسبوعين.",
            "risk": "إشارات قديمة تقلل الثقة؛ تحقق يدوي من المصدر.",
            "horizon_days": 30,
        },
    ]

    if ctx.get("focus") == "compliance":
        base_experiments[0] = {
            "hypothesis": "فحص قائمة القمع قبل كل دفعة يقلل حوادث الإرسال",
            "metric": "blocked_or_review_events_avoided",
            "action": "فعّل خطوة مراجعة إضافية لمجموعة ٢٠٠ جهة.",
            "risk": "زمن الموافقة أطول؛ حدد SLA داخلياً.",
            "horizon_days": 30,
        }

    adaptation_notes: list[str] = []
    if _past_failed(past, "reply_rate"):
        base_experiments[0] = {
            "hypothesis": "تقسيم الرسالة إلى نقطتين (قيمة ثم طلب) يحسّن الرد رغم ضعف النسخ القصيرة سابقاً",
            "metric": "reply_rate_7d",
            "action": "جرّب هيكل «مشكلة—نتيجة—سؤال واحد» على ٤٠ جهة مع موافقة.",
            "risk": "قد يطول النص؛ راقب حدود القناة.",
            "horizon_days": 30,
        }
        adaptation_notes.append("past_reply_rate_failure")
    if _past_failed(past, "meetings_booked"):
        base_experiments[1] = {
            "hypothesis": "تسريع المتابعة خلال ٢٤ ساعة بعد الرد يعوض ضعف تجربة «تأخير المتابعة»",
            "metric": "meetings_booked_per_100_outreach",
            "action": "مهمة SLA داخلية: رد بشري أو مسودة خلال ٢٤ ساعة لمجموعة صغيرة.",
            "risk": "ضغط تشغيلي على الفريق.",
            "horizon_days": 30,
        }
        adaptation_notes.append("past_meetings_failure")
    if _past_failed(past, "approval_rate"):
        base_experiments[2] = {
            "hypothesis": "قالب موافقة مسبق (نقاط حمراء) يقلل الدورات رغم رفض المسودات السابقة",
            "metric": "approval_rate_first_pass",
            "action": "أضف ٣ أسئلة نعم/لا قبل إرسال المسودة للموافِق.",
            "risk": "مزيد من الاحتكاك؛ اختصر القالب.",
            "horizon_days": 30,
        }
        adaptation_notes.append("past_approval_failure")

    ctx_out = {**ctx, "adaptation_notes": adaptation_notes}
    return {"experiments": base_experiments, "context_echo": ctx_out}
