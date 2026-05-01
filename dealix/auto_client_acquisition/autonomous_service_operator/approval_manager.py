"""Human-in-the-loop gates for operator workflow."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.autonomous_service_operator import session_state as ss


def set_pending_approval(session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return ss.upsert_session(
        session_id,
        {"workflow_state": "pending_approval", "pending_card": payload},
    )


def apply_decision(session_id: str, decision: str) -> dict[str, Any]:
    d = (decision or "").strip().lower()
    if d in ("approve", "اعتمد"):
        return ss.upsert_session(
            session_id,
            {"workflow_state": "approved", "pending_card": None, "last_decision": "approve"},
        )
    if d in ("edit", "تعديل"):
        return ss.upsert_session(
            session_id,
            {"workflow_state": "edit_requested", "last_decision": "edit"},
        )
    if d in ("skip", "تخطي"):
        return ss.upsert_session(
            session_id,
            {"workflow_state": "skipped", "pending_card": None, "last_decision": "skip"},
        )
    return ss.upsert_session(session_id, {"workflow_state": "unknown_decision", "last_decision": d})


def pending_card(session_id: str) -> dict[str, Any] | None:
    s = ss.get_session(session_id)
    if not s:
        return None
    return s.get("pending_card") if isinstance(s.get("pending_card"), dict) else None
