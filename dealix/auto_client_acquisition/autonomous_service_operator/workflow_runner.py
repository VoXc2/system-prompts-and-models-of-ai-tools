"""Simple workflow state machine: intake → draft → pending_approval → proof."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.autonomous_service_operator import session_state as ss


def advance(session_id: str, event: str) -> dict[str, Any]:
    """event: start_service | draft_ready | submit_for_approval | proof_ready"""
    s = ss.touch_session(session_id)
    state = str(s.get("workflow_state") or "idle")
    ev = (event or "").strip().lower()
    transitions: dict[tuple[str, str], str] = {
        ("idle", "start_service"): "intake",
        ("intake", "draft_ready"): "draft",
        ("draft", "submit_for_approval"): "pending_approval",
        ("pending_approval", "proof_ready"): "proof",
        ("proof", "start_service"): "intake",
    }
    key = (state, ev)
    new_state = transitions.get(key, state)
    return ss.upsert_session(session_id, {"workflow_state": new_state, "last_event": ev})
