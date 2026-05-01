"""Build a post-meeting follow-up draft (Arabic) — never sends."""

from __future__ import annotations

from typing import Any


def build_post_meeting_followup(
    *,
    summary: dict[str, Any] | None = None,
    next_steps: list[str] | None = None,
    contact_name: str = "",
    company_name: str = "",
    objections: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Build a draft follow-up email/WhatsApp message in Arabic.

    Always returns approval_required=True; never executes a send.
    """
    next_steps = next_steps or []
    objections = objections or []

    salutation = f"هلا {contact_name}" if contact_name else "هلا"
    company_part = f" من شركة {company_name}" if company_name else ""

    bullet_steps = "\n".join([f"• {s}" for s in next_steps]) or "• [حدد الخطوة التالية بتاريخ محدد]"

    objection_addressed = ""
    if objections:
        labels = sorted({str(o.get("label_ar", "")) for o in objections if o.get("label_ar")})
        if labels:
            objection_addressed = (
                "\nرجعت بعد الاجتماع وفكرت في النقاط التي ذكرتها: "
                + "، ".join(labels)
                + ". أرفقت لك إجابات قصيرة مع أمثلة."
            )

    body_ar = (
        f"{salutation}،\n"
        f"شكراً على وقتك اليوم{company_part}. "
        "ملخص ما اتفقنا عليه:\n"
        f"{bullet_steps}\n"
        f"{objection_addressed}\n"
        "\nإذا كل شي واضح من جهتك، أبدأ في تجهيز Pilot قصير ونشتغل خلال أسبوع. "
        "أي ملاحظة تحب تضيفها قبل ما نبدأ؟\n\nشاكر لك."
    )

    subject_ar = f"متابعة اجتماع اليوم — {company_name or 'Dealix'}"

    return {
        "channel_drafts": {
            "email": {
                "subject_ar": subject_ar,
                "body_ar": body_ar,
                "approval_required": True,
                "live_send_allowed": False,
            },
            "whatsapp": {
                "body_ar": (
                    f"{salutation}، شكراً على اجتماع اليوم. "
                    "الخطوة التالية: " + (next_steps[0] if next_steps else "نحدد موعد بداية الـPilot") +
                    ". أتابع معك خلال يومين."
                ),
                "approval_required": True,
                "live_send_allowed": False,
            },
        },
        "summary_used": bool(summary),
        "objections_addressed": [str(o.get("label_ar")) for o in objections if o.get("label_ar")],
        "approval_required": True,
    }
