"""
Account Timeline helpers — narrative renderers for UI + email digests.

`render_timeline_markdown()` produces a human-readable Arabic timeline
suitable for the customer's QBR or daily brief. The narrative is
deterministic from the event stream → reproducible audit trail.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from auto_client_acquisition.revenue_memory.projections import AccountTimeline


def render_timeline_markdown(timeline: AccountTimeline) -> str:
    """Render an account timeline as a brief Arabic Markdown summary."""
    lines: list[str] = []
    lines.append(f"# Timeline — Account {timeline.account_id}")
    if timeline.first_seen:
        lines.append(f"**أول تفاعل:** {timeline.first_seen.date()}")
    if timeline.last_activity:
        lines.append(f"**آخر نشاط:** {timeline.last_activity.date()}")
    lines.append("")
    lines.append(
        f"**ملخص:** {timeline.n_messages_sent} رسالة · "
        f"{timeline.n_replies} رد · {timeline.n_meetings} اجتماع · "
        f"{timeline.n_signals} إشارة شراء"
    )
    lines.append("")
    lines.append("## التسلسل الزمني")
    if not timeline.entries:
        lines.append("_لا أحداث مسجلة بعد._")
    else:
        for entry in timeline.entries[-30:]:  # last 30 events
            stamp = entry.occurred_at.strftime("%Y-%m-%d %H:%M")
            lines.append(f"- `{stamp}` — {entry.headline}")
    return "\n".join(lines)


def timeline_to_dashboard_dict(timeline: AccountTimeline) -> dict[str, Any]:
    """Compact dict for the Dashboard widget."""
    return {
        "account_id": timeline.account_id,
        "metrics": {
            "messages": timeline.n_messages_sent,
            "replies": timeline.n_replies,
            "meetings": timeline.n_meetings,
            "signals": timeline.n_signals,
        },
        "last_activity": timeline.last_activity.isoformat() if timeline.last_activity else None,
        "recent": [
            {
                "at": e.occurred_at.isoformat(),
                "type": e.event_type,
                "headline": e.headline,
            }
            for e in timeline.entries[-10:]
        ],
    }
