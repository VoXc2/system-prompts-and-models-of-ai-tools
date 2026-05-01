"""
Campaign Risk Engine — pre-launch PDPL risk assessment for outreach campaigns.

Inputs: target list size, consent coverage, sensitive data presence,
template body, channel, time window. Output: risk score + per-issue list +
recommended fixes BEFORE the campaign goes live.

This is what makes the dashboard say:
  "Blocked: 18 contacts removed بسبب opt-out سابق. 7 يحتاجون lawful basis review.
   231 safe to contact."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Risky phrases — detected in any draft → escalate
RISKY_PHRASES_AR: tuple[str, ...] = (
    "ضمان 100",
    "نتائج مضمونة",
    "خصم محدود",
    "آخر فرصة",
    "اضغط هنا فوراً",
    "credit card",
    "رقم الهوية",
    "iban",
)

# PII keywords that should not appear in outbound bodies
PII_PHRASES: tuple[str, ...] = ("رقم الهوية", "رقم البطاقة", "passport", "national id", "iban")


@dataclass
class CampaignRiskAssessment:
    """Per-campaign risk report."""

    risk_score: int                # 0..100, higher = more risky
    risk_band: str                 # safe / caution / high / blocked
    issues: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    contacts_safe: int = 0
    contacts_blocked: int = 0
    contacts_needing_review: int = 0
    recommended_fixes_ar: list[str] = field(default_factory=list)


def _bucket(score: int) -> str:
    if score >= 80:
        return "blocked"
    if score >= 50:
        return "high"
    if score >= 25:
        return "caution"
    return "safe"


def score_campaign_risk(
    *,
    target_count: int,
    contacts_with_consent: int,
    contacts_opted_out: int,
    contacts_no_lawful_basis: int,
    template_body: str,
    template_subject: str = "",
    channel: str = "email",
    has_unsubscribe_link: bool = True,
    in_quiet_hours: bool = False,
) -> CampaignRiskAssessment:
    """Score the campaign before sending — block or allow."""
    issues: list[str] = []
    blockers: list[str] = []
    fixes: list[str] = []
    score = 0

    # Coverage
    contacts_blocked = contacts_opted_out
    contacts_needing_review = contacts_no_lawful_basis
    contacts_safe = max(0, target_count - contacts_blocked - contacts_needing_review)

    if contacts_opted_out > 0:
        # Opt-outs are auto-removed but we report them
        issues.append(f"{contacts_opted_out} contacts سبق لهم opt-out — سيُحذفون من الإرسال.")
        score += 5
    if contacts_no_lawful_basis > 0:
        score += 15
        issues.append(f"{contacts_no_lawful_basis} contacts بدون lawful basis واضح.")
        fixes.append(
            "راجع المصدر + سجّل lawful_basis في consent ledger قبل الإرسال."
        )

    # Template scanning
    body_lower = (template_body or "").lower()
    subject_lower = (template_subject or "").lower()
    combined = f"{subject_lower} {body_lower}"

    risky = [p for p in RISKY_PHRASES_AR if p.lower() in combined]
    if risky:
        score += 20 * len(risky)
        for p in risky:
            issues.append(f"عبارة محظورة في القالب: '{p}'")
        fixes.append("احذف العبارات الترويجية المبالغ فيها — استبدلها بقيمة محددة.")

    pii = [p for p in PII_PHRASES if p.lower() in combined]
    if pii:
        score += 30
        blockers.append(f"PII في القالب: {pii} — لا تطلب بيانات حساسة في الـ outbound.")

    # Unsubscribe link required for email
    if channel == "email" and not has_unsubscribe_link:
        score += 25
        blockers.append("الإيميل بدون List-Unsubscribe header (RFC 8058) — مخالف للمعايير.")
        fixes.append("أضف List-Unsubscribe header — Dealix يضيفه تلقائياً.")

    # Quiet hours
    if in_quiet_hours:
        score += 10
        issues.append("الإرسال داخل ساعات الهدوء (8م-9ص) — مزعج للمتلقي.")
        fixes.append("أجّل الإرسال إلى صباح اليوم التالي.")

    # Coverage too low
    if target_count > 0:
        coverage = contacts_safe / target_count
        if coverage < 0.5:
            score += 25
            issues.append(
                f"نسبة الـ contacts الآمنة منخفضة ({coverage*100:.0f}%) — راجع جودة الـ list."
            )

    score = min(100, score)
    band = _bucket(score)
    if blockers:
        band = "blocked"

    if not issues and not blockers:
        fixes.append("لا توصيات — الحملة آمنة للإرسال.")

    return CampaignRiskAssessment(
        risk_score=score,
        risk_band=band,
        issues=issues,
        blockers=blockers,
        contacts_safe=contacts_safe,
        contacts_blocked=contacts_blocked,
        contacts_needing_review=contacts_needing_review,
        recommended_fixes_ar=fixes,
    )
