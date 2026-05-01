"""
Meeting Operator — agenda + calendar draft + post-meeting follow-up.

Pure drafting only. No live Google Calendar event creation here —
the actual `events.insert` happens elsewhere (and only after explicit
user authorization via OAuth).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


def build_meeting_agenda(
    *,
    contact_name: str,
    company: str,
    purpose_ar: str = "اكتشاف وتأهيل أولي",
    duration_minutes: int = 20,
) -> dict[str, Any]:
    """Generate a deterministic Saudi-friendly agenda."""
    if duration_minutes <= 15:
        slots_ar = [
            "تعارف سريع (٢ دقائق)",
            "فهم وضع الشركة الحالي (٥ دقائق)",
            "عرض موجز لـ Dealix (٥ دقائق)",
            "تحديد الخطوة التالية (٣ دقائق)",
        ]
    elif duration_minutes <= 30:
        slots_ar = [
            "تعارف وأهداف الاجتماع (٣ دقائق)",
            f"الوضع الحالي لدى {company} (٧ دقائق)",
            "كيف يدعم Dealix هدفكم (١٠ دقائق)",
            "أسئلة مفتوحة (٥ دقائق)",
            "الخطوات التالية + توقيت المتابعة (٥ دقائق)",
        ]
    else:
        slots_ar = [
            "تعارف وأهداف الاجتماع (٥ دقائق)",
            f"التشخيص العميق لـ {company} (١٥ دقيقة)",
            "عرض demo حي مع سيناريو فعلي (١٥ دقيقة)",
            "ROI breakdown (٥ دقائق)",
            "أسئلة + تحديات تنفيذية (١٠ دقائق)",
            "الخطة المقترحة + الموافقات المطلوبة (١٠ دقائق)",
        ]
    return {
        "title_ar": f"اجتماع Dealix × {company}",
        "purpose_ar": purpose_ar,
        "duration_minutes": duration_minutes,
        "agenda_ar": slots_ar,
        "attendees_suggested_ar": [contact_name, "مؤسس / مدير مبيعات Dealix"],
        "approval_required": True,
        "approval_status": "pending_approval",
    }


def build_calendar_draft(
    *,
    contact_email: str | None,
    contact_name: str,
    company: str,
    proposed_start_iso: str | None = None,
    duration_minutes: int = 20,
) -> dict[str, Any]:
    """
    Build a Google-Calendar-shaped draft (NOT inserted live).

    Suggests the next business hour slot if no start is provided.
    Real `events.insert` happens only after the operator approves AND
    has authorized Calendar OAuth.
    """
    if proposed_start_iso:
        try:
            start_dt = datetime.fromisoformat(proposed_start_iso.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            start_dt = _next_business_hour()
    else:
        start_dt = _next_business_hour()
    end_dt = start_dt + timedelta(minutes=duration_minutes)

    summary_ar = f"اجتماع Dealix × {company}"
    description_ar = (
        f"اجتماع مع {contact_name} من {company} لاستكشاف فرصة استخدام "
        f"Dealix لتشغيل النمو. مدة الاجتماع: {duration_minutes} دقيقة."
    )
    return {
        "summary": summary_ar,
        "description": description_ar,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "Asia/Riyadh",
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "Asia/Riyadh",
        },
        "attendees": [
            {"email": contact_email} for contact_email in [contact_email] if contact_email
        ],
        "conference_data_request": {
            "createRequest": {
                "requestId": f"dealix-meet-{int(start_dt.timestamp())}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
        "live_inserted": False,
        "approval_required": True,
        "approval_status": "pending_approval",
        "compliance_note_ar": (
            "draft فقط — لا يُنشأ event حي في Google Calendar حتى موافقة "
            "OAuth صريحة + ضغطة المستخدم 'أنشئ الاجتماع'."
        ),
    }


def build_post_meeting_followup(
    *,
    contact_name: str,
    company: str,
    summary_ar: str,
    next_step_ar: str = "أرسل recap + pilot offer",
) -> dict[str, Any]:
    """Generate the post-meeting follow-up draft."""
    body_ar = (
        f"شكراً أستاذ {contact_name} على وقتكم الصباحي.\n\n"
        f"خلاصة الاجتماع:\n{summary_ar}\n\n"
        f"الخطوة التالية: {next_step_ar}\n\n"
        f"نسعد بمتابعة الموضوع متى ناسبكم."
    )
    return {
        "channel_recommendation": "email",
        "subject_ar": f"شكراً {contact_name} — متابعة اجتماع {company}",
        "body_ar": body_ar,
        "approval_required": True,
        "approval_status": "pending_approval",
    }


# ── Internal helpers ────────────────────────────────────────────
def _next_business_hour(*, now: datetime | None = None) -> datetime:
    """Next 09:00-17:00 Riyadh slot (demo helper; not timezone-perfect)."""
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    # Push to next day 10am UTC ~ 1pm Riyadh — safe demo slot
    candidate = (n + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    # Skip Friday (Saudi weekend = Fri-Sat)
    while candidate.weekday() in (4, 5):
        candidate += timedelta(days=1)
    return candidate
