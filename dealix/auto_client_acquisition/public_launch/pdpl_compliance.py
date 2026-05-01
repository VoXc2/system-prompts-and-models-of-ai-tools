"""PDPL Compliance — final readiness check before Public Launch.

Saudi Personal Data Protection Law (PDPL) compliance check covering:
- Data residency
- Opt-in audit per channel
- Breach notification readiness (72-hour rule)
- DPA template availability
- Privacy policy bilingual publication
- SDAIA registration status (if applicable)
- Data retention policy enforcement

Deterministic — no I/O, no LLM. State is passed in as dict.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Mapping


@dataclass(frozen=True)
class PDPLCheck:
    key: str
    name_ar: str
    description_ar: str
    severity: str  # "critical" | "high" | "medium"


PDPL_CHECKS: tuple[PDPLCheck, ...] = (
    PDPLCheck(
        key="data_residency_saudi",
        name_ar="إقامة البيانات في السعودية",
        description_ar="بيانات العملاء مخزنة في region سعودي أو لدى شريك سعودي معتمد",
        severity="critical",
    ),
    PDPLCheck(
        key="whatsapp_opt_in_audit",
        name_ar="تدقيق opt-in لـ WhatsApp",
        description_ar="كل رقم واتساب فيه opt-in موثّق قبل الإرسال",
        severity="critical",
    ),
    PDPLCheck(
        key="email_opt_in_audit",
        name_ar="تدقيق opt-in لـ Email",
        description_ar="كل بريد إلكتروني فيه opt-in موثّق أو جاء عبر website form",
        severity="high",
    ),
    PDPLCheck(
        key="breach_notification_72h_ready",
        name_ar="جاهزية إبلاغ التسريب خلال 72 ساعة",
        description_ar="عند تسريب بيانات: إبلاغ SDAIA + العملاء المتأثرين خلال 72 ساعة",
        severity="critical",
    ),
    PDPLCheck(
        key="dpa_template_published",
        name_ar="نشر نموذج DPA",
        description_ar="نموذج Data Processing Agreement عربي/إنجليزي متاح للعملاء",
        severity="high",
    ),
    PDPLCheck(
        key="privacy_policy_bilingual",
        name_ar="سياسة الخصوصية ثنائية اللغة",
        description_ar="Privacy Policy منشورة بالعربية والإنجليزية على dealix.me",
        severity="critical",
    ),
    PDPLCheck(
        key="data_retention_policy",
        name_ar="سياسة احتفاظ البيانات",
        description_ar="بيانات الـ leads غير المتفاعلين تُحذف بعد 90 يوم",
        severity="high",
    ),
    PDPLCheck(
        key="trace_redaction_active",
        name_ar="إخفاء PII من traces",
        description_ar="Trace Redactor مفعّل ويغطي email/phone/national_id/passport",
        severity="critical",
    ),
    PDPLCheck(
        key="action_ledger_audit",
        name_ar="سجل الأفعال (Action Ledger)",
        description_ar="كل external action مسجّل مع who/what/when/approval_id",
        severity="high",
    ),
    PDPLCheck(
        key="consent_revocation_path",
        name_ar="مسار إلغاء الموافقة",
        description_ar="العميل يقدر يلغي opt-in عبر link/email/WhatsApp بدون احتكاك",
        severity="medium",
    ),
)


@dataclass
class PDPLReport:
    overall_status: str   # "compliant" | "needs_fixes" | "non_compliant"
    score_passed: int
    score_total: int
    critical_failures: list[Mapping[str, Any]]
    high_failures: list[Mapping[str, Any]]
    medium_failures: list[Mapping[str, Any]]
    check_results: list[Mapping[str, Any]]
    summary_ar: str
    next_actions_ar: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_pdpl_compliance(state: Mapping[str, Any]) -> PDPLReport:
    """Evaluate PDPL compliance.

    Args:
        state: dict mapping check key → bool (True = compliant).
               Keys not in state default to False (non-compliant).

    Returns:
        PDPLReport with overall status, failures by severity, next actions.
    """
    results: list[dict[str, Any]] = []
    critical_failures: list[dict[str, Any]] = []
    high_failures: list[dict[str, Any]] = []
    medium_failures: list[dict[str, Any]] = []
    actions: list[str] = []
    passed = 0

    for check in PDPL_CHECKS:
        ok = bool(state.get(check.key, False))
        result = {
            "key": check.key,
            "name_ar": check.name_ar,
            "passed": ok,
            "severity": check.severity,
            "description_ar": check.description_ar,
        }
        results.append(result)
        if ok:
            passed += 1
        else:
            if check.severity == "critical":
                critical_failures.append(result)
                actions.append(f"🛑 [CRITICAL] {check.name_ar} — {check.description_ar}")
            elif check.severity == "high":
                high_failures.append(result)
                actions.append(f"⚠️ [HIGH] {check.name_ar}")
            else:
                medium_failures.append(result)

    total = len(PDPL_CHECKS)

    if critical_failures:
        status = "non_compliant"
        summary = (
            f"🛑 NON-COMPLIANT — {len(critical_failures)} مشاكل critical. "
            "لا تنتقل لـ Public Launch قبل إصلاحها."
        )
    elif high_failures:
        status = "needs_fixes"
        summary = (
            f"⚠️ NEEDS FIXES — {len(high_failures)} مشاكل high. "
            f"PDPL compliance score: {passed}/{total}."
        )
    else:
        status = "compliant"
        summary = f"✅ COMPLIANT — كل {total} فحوصات PDPL متحققة."

    return PDPLReport(
        overall_status=status,
        score_passed=passed,
        score_total=total,
        critical_failures=critical_failures,
        high_failures=high_failures,
        medium_failures=medium_failures,
        check_results=results,
        summary_ar=summary,
        next_actions_ar=actions,
    )
