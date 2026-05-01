"""
Contactability — per-contact "can we contact?" decision with PDPL reasons.

Default policy: **no cold WhatsApp** without lawful basis.
PDPL Art.5 emphasizes lawful basis, consent, and purpose limitation.
"""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.growth_operator.contact_importer import (
    classify_contact_source,
    detect_opt_out,
    normalize_phone,
)

# ── Decision labels ──────────────────────────────────────────────
CONTACTABILITY_LABELS: tuple[str, ...] = (
    "safe",            # consent + lawful basis verified
    "needs_review",    # source unclear; pending operator confirmation
    "blocked",         # opt-out / banned / invalid / breaches policy
)


def score_contactability(
    contact: dict[str, Any],
    *,
    channel: str = "whatsapp",
    require_consent_for_cold_whatsapp: bool = True,
) -> dict[str, Any]:
    """
    Decide whether this contact can be approached on this channel today.

    Returns:
      {
        "label": "safe"|"needs_review"|"blocked",
        "channel": "...",
        "reasons": [...],          # human-readable Arabic reasons
        "next_action": "...",      # what the operator should do
      }
    """
    reasons: list[str] = []
    label: str = "safe"

    # 1) Opt-out / banned wins everything
    if detect_opt_out(contact):
        return {
            "label": "blocked",
            "channel": channel,
            "reasons": ["العميل سجل opt-out أو محظور — لا تواصل بأي شكل."],
            "next_action": "remove_from_lists",
        }

    # 2) Phone validity
    phone = normalize_phone(contact.get("phone"))
    if channel == "whatsapp" and not phone:
        return {
            "label": "blocked",
            "channel": channel,
            "reasons": ["لا يوجد رقم صالح — WhatsApp مستحيل."],
            "next_action": "remove_or_collect_phone",
        }

    # 3) Source classification
    src = classify_contact_source(contact)

    # Cold WhatsApp without consent → blocked
    if channel == "whatsapp" and require_consent_for_cold_whatsapp:
        if src == "cold_list":
            return {
                "label": "blocked",
                "channel": channel,
                "reasons": [
                    "WhatsApp البارد ممنوع بدون lawful basis (PDPL م.5).",
                    "السياسة: لا cold WhatsApp افتراضياً.",
                ],
                "next_action": "switch_to_email_or_get_consent",
            }
        if src == "unknown":
            return {
                "label": "needs_review",
                "channel": channel,
                "reasons": [
                    "مصدر الرقم غير محدد — يحتاج توثيق lawful basis.",
                    "ارجع للمشغّل لإقرار العلاقة قبل الإرسال.",
                ],
                "next_action": "operator_confirms_source",
            }

    # 4) Healthy paths
    if src in ("existing_customer", "inbound_lead", "referral"):
        return {
            "label": "safe",
            "channel": channel,
            "reasons": [
                f"علاقة قائمة ({src}) — أساس قانوني قائم لـ business contact.",
            ],
            "next_action": "draft_message_with_approval",
        }
    if src == "old_lead":
        last = contact.get("last_contacted_at")
        if last:
            reasons.append("lead سابق — تواصل ضمن نافذة شهور قابلة للتبرير.")
            label = "safe"
        else:
            reasons.append("lead سابق بدون تاريخ تواصل — يحتاج warm-up قصير.")
            label = "needs_review"
        return {
            "label": label,
            "channel": channel,
            "reasons": reasons,
            "next_action": (
                "draft_short_followup_with_approval" if label == "safe"
                else "operator_confirms_continuity"
            ),
        }
    if src == "event_lead":
        return {
            "label": "safe",
            "channel": channel,
            "reasons": ["lead من فعالية مع موافقة ضمنية على المتابعة بـ 30 يوم."],
            "next_action": "draft_event_followup_with_approval",
        }

    # 5) Email channel — more permissive (List-Unsubscribe header makes it safer)
    if channel == "email":
        if src == "unknown":
            return {
                "label": "needs_review",
                "channel": "email",
                "reasons": ["مصدر غير محدد — أرسل عبر إيميل مع List-Unsubscribe إن قبلت."],
                "next_action": "operator_confirms_source",
            }
        return {
            "label": "safe",
            "channel": "email",
            "reasons": [f"مصدر مقبول للإيميل B2B ({src})."],
            "next_action": "draft_email_with_approval",
        }

    # Fallback (defensive)
    return {
        "label": "needs_review",
        "channel": channel,
        "reasons": ["لا تطابق سياسة معروفة — يحتاج مراجعة المشغّل."],
        "next_action": "operator_review_required",
    }


def contactability_summary(
    contacts: list[dict[str, Any]],
    *,
    channel: str = "whatsapp",
) -> dict[str, Any]:
    """Bulk classification report for the upload dashboard."""
    counts: dict[str, int] = {label: 0 for label in CONTACTABILITY_LABELS}
    next_actions: dict[str, int] = {}
    sample_blocked: list[dict[str, Any]] = []
    sample_review: list[dict[str, Any]] = []
    sample_safe: list[dict[str, Any]] = []

    for c in contacts:
        decision = score_contactability(c, channel=channel)
        counts[decision["label"]] += 1
        next_actions[decision["next_action"]] = next_actions.get(decision["next_action"], 0) + 1
        if decision["label"] == "blocked" and len(sample_blocked) < 5:
            sample_blocked.append({**c, **decision})
        elif decision["label"] == "needs_review" and len(sample_review) < 5:
            sample_review.append({**c, **decision})
        elif decision["label"] == "safe" and len(sample_safe) < 5:
            sample_safe.append({**c, **decision})

    return {
        "channel": channel,
        "total": len(contacts),
        "by_label": counts,
        "by_next_action": next_actions,
        "sample_safe": sample_safe,
        "sample_review": sample_review,
        "sample_blocked": sample_blocked,
        "policy_note": (
            "لا cold WhatsApp بدون lawful basis — السياسة الافتراضية. "
            "العميل يقدر يعدل القاعدة لكل قائمة بعد توثيق المصدر."
        ),
    }
