"""Outreach sequence — re-uses launch_ops with revenue-tier extensions."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.launch_ops.outreach_messages import (
    build_first_20_segments as _base_segments,
    build_followup_message as _base_followup,
    build_outreach_message as _base_msg,
    build_reply_handlers as _base_handlers,
)


def build_first_20_segments_v2() -> dict[str, Any]:
    """Re-export (single source of truth in launch_ops)."""
    return _base_segments()


def build_outreach_message_v2(
    segment_id: str, *, name: str = "[الاسم]",
) -> dict[str, Any]:
    """Re-export from launch_ops."""
    return _base_msg(segment_id, name=name)


def build_followup_1(segment_id: str, *, name: str = "[الاسم]") -> dict[str, Any]:
    return _base_followup(segment_id, step=1, name=name)


def build_followup_2(segment_id: str, *, name: str = "[الاسم]") -> dict[str, Any]:
    return _base_followup(segment_id, step=2, name=name)


def build_reply_handlers_v2() -> dict[str, dict[str, str]]:
    return _base_handlers()
