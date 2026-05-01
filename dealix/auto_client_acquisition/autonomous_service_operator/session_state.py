"""In-memory operator sessions — MVP; replace with DB or revenue_memory later."""

from __future__ import annotations

import uuid
from typing import Any

_SESSIONS: dict[str, dict[str, Any]] = {}


def new_session_id() -> str:
    return f"op_{uuid.uuid4().hex[:16]}"


def get_session(session_id: str) -> dict[str, Any] | None:
    return _SESSIONS.get(session_id)


def upsert_session(session_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    base = dict(_SESSIONS.get(session_id, {}))
    base.update(patch)
    base["session_id"] = session_id
    _SESSIONS[session_id] = base
    return base


def touch_session(session_id: str) -> dict[str, Any]:
    if session_id not in _SESSIONS:
        _SESSIONS[session_id] = {"session_id": session_id, "workflow_state": "idle"}
    return _SESSIONS[session_id]


def list_sessions_with_pending() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for sid, data in _SESSIONS.items():
        pc = data.get("pending_card")
        if isinstance(pc, dict):
            out.append({"session_id": sid, "card": pc})
    return out
