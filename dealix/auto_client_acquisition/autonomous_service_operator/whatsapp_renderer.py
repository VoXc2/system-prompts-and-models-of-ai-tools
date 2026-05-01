"""WhatsApp renderer — convert cards/briefs to WhatsApp-ready format.

Drafts only. Never sends. Always emits buttons_ar capped at 3 (WhatsApp Reply
Buttons limit) and Arabic body text.
"""

from __future__ import annotations

from typing import Any


def render_card_for_whatsapp(card: dict[str, Any]) -> dict[str, Any]:
    """Render any decision card as a WhatsApp-style draft message."""
    title = str(card.get("title_ar", "")).strip()[:60]
    summary = str(card.get("summary_ar", "")).strip()[:300]
    why_now = str(card.get("why_now_ar", "")).strip()[:200]
    action = str(card.get("recommended_action_ar", "")).strip()[:200]
    risk = str(card.get("risk_level", "")).strip()
    buttons = list(card.get("buttons_ar", []))[:3]

    body_lines: list[str] = [title]
    if summary:
        body_lines.append("")
        body_lines.append(summary)
    if why_now:
        body_lines.append("")
        body_lines.append(f"لماذا الآن: {why_now}")
    if action:
        body_lines.append(f"الإجراء المقترح: {action}")
    if risk:
        body_lines.append(f"المخاطرة: {risk}")
    if buttons:
        body_lines.append("")
        body_lines.append("أزرار: " + " | ".join(buttons))

    return {
        "channel": "whatsapp",
        "kind": "card_draft",
        "body_ar": "\n".join(body_lines),
        "buttons_ar": buttons,
        "approval_required": True,
        "live_send_allowed": False,
    }


def render_approval_card_for_whatsapp(
    card: dict[str, Any],
) -> dict[str, Any]:
    """Render an approval card specifically — guarantees the 3 standard buttons."""
    out = render_card_for_whatsapp(card)
    out["buttons_ar"] = card.get("buttons_ar") or ["اعتمد", "عدّل", "تخطي"]
    out["kind"] = "approval_card"
    return out


def render_daily_brief_for_whatsapp(brief: dict[str, Any]) -> dict[str, Any]:
    """Render a CEO/Growth Manager daily brief as WhatsApp draft."""
    summary_lines = list(brief.get("summary_ar", []))[:8]
    decisions = list(brief.get("priority_decisions_ar", []))[:3]

    body_lines = ["صباح الخير 👋", "", "أهم اليوم:"]
    body_lines.extend(f"• {line}" for line in summary_lines)
    if decisions:
        body_lines.append("")
        body_lines.append("3 قرارات تنتظر:")
        body_lines.extend(f"{i + 1}. {d}" for i, d in enumerate(decisions))

    return {
        "channel": "whatsapp",
        "kind": "daily_brief_draft",
        "body_ar": "\n".join(body_lines),
        "buttons_ar": ["اعرض القرارات", "Proof Pack", "لاحقاً"],
        "approval_required": True,
        "live_send_allowed": False,
    }
