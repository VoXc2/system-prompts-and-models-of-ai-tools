"""Google Calendar API-shaped draft payloads — no OAuth, no HTTP."""

from __future__ import annotations

from typing import Any


def build_calendar_draft_payload(params: dict[str, Any]) -> dict[str, Any]:
    """
    Minimal ``events.insert``-like resource for review only.
    """
    summary = str(params.get("summary_ar") or params.get("summary") or "اجتماع متابعة — Dealix")
    start = str(params.get("start_iso") or "2026-05-02T10:00:00+03:00")
    end = str(params.get("end_iso") or "2026-05-02T10:30:00+03:00")
    return {
        "approval_required": True,
        "event": {
            "summary": summary,
            "start": {"dateTime": start, "timeZone": "Asia/Riyadh"},
            "end": {"dateTime": end, "timeZone": "Asia/Riyadh"},
            "attendees": params.get("attendees") if isinstance(params.get("attendees"), list) else [],
        },
        "note_ar": "مسودة حدث فقط — لا يُنشأ في تقويم Google في MVP.",
    }
