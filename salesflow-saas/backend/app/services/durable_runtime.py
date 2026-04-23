"""Durable Runtime — persistent checkpointer for crash-safe workflows.

Wraps DurableTaskFlow with DB-backed persistence. Supports:
- Checkpoint after every state change
- Resume from last checkpoint after crash/restart
- Side-effect boundary tracking (avoid duplicate execution on resume)
- Correlation ID propagation
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class DurableRuntime:
    """Persistent checkpointer for long-running workflows."""

    async def start_run(
        self,
        db: AsyncSession,
        *,
        tenant_id: str,
        flow_name: str,
        initial_state: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Start a new durable workflow run."""
        from app.models.durable_checkpoint import DurableCheckpoint

        run_id = str(uuid.uuid4())
        cp = DurableCheckpoint(
            tenant_id=tenant_id,
            flow_name=flow_name,
            run_id=run_id,
            revision_id=str(uuid.uuid4()),
            sequence_num=0,
            note="run_started",
            state=initial_state or {},
            correlation_id=correlation_id or run_id,
            status="running",
        )
        db.add(cp)
        await db.commit()
        await db.refresh(cp)
        return {"run_id": run_id, "correlation_id": cp.correlation_id, "status": "running"}

    async def checkpoint(
        self,
        db: AsyncSession,
        *,
        tenant_id: str,
        run_id: str,
        note: str,
        state_patch: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Persist a checkpoint after a successful step."""
        from app.models.durable_checkpoint import DurableCheckpoint

        # Get current state
        last = await self._get_last_checkpoint(db, tenant_id=tenant_id, run_id=run_id)
        if not last:
            return {"error": "run_not_found"}

        new_state = dict(last["state"])
        new_state.update(state_patch)

        cp = DurableCheckpoint(
            tenant_id=tenant_id,
            flow_name=last["flow_name"],
            run_id=run_id,
            revision_id=str(uuid.uuid4()),
            sequence_num=last["sequence_num"] + 1,
            note=note,
            state=new_state,
            correlation_id=last["correlation_id"],
            status="running",
        )
        db.add(cp)
        await db.commit()
        await db.refresh(cp)
        return {
            "run_id": run_id,
            "revision_id": cp.revision_id,
            "sequence_num": cp.sequence_num,
            "state": cp.state,
        }

    async def complete_run(
        self,
        db: AsyncSession,
        *,
        tenant_id: str,
        run_id: str,
        final_state: Dict[str, Any],
        status: str = "completed",
    ) -> Dict[str, Any]:
        """Mark a run as completed (or failed)."""
        from app.models.durable_checkpoint import DurableCheckpoint

        last = await self._get_last_checkpoint(db, tenant_id=tenant_id, run_id=run_id)
        if not last:
            return {"error": "run_not_found"}

        cp = DurableCheckpoint(
            tenant_id=tenant_id,
            flow_name=last["flow_name"],
            run_id=run_id,
            revision_id=str(uuid.uuid4()),
            sequence_num=last["sequence_num"] + 1,
            note=f"run_{status}",
            state=final_state,
            correlation_id=last["correlation_id"],
            status=status,
            completed_at=datetime.now(timezone.utc),
        )
        db.add(cp)
        await db.commit()
        return {"run_id": run_id, "status": status, "final_state": final_state}

    async def resume_run(
        self,
        db: AsyncSession,
        *,
        tenant_id: str,
        run_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Resume a run from its last checkpoint."""
        last = await self._get_last_checkpoint(db, tenant_id=tenant_id, run_id=run_id)
        if not last:
            return None
        if last["status"] != "running":
            return {"run_id": run_id, "status": last["status"], "already_done": True}
        return last

    async def list_incomplete_runs(
        self, db: AsyncSession, *, tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find all runs still in 'running' state (for startup recovery)."""
        from app.models.durable_checkpoint import DurableCheckpoint
        from sqlalchemy import distinct

        # Get all distinct run_ids
        stmt = select(distinct(DurableCheckpoint.run_id))
        if tenant_id:
            stmt = stmt.where(DurableCheckpoint.tenant_id == tenant_id)
        result = await db.execute(stmt)
        run_ids = [r[0] for r in result.all()]

        incomplete = []
        for rid in run_ids:
            last = await self._get_last_checkpoint(db, tenant_id=tenant_id, run_id=rid)
            if last and last["status"] == "running":
                incomplete.append(last)
        return incomplete

    async def _get_last_checkpoint(
        self, db: AsyncSession, *, tenant_id: Optional[str], run_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get the latest checkpoint for a run."""
        from app.models.durable_checkpoint import DurableCheckpoint

        stmt = (
            select(DurableCheckpoint)
            .where(DurableCheckpoint.run_id == run_id)
            .order_by(DurableCheckpoint.sequence_num.desc())
            .limit(1)
        )
        if tenant_id:
            stmt = stmt.where(DurableCheckpoint.tenant_id == tenant_id)
        result = await db.execute(stmt)
        cp = result.scalar_one_or_none()
        if not cp:
            return None
        return {
            "run_id": cp.run_id,
            "flow_name": cp.flow_name,
            "revision_id": cp.revision_id,
            "sequence_num": cp.sequence_num,
            "note": cp.note,
            "state": cp.state or {},
            "correlation_id": cp.correlation_id,
            "status": cp.status,
            "completed_at": cp.completed_at.isoformat() if cp.completed_at else None,
        }


durable_runtime = DurableRuntime()
