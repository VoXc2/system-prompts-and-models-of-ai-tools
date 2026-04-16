"""Detect mismatches between stated intentions, claims, and executed tool calls."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.sovereign.schemas import ContradictionRecord


class ContradictionDashboard(BaseModel):
    items: list[ContradictionRecord]
    total_open: int
    total_resolved: int
    total_escalated: int


class ContradictionStats(BaseModel):
    total: int
    by_agent: dict[str, int]
    by_status: dict[str, int]
    contradiction_rate: float


@dataclass
class _IntentionState:
    tenant_id: str
    agent_id: str
    intended_action: str
    claimed_action: str | None = None
    actual_tool_call: str | None = None
    side_effects: list[str] = field(default_factory=list)
    record_id: UUID = field(default_factory=uuid4)
    resolution_status: str = "open"
    resolution_notes: str | None = None


class ContradictionEngine:
    def __init__(self) -> None:
        self._intentions: dict[UUID, _IntentionState] = {}
        self._tenant_intentions: dict[str, list[UUID]] = {}
        self._records: dict[UUID, ContradictionRecord] = {}

    def record_intention(self, tenant_id: str, agent_id: str, intended_action: str) -> UUID:
        intention_id = uuid4()
        self._intentions[intention_id] = _IntentionState(
            tenant_id=tenant_id,
            agent_id=agent_id,
            intended_action=intended_action,
        )
        self._tenant_intentions.setdefault(tenant_id, []).append(intention_id)
        return intention_id

    def record_claim(self, tenant_id: str, intention_id: UUID, claimed_action: str) -> None:
        state = self._require_intention(tenant_id, intention_id)
        state.claimed_action = claimed_action

    def record_actual(
        self,
        tenant_id: str,
        intention_id: UUID,
        actual_tool_call: str,
        side_effects: list[str],
    ) -> None:
        state = self._require_intention(tenant_id, intention_id)
        state.actual_tool_call = actual_tool_call
        state.side_effects = side_effects

    def _require_intention(self, tenant_id: str, intention_id: UUID) -> _IntentionState:
        state = self._intentions.get(intention_id)
        if state is None or state.tenant_id != tenant_id:
            msg = "Unknown intention for tenant"
            raise KeyError(msg)
        return state

    def detect(self, tenant_id: str, intention_id: UUID) -> ContradictionRecord:
        state = self._require_intention(tenant_id, intention_id)
        claimed = state.claimed_action or ""
        actual = state.actual_tool_call or ""
        contradiction = bool(claimed and actual and claimed.strip() != actual.strip())
        record = ContradictionRecord(
            record_id=state.record_id,
            agent_id=state.agent_id,
            intended_action=state.intended_action,
            claimed_action=claimed,
            actual_tool_call=actual,
            side_effects=state.side_effects,
            contradiction_detected=contradiction,
            resolution_status=state.resolution_status,  # type: ignore[arg-type]
            resolution_notes=state.resolution_notes,
        )
        self._records[record.record_id] = record
        return record

    def get_dashboard(self, tenant_id: str, limit: int, offset: int) -> ContradictionDashboard:
        ids = self._tenant_intentions.get(tenant_id, [])
        slice_ids = ids[offset : offset + limit]
        items: list[ContradictionRecord] = []
        for iid in slice_ids:
            items.append(self.detect(tenant_id, iid))
        all_records = [self.detect(tenant_id, i) for i in ids]
        open_c = sum(1 for r in all_records if r.resolution_status == "open")
        resolved = sum(1 for r in all_records if r.resolution_status == "resolved")
        escalated = sum(1 for r in all_records if r.resolution_status == "escalated")
        return ContradictionDashboard(
            items=items,
            total_open=open_c,
            total_resolved=resolved,
            total_escalated=escalated,
        )

    def resolve(self, tenant_id: str, record_id: UUID, resolution_notes: str) -> None:
        rec = self._records.get(record_id)
        if rec is None:
            msg = "Unknown contradiction record"
            raise KeyError(msg)
        st = self._find_state_by_record(tenant_id, record_id)
        st.resolution_status = "resolved"
        st.resolution_notes = resolution_notes
        self._records[record_id] = rec.model_copy(
            update={"resolution_status": "resolved", "resolution_notes": resolution_notes},
        )

    def escalate(self, tenant_id: str, record_id: UUID, reason: str) -> None:
        rec = self._records.get(record_id)
        if rec is None:
            msg = "Unknown contradiction record"
            raise KeyError(msg)
        st = self._find_state_by_record(tenant_id, record_id)
        st.resolution_status = "escalated"
        st.resolution_notes = reason
        self._records[record_id] = rec.model_copy(
            update={"resolution_status": "escalated", "resolution_notes": reason},
        )

    def _find_state_by_record(self, tenant_id: str, record_id: UUID) -> _IntentionState:
        for st in self._intentions.values():
            if st.record_id == record_id and st.tenant_id == tenant_id:
                return st
        msg = "Record not found for tenant"
        raise KeyError(msg)

    def get_stats(self, tenant_id: str) -> ContradictionStats:
        ids = self._tenant_intentions.get(tenant_id, [])
        by_agent: dict[str, int] = {}
        by_status: dict[str, int] = {}
        contradictions = 0
        for iid in ids:
            rec = self.detect(tenant_id, iid)
            by_agent[rec.agent_id] = by_agent.get(rec.agent_id, 0) + 1
            by_status[rec.resolution_status] = by_status.get(rec.resolution_status, 0) + 1
            if rec.contradiction_detected:
                contradictions += 1
        total = len(ids)
        rate = contradictions / total if total else 0.0
        return ContradictionStats(
            total=total,
            by_agent=by_agent,
            by_status=by_status,
            contradiction_rate=rate,
        )
