"""Session state — minimal in-memory state for an operator conversation."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

# Valid state transitions for the operator session.
_VALID_STATES: tuple[str, ...] = (
    "new",
    "intent_classified",
    "intake_collecting",
    "intake_complete",
    "service_recommended",
    "workflow_running",
    "approval_pending",
    "approval_received",
    "executing",
    "proof_pending",
    "proof_delivered",
    "upsell_offered",
    "closed",
)


@dataclass
class SessionState:
    """A single operator conversation session."""
    session_id: str
    customer_id: str | None = None
    state: str = "new"
    intent: str | None = None
    recommended_service_id: str | None = None
    bundle_id: str | None = None
    intake_payload: dict[str, Any] = field(default_factory=dict)
    actions_pending_approval: list[dict[str, Any]] = field(default_factory=list)
    actions_approved: list[dict[str, Any]] = field(default_factory=list)
    actions_blocked: list[dict[str, Any]] = field(default_factory=list)
    proof_pack: dict[str, Any] | None = None
    upsell_offer: dict[str, Any] | None = None
    history: list[dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "customer_id": self.customer_id,
            "state": self.state,
            "intent": self.intent,
            "recommended_service_id": self.recommended_service_id,
            "bundle_id": self.bundle_id,
            "intake_payload": dict(self.intake_payload),
            "actions_pending_approval": list(self.actions_pending_approval),
            "actions_approved": list(self.actions_approved),
            "actions_blocked": list(self.actions_blocked),
            "proof_pack": self.proof_pack,
            "upsell_offer": self.upsell_offer,
            "history_len": len(self.history),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


def build_new_session(customer_id: str | None = None) -> SessionState:
    """Build a fresh session with a generated UUID."""
    return SessionState(
        session_id=str(uuid.uuid4()),
        customer_id=customer_id,
    )


def transition_session(
    session: SessionState,
    *,
    new_state: str,
    note: str = "",
) -> SessionState:
    """Move the session to a new state with audit trail."""
    if new_state not in _VALID_STATES:
        raise ValueError(
            f"Unknown session state: {new_state}. "
            f"Valid: {', '.join(_VALID_STATES)}"
        )
    session.history.append({
        "from": session.state,
        "to": new_state,
        "note": note[:200],
        "ts": time.time(),
    })
    session.state = new_state
    session.updated_at = time.time()
    return session
