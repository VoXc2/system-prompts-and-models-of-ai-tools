"""Operator memory — minimal in-process store for sessions + facts."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .session_state import SessionState


@dataclass
class OperatorMemory:
    """In-process memory for the operator. Production = Supabase/Redis."""
    sessions: dict[str, SessionState] = field(default_factory=dict)
    customer_facts: dict[str, dict[str, Any]] = field(default_factory=dict)
    customer_preferences: dict[str, dict[str, Any]] = field(default_factory=dict)
    blocked_actions_log: list[dict[str, Any]] = field(default_factory=list)
    approved_actions_log: list[dict[str, Any]] = field(default_factory=list)
    pivots_log: list[dict[str, Any]] = field(default_factory=list)

    # ── sessions ────────────────────────────────────────────
    def upsert_session(self, session: SessionState) -> SessionState:
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> SessionState | None:
        return self.sessions.get(session_id)

    def list_sessions_for_customer(self, customer_id: str) -> list[SessionState]:
        return [s for s in self.sessions.values()
                if s.customer_id == customer_id]

    # ── customer facts ──────────────────────────────────────
    def remember_fact(self, customer_id: str, key: str, value: Any) -> None:
        bucket = self.customer_facts.setdefault(customer_id, {})
        bucket[key] = value

    def get_fact(self, customer_id: str, key: str) -> Any:
        return self.customer_facts.get(customer_id, {}).get(key)

    def all_facts(self, customer_id: str) -> dict[str, Any]:
        return dict(self.customer_facts.get(customer_id, {}))

    # ── preferences ─────────────────────────────────────────
    def update_preference(
        self, customer_id: str, *, key: str, value: Any,
    ) -> None:
        bucket = self.customer_preferences.setdefault(customer_id, {})
        bucket[key] = value

    def get_preferences(self, customer_id: str) -> dict[str, Any]:
        return dict(self.customer_preferences.get(customer_id, {}))

    # ── action audit ────────────────────────────────────────
    def log_blocked_action(
        self, *, action_type: str, reason_ar: str,
        customer_id: str | None = None,
    ) -> None:
        self.blocked_actions_log.append({
            "ts": time.time(),
            "action_type": action_type,
            "reason_ar": reason_ar[:200],
            "customer_id": customer_id,
        })

    def log_approved_action(
        self, *, action_type: str,
        customer_id: str | None = None,
        notes: str = "",
    ) -> None:
        self.approved_actions_log.append({
            "ts": time.time(),
            "action_type": action_type,
            "customer_id": customer_id,
            "notes": notes[:200],
        })

    def summarize_audit(self) -> dict[str, Any]:
        return {
            "blocked_count": len(self.blocked_actions_log),
            "approved_count": len(self.approved_actions_log),
            "blocked_recent": self.blocked_actions_log[-5:],
            "approved_recent": self.approved_actions_log[-5:],
        }


def build_session_context(
    *,
    memory: OperatorMemory,
    session_id: str,
) -> dict[str, Any]:
    """Build a context blob for a session — facts + recent audit + state."""
    session = memory.get_session(session_id)
    if session is None:
        return {"error": "unknown session"}

    customer_id = session.customer_id or ""
    return {
        "session": session.to_dict(),
        "customer_facts": memory.all_facts(customer_id),
        "preferences": memory.get_preferences(customer_id),
        "audit": memory.summarize_audit(),
    }
