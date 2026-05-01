"""Merge innovation demo command feed with event-derived cards."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.innovation.command_feed import build_demo_command_feed
from auto_client_acquisition.revenue_company_os.event_to_card import event_to_card


def build_company_os_command_feed(extra_events: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    base = build_demo_command_feed()
    cards = list(base.get("cards") or [])
    for ev in extra_events or []:
        et = str(ev.get("type") or "form.submitted")
        cards.append(event_to_card(et, ev.get("payload")))
    return {"cards": cards, "source": "company_os_merged", "demo": True}
