"""
Tool Verification Ledger.

Every tool invocation is logged with:
- intended_action (what the agent said it would do)
- actual_action (what actually happened)
- outputs + side effects
- verification_status

This is the difference between an agent 'claiming to have done something'
and an enterprise system 'proving what happened'.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class ToolInvocation:
    invocation_id: str
    tool_name: str
    agent_name: str
    decision_id: str | None
    intended_action: str
    actual_action: str
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    side_effects: list[str] = field(default_factory=list)
    verification_status: str = "pending"  # pending | verified | contradicted | blocked
    contradiction_flag: bool = False
    at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "invocation_id": self.invocation_id,
            "tool_name": self.tool_name,
            "agent_name": self.agent_name,
            "decision_id": self.decision_id,
            "intended_action": self.intended_action,
            "actual_action": self.actual_action,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "side_effects": self.side_effects,
            "verification_status": self.verification_status,
            "contradiction_flag": self.contradiction_flag,
            "at": self.at.isoformat(),
        }


class ToolVerificationLedger:
    """Append-only ledger of tool invocations."""

    def __init__(self) -> None:
        self._entries: list[ToolInvocation] = []

    def record(
        self,
        *,
        tool_name: str,
        agent_name: str,
        intended_action: str,
        actual_action: str,
        decision_id: str | None = None,
        inputs: dict[str, Any] | None = None,
        outputs: dict[str, Any] | None = None,
        side_effects: list[str] | None = None,
    ) -> ToolInvocation:
        contradiction = intended_action != actual_action
        entry = ToolInvocation(
            invocation_id=f"tool_{uuid.uuid4().hex[:16]}",
            tool_name=tool_name,
            agent_name=agent_name,
            decision_id=decision_id,
            intended_action=intended_action,
            actual_action=actual_action,
            inputs=inputs or {},
            outputs=outputs or {},
            side_effects=side_effects or [],
            verification_status="contradicted" if contradiction else "verified",
            contradiction_flag=contradiction,
        )
        self._entries.append(entry)
        return entry

    def contradictions(self) -> list[ToolInvocation]:
        return [e for e in self._entries if e.contradiction_flag]

    def for_decision(self, decision_id: str) -> list[ToolInvocation]:
        return [e for e in self._entries if e.decision_id == decision_id]

    def __len__(self) -> int:
        return len(self._entries)
