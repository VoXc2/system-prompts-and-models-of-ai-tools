"""Append-only conversation turns per session (in-memory MVP)."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.autonomous_service_operator import session_state as ss


def append_turn(session_id: str, role: str, content: str, meta: dict[str, Any] | None = None) -> None:
    s = ss.touch_session(session_id)
    log = list(s.get("turns") or [])
    log.append({"role": role, "content": content[:4000], **(meta or {})})
    ss.upsert_session(session_id, {"turns": log[-50:]})


def list_turns(session_id: str) -> list[dict[str, Any]]:
    s = ss.get_session(session_id) or {}
    return list(s.get("turns") or [])
