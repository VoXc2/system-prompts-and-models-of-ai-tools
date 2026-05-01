"""Post-meeting follow-up draft (Arabic)."""

from __future__ import annotations

from typing import Any


def build_post_meeting_followup(summary_ar: str, next_steps: list[str] | None = None) -> dict[str, Any]:
    steps = next_steps or ["إرسال ملخص موافق عليه", "تحديد موعد متابعة", "مشاركة مسودة عرض مختصرة"]
    body = (
        f"شكراً لوقتكم. الملخص: {summary_ar[:200]}…\n"
        f"الخطوات المقترحة: {'؛ '.join(steps)}.\n"
        "ننتظر تأكيدكم للمتابعة."
    )
    return {"subject_ar": "متابعة — ملخص الاجتماع والخطوة التالية", "body_ar": body, "approval_required": True, "demo": True}
