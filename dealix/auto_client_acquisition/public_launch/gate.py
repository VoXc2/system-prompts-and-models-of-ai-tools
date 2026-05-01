"""Public Launch Gate — evaluates 9 deterministic criteria.

The gate is the formal transition from Paid Beta to Public Launch.
All criteria must be deterministic (no LLM, no network) so that the
verdict is reproducible in CI and in the dashboard.

Criteria (from PAID_BETA_OPERATING_PLAYBOOK §8):
  1. ≥5 pilots completed (delivered Proof Pack within 7 days)
  2. ≥2 paid customers (Moyasar invoice paid OR signed Growth OS)
  3. 0 unsafe sends (no live action without approval in audit ledger)
  4. Weekly Proof Pack cadence (≥3 weeks consecutive)
  5. Support flow operational (avg first response < SLA)
  6. Funnel visible (lead → demo → pilot → paid measurable)
  7. ≥14 days staging stable (uptime ≥ 99% over 14 days)
  8. Billing live (Moyasar webhook signed and verified)
  9. Legal complete (Terms + Privacy + DPA published)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class GateCriterion:
    """Definition of a single Public Launch criterion."""
    key: str
    name_ar: str
    threshold: float | int | bool
    unit: str
    description_ar: str


PUBLIC_LAUNCH_CRITERIA: tuple[GateCriterion, ...] = (
    GateCriterion(
        key="pilots_completed",
        name_ar="Pilots مكتملة",
        threshold=5,
        unit="count",
        description_ar="عدد Pilots التي سُلّم لها Proof Pack نهائي خلال 7 أيام",
    ),
    GateCriterion(
        key="paid_customers",
        name_ar="عملاء مدفوعون",
        threshold=2,
        unit="count",
        description_ar="عملاء دفعوا فعلياً عبر Moyasar أو وقّعوا Growth OS",
    ),
    GateCriterion(
        key="unsafe_sends",
        name_ar="إرسال غير آمن",
        threshold=0,
        unit="count",
        description_ar="عدد الأفعال الـ live بدون اعتماد بشري في Action Ledger (يجب = 0)",
    ),
    GateCriterion(
        key="proof_cadence_weeks",
        name_ar="استمرارية Proof Pack",
        threshold=3,
        unit="weeks_consecutive",
        description_ar="عدد الأسابيع المتتالية التي صدر فيها Proof Pack",
    ),
    GateCriterion(
        key="support_first_response_minutes_p1",
        name_ar="استجابة Support P1",
        threshold=120,
        unit="minutes",
        description_ar="متوسط استجابة P1 ≤ 120 دقيقة (هدف SLA)",
    ),
    GateCriterion(
        key="funnel_visible",
        name_ar="Funnel مرئي",
        threshold=True,
        unit="bool",
        description_ar="lead→demo→pilot→paid قابل للقياس في Operating Board",
    ),
    GateCriterion(
        key="staging_uptime_days",
        name_ar="استقرار Staging",
        threshold=14,
        unit="days_uptime_99",
        description_ar="عدد الأيام المتتالية بـ uptime ≥ 99% على staging",
    ),
    GateCriterion(
        key="billing_webhook_verified",
        name_ar="Moyasar webhook موثّق",
        threshold=True,
        unit="bool",
        description_ar="Moyasar webhook signed وتم تحقق التوقيع",
    ),
    GateCriterion(
        key="legal_complete",
        name_ar="القانوني مكتمل",
        threshold=True,
        unit="bool",
        description_ar="Terms of Service + Privacy Policy + DPA منشورة بالعربي والإنجليزي",
    ),
)


@dataclass
class GateVerdict:
    """Result of evaluating Public Launch readiness."""
    decision: str  # "GO_PUBLIC_LAUNCH" | "NO_GO" | "BLOCKED"
    score_passed: int
    score_total: int
    blockers: list[Mapping[str, Any]]
    next_actions_ar: list[str]
    criteria_results: list[Mapping[str, Any]]
    summary_ar: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _check_criterion(crit: GateCriterion, value: Any) -> tuple[bool, str]:
    """Compare actual value against threshold. Return (passed, reason_ar)."""
    if crit.unit == "bool":
        passed = bool(value) is bool(crit.threshold)
        if passed:
            return True, "متحقّق"
        return False, f"يجب أن يكون {crit.threshold}"

    if crit.key == "unsafe_sends":
        # Unique: lower is better. Threshold = 0 means must equal 0.
        try:
            v = int(value)
        except (TypeError, ValueError):
            return False, "قيمة غير صحيحة"
        return (v == 0, f"وُجد {v} (يجب = 0)" if v != 0 else "0 إرسال غير آمن")

    if crit.key == "support_first_response_minutes_p1":
        # Lower is better. Threshold is the maximum.
        try:
            v = float(value)
        except (TypeError, ValueError):
            return False, "قيمة غير صحيحة"
        return (
            v <= crit.threshold,
            f"{v:.0f} دقيقة (الحد الأعلى {crit.threshold})",
        )

    # Default: numeric, higher is better.
    try:
        v = float(value)
    except (TypeError, ValueError):
        return False, "قيمة غير صحيحة"
    return (
        v >= crit.threshold,
        f"{int(v) if v.is_integer() else v}/{crit.threshold} {crit.unit}",
    )


def _next_action_for(crit: GateCriterion, value: Any) -> str | None:
    """Generate Arabic next-action when a criterion fails."""
    if crit.key == "pilots_completed":
        return f"شغّل {int(crit.threshold) - int(value or 0)} Pilots إضافية مع Proof Pack مكتمل."
    if crit.key == "paid_customers":
        return f"اقفل {int(crit.threshold) - int(value or 0)} عميل مدفوع إضافي (Moyasar أو Growth OS)."
    if crit.key == "unsafe_sends":
        return "راجع Action Ledger، أوقف القناة المعنية، نفّذ post-mortem فوراً."
    if crit.key == "proof_cadence_weeks":
        return "أصدر Proof Pack أسبوعياً متتالياً حتى تصل 3 أسابيع متتالية."
    if crit.key == "support_first_response_minutes_p1":
        return "حسّن SLA — قلّل first-response P1 إلى ≤120 دقيقة."
    if crit.key == "funnel_visible":
        return "افتح Operating Board مع كل الأعمدة الـ15 وحدّثه يومياً."
    if crit.key == "staging_uptime_days":
        return f"حافظ على staging stable حتى تصل {int(crit.threshold)} يوم متتالي بـ uptime ≥99%."
    if crit.key == "billing_webhook_verified":
        return "فعّل Moyasar webhook signature verification + اختبر بـ test payload."
    if crit.key == "legal_complete":
        return "انشر Terms + Privacy + DPA باللغتين العربية والإنجليزية على الموقع."
    return None


def evaluate_public_launch_gate(
    state: Mapping[str, Any],
    criteria: Sequence[GateCriterion] | None = None,
) -> GateVerdict:
    """Evaluate Public Launch readiness.

    Args:
        state: dict mapping criterion key → measured value.
        criteria: optional override (defaults to PUBLIC_LAUNCH_CRITERIA).

    Returns:
        GateVerdict with decision, score, blockers, and Arabic next actions.
    """
    crits = criteria or PUBLIC_LAUNCH_CRITERIA
    results: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    actions: list[str] = []
    passed_count = 0

    for c in crits:
        value = state.get(c.key)
        ok, reason = _check_criterion(c, value)
        result = {
            "key": c.key,
            "name_ar": c.name_ar,
            "passed": ok,
            "value": value,
            "threshold": c.threshold,
            "unit": c.unit,
            "reason_ar": reason,
        }
        results.append(result)
        if ok:
            passed_count += 1
        else:
            blockers.append(result)
            action = _next_action_for(c, value)
            if action:
                actions.append(action)

    total = len(crits)
    if passed_count == total:
        decision = "GO_PUBLIC_LAUNCH"
        summary = (
            f"✅ جاهز للإطلاق العام — كل المعايير الـ{total} متحققة. "
            "ابدأ خطة Public Launch من MASTER_STRATEGIC_PLAN §3 Phase 3."
        )
    elif any(b["key"] == "unsafe_sends" for b in blockers):
        decision = "BLOCKED"
        summary = (
            "🛑 Hard block — إرسال غير آمن مكتشف. "
            "أوقف كل live actions الآن. شغّل incident_router SEV1."
        )
    else:
        decision = "NO_GO"
        summary = (
            f"⏳ NO_GO — {passed_count}/{total} متحقق. "
            f"المتبقي: {', '.join(b['name_ar'] for b in blockers)}."
        )

    return GateVerdict(
        decision=decision,
        score_passed=passed_count,
        score_total=total,
        blockers=blockers,
        next_actions_ar=actions,
        criteria_results=results,
        summary_ar=summary,
    )
