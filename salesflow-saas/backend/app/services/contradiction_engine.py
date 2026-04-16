"""
Contradiction Engine — Dealix Sovereign Trust Plane

Captures and surfaces contradictions between:
  - Intended agent action
  - Claimed agent action
  - Actual tool call
  - Side effects

Every agent tool call should call record_tool_call().
The engine detects deviations and creates ContradictionRecord entries.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.sovereign import (
    ToolVerificationLedger,
    ContradictionRecord,
)


class ContradictionEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_tool_call(
        self,
        tenant_id: str,
        agent_role: str,
        tool_name: str,
        intended_action: str,
        claimed_action: str,
        actual_tool_call: dict[str, Any],
        side_effects: list[Any] | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
        latency_ms: int | None = None,
        outcome: str = "success",
    ) -> tuple[ToolVerificationLedger, ContradictionRecord | None]:
        """
        Record a tool execution. Automatically detect contradictions.
        Returns (ledger_entry, contradiction_record_or_None).
        """
        contradiction_status = self._detect_contradiction(
            intended_action=intended_action,
            claimed_action=claimed_action,
            actual_tool_call=actual_tool_call,
            side_effects=side_effects or [],
        )

        ledger = ToolVerificationLedger(
            tenant_id=tenant_id,
            agent_role=agent_role,
            tool_name=tool_name,
            intended_action=intended_action,
            claimed_action=claimed_action,
            actual_tool_call=actual_tool_call,
            side_effects=side_effects or [],
            contradiction_status=contradiction_status,
            correlation_id=correlation_id,
            trace_id=trace_id,
            span_id=span_id,
            outcome=outcome,
            latency_ms=latency_ms,
        )
        self.db.add(ledger)
        await self.db.flush()

        contradiction = None
        if contradiction_status in ("suspected", "confirmed"):
            contradiction = ContradictionRecord(
                tenant_id=tenant_id,
                agent_role=agent_role,
                tool_ledger_id=ledger.id,
                intended_action_summary=intended_action[:1000],
                actual_action_summary=self._summarize_actual(actual_tool_call),
                contradiction_type=self._classify_contradiction(
                    intended_action, claimed_action, actual_tool_call, side_effects or []
                ),
                severity=self._assess_severity(tool_name, contradiction_status),
                status="open",
                correlation_id=correlation_id,
            )
            self.db.add(contradiction)

        await self.db.commit()
        return ledger, contradiction

    def _detect_contradiction(
        self,
        intended_action: str,
        claimed_action: str,
        actual_tool_call: dict,
        side_effects: list,
    ) -> str:
        """
        Heuristic contradiction detection.
        Returns: none | suspected | confirmed
        """
        if not intended_action or not claimed_action:
            return "none"

        # Simple keyword mismatch heuristic (production: use embedding similarity)
        intended_lower = intended_action.lower()
        claimed_lower = claimed_action.lower()
        actual_tool = actual_tool_call.get("tool", "").lower()

        if actual_tool and actual_tool not in claimed_lower and actual_tool not in intended_lower:
            return "confirmed"

        # Check for unexpected side effects
        if side_effects:
            return "suspected"

        # Check for significant length mismatch suggesting schema violation
        if len(claimed_lower) > 0 and abs(len(intended_lower) - len(claimed_lower)) > 200:
            return "suspected"

        return "none"

    def _classify_contradiction(
        self,
        intended: str,
        claimed: str,
        actual: dict,
        side_effects: list,
    ) -> str:
        if actual.get("tool") and actual["tool"].lower() not in claimed.lower():
            return "claim_mismatch"
        if side_effects:
            return "side_effect_unexpected"
        return "claim_mismatch"

    def _assess_severity(self, tool_name: str, status: str) -> str:
        high_risk_tools = {
            "send_message", "sign_contract", "submit_offer", "transfer_funds",
            "delete_record", "activate_partner", "publish_board_pack",
        }
        if any(t in tool_name.lower() for t in high_risk_tools):
            return "high" if status == "confirmed" else "medium"
        return "medium" if status == "confirmed" else "low"

    def _summarize_actual(self, actual_tool_call: dict) -> str:
        return str(actual_tool_call)[:1000]

    async def get_dashboard(self, tenant_id: str) -> dict[str, Any]:
        """Return contradiction dashboard summary."""
        total_result = await self.db.execute(
            select(func.count(ContradictionRecord.id)).where(
                ContradictionRecord.tenant_id == tenant_id,
            )
        )
        total = total_result.scalar() or 0

        open_result = await self.db.execute(
            select(func.count(ContradictionRecord.id)).where(
                ContradictionRecord.tenant_id == tenant_id,
                ContradictionRecord.status == "open",
            )
        )
        open_count = open_result.scalar() or 0

        critical_result = await self.db.execute(
            select(func.count(ContradictionRecord.id)).where(
                ContradictionRecord.tenant_id == tenant_id,
                ContradictionRecord.severity == "high",
                ContradictionRecord.status == "open",
            )
        )
        critical_count = critical_result.scalar() or 0

        recent = await self.db.execute(
            select(ContradictionRecord).where(
                ContradictionRecord.tenant_id == tenant_id,
            ).order_by(ContradictionRecord.created_at.desc()).limit(10)
        )
        recent_rows = recent.scalars().all()

        return {
            "total_contradictions": total,
            "open_contradictions": open_count,
            "critical_open": critical_count,
            "recent": [
                {
                    "id": str(r.id),
                    "agent_role": r.agent_role,
                    "contradiction_type": r.contradiction_type,
                    "severity": r.severity,
                    "status": r.status,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in recent_rows
            ],
        }

    async def resolve(
        self,
        tenant_id: str,
        contradiction_id: str,
        resolution_notes: str,
        false_positive: bool = False,
    ) -> dict[str, Any]:
        result = await self.db.execute(
            select(ContradictionRecord).where(
                ContradictionRecord.id == contradiction_id,
                ContradictionRecord.tenant_id == tenant_id,
            )
        )
        rec = result.scalar_one_or_none()
        if not rec:
            raise ValueError("Contradiction not found")
        rec.status = "false_positive" if false_positive else "resolved"
        rec.resolution_notes = resolution_notes
        await self.db.commit()
        return {"id": contradiction_id, "status": rec.status}
