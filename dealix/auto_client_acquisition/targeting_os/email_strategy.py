"""Email strategy — drafts only, unsubscribe always, pacing-aware."""

from __future__ import annotations

from typing import Any


def draft_b2b_email(
    contact: dict[str, Any],
    *,
    offer: str = "",
    why_now: str = "",
    tone: str = "professional_saudi",
) -> dict[str, Any]:
    """Build a B2B email draft (Arabic). Never sends."""
    name = contact.get("name", "")
    company = contact.get("company", "")
    role = contact.get("role", "")

    salutation = f"هلا {name}" if name else "هلا"
    company_part = f" من {company}" if company else ""
    why_now_part = f"\n{why_now}\n" if why_now else "\n"

    body_ar = (
        f"{salutation}،\n\n"
        f"أكتب لك{company_part} باختصار. "
        f"نشتغل على Dealix كمدير نمو عربي للشركات السعودية:"
        f"{why_now_part}"
        "خلال 7 أيام، نطلع لك:\n"
        "• 10 فرص B2B مناسبة لقطاعكم\n"
        "• رسائل عربية جاهزة بنبرتنا\n"
        "• خطة متابعة قابلة للتنفيذ\n"
        "• Proof Pack بعد الأسبوع\n\n"
        f"{offer or 'Pilot بـ 499 ريال أو مجاني مقابل case study.'}\n\n"
        "إذا الفكرة تناسبك، نحدد مكالمة 15 دقيقة هذا الأسبوع.\n"
        "وإن ما كانت الأولوية الآن خبرني وأرتاح.\n\nشاكر لك."
    )

    return {
        "subject_ar": (
            f"فرصة نمو لـ{company}" if company else "فرصة نمو B2B خلال 7 أيام"
        ),
        "body_ar": include_unsubscribe_footer(body_ar),
        "tone": tone,
        "target_role": role,
        "approval_required": True,
        "live_send_allowed": False,
    }


def include_unsubscribe_footer(body: str) -> str:
    """Append a one-line unsubscribe footer (Arabic + English)."""
    if not body:
        return body
    footer = (
        "\n\n———\n"
        "لإيقاف هذه الرسائل، رد بكلمة \"إلغاء\" / Reply STOP to unsubscribe."
    )
    return body + footer


def recommend_pacing(domain_reputation: str = "fresh") -> dict[str, Any]:
    """Recommend a daily send pacing based on domain reputation."""
    rep = (domain_reputation or "fresh").lower()
    table = {
        "fresh":     {"max_daily": 20, "warmup_days": 21, "ramp_step": 5},
        "warmed":    {"max_daily": 60, "warmup_days": 0, "ramp_step": 10},
        "trusted":   {"max_daily": 200, "warmup_days": 0, "ramp_step": 25},
        "damaged":   {"max_daily": 5, "warmup_days": 30, "ramp_step": 1},
    }
    plan = table.get(rep, table["fresh"])
    return {
        "domain_reputation": rep,
        **plan,
        "notes_ar": (
            "ابدأ بحدود يومية صغيرة على domain جديد، وارتفع تدريجياً. "
            "domain متضرر يحتاج فترة تبريد + warmup قبل العودة."
        ),
    }


def score_email_risk(
    contact: dict[str, Any], message: str = "",
) -> dict[str, Any]:
    """
    Score an outbound email's risk 0..100 (higher = riskier).

    Looks at source, opt_in, message content for spam triggers.
    """
    source = contact.get("source", "unknown_source")
    opt_in = (contact.get("opt_in_status") or "unknown").lower()

    risk = 0
    reasons: list[str] = []

    if source == "cold_list":
        risk += 50; reasons.append("قائمة باردة — مخاطرة spam مرتفعة.")
    elif source == "unknown_source":
        risk += 30; reasons.append("مصدر غير معروف — يحتاج مراجعة.")
    elif source in ("inbound_lead", "crm_customer", "website_form"):
        risk -= 10  # safer

    if opt_in not in ("yes", "double"):
        risk += 10

    msg = (message or "").lower()
    spam_triggers = ["ضمان 100%", "ضمان مضمون", "act now", "urgent",
                     "free money", "click here now", "limited offer"]
    for t in spam_triggers:
        if t in msg.lower() or t in (message or ""):
            risk += 15
            reasons.append(f"عبارة spam: {t}")

    risk = max(0, min(100, risk))
    if risk >= 60:
        verdict = "blocked"
    elif risk >= 30:
        verdict = "needs_review"
    else:
        verdict = "safe"

    return {"risk": risk, "verdict": verdict, "reasons_ar": reasons}


def build_followup_sequence(
    contact: dict[str, Any], *, offer: str = "",
) -> dict[str, Any]:
    """Build a 3-step Arabic email follow-up sequence."""
    name = contact.get("name", "")
    sal = f"هلا {name}" if name else "هلا"
    return {
        "approval_required": True,
        "live_send_allowed": False,
        "steps": [
            {
                "day": 0,
                "subject_ar": "فرصة نمو B2B خلال 7 أيام",
                "body_ar": include_unsubscribe_footer(
                    f"{sal}، (الرسالة الأولى مع العرض الكامل)"
                ),
            },
            {
                "day": 3,
                "subject_ar": "متابعة سريعة",
                "body_ar": include_unsubscribe_footer(
                    f"{sal}، أتابع رسالتي السابقة. "
                    "هل أرتب لك ديمو 12 دقيقة هذا الأسبوع؟"
                ),
            },
            {
                "day": 7,
                "subject_ar": "آخر متابعة",
                "body_ar": include_unsubscribe_footer(
                    f"{sal}، آخر متابعة من جهتي. "
                    "إذا ما كانت الأولوية الآن أرتاح وأرشّفها. "
                    "وإن أردت ديمو لاحقاً، أنا موجود."
                ),
            },
        ],
    }
