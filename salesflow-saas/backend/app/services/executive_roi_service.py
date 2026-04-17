"""Executive Room Service — aggregates real data from 7 sources for the executive dashboard."""

from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.deal import Deal
from app.models.operations import ApprovalRequest, IntegrationSyncState


class ExecutiveRoomService:
    """Aggregates live data from multiple services into one executive snapshot."""

    async def build_snapshot(self, db: AsyncSession, tenant_id: str) -> Dict[str, Any]:
        tid = UUID(tenant_id)
        return {
            "revenue": await self._revenue(db, tid),
            "approvals": await self._approvals(db, tid),
            "connectors": await self._connectors(db, tid),
            "compliance": await self._compliance(db, tenant_id),
            "contradictions": await self._contradictions(db, tenant_id),
            "strategic_deals": await self._strategic_deals(db, tid),
            "evidence_packs": await self._evidence_packs(db, tid),
        }

    # ── Revenue ──────────────────────────────────────────────

    async def _revenue(self, db: AsyncSession, tid: UUID) -> Dict[str, Any]:
        actual = float(
            (await db.execute(
                select(func.coalesce(func.sum(Deal.value), 0))
                .where(Deal.tenant_id == tid, Deal.stage == "closed_won")
            )).scalar() or 0
        )
        pipeline = float(
            (await db.execute(
                select(func.coalesce(func.sum(Deal.value), 0))
                .where(Deal.tenant_id == tid, Deal.stage.in_(["discovery", "proposal", "negotiation"]))
            )).scalar() or 0
        )
        total_closed = int(
            (await db.execute(
                select(func.count()).select_from(Deal)
                .where(Deal.tenant_id == tid, Deal.stage.in_(["closed_won", "closed_lost"]))
            )).scalar() or 0
        )
        won = int(
            (await db.execute(
                select(func.count()).select_from(Deal)
                .where(Deal.tenant_id == tid, Deal.stage == "closed_won")
            )).scalar() or 0
        )
        win_rate = round((won / total_closed * 100), 1) if total_closed else 0.0
        forecast = round(actual * 1.1, 2)
        variance = round(((actual - forecast) / forecast * 100), 1) if forecast else 0.0
        return {
            "actual": actual,
            "forecast": forecast,
            "variance_percent": variance,
            "pipeline_value": pipeline,
            "win_rate": win_rate,
        }

    # ── Approvals with SLA ───────────────────────────────────

    async def _approvals(self, db: AsyncSession, tid: UUID) -> Dict[str, Any]:
        rows = (await db.execute(
            select(ApprovalRequest.payload)
            .where(ApprovalRequest.tenant_id == tid, ApprovalRequest.status == "pending")
        )).scalars().all()
        pending = len(rows)
        warning = breach = 0
        for payload in rows:
            sla = (payload or {}).get("_dealix_sla", {}) if isinstance(payload, dict) else {}
            level = int(sla.get("escalation_level", 0)) if isinstance(sla, dict) else 0
            if level == 1:
                warning += 1
            elif level >= 2:
                breach += 1
        return {"pending": pending, "warning": warning, "breach": breach}

    # ── Connectors ───────────────────────────────────────────

    async def _connectors(self, db: AsyncSession, tid: UUID) -> Dict[str, Any]:
        rows = (await db.execute(
            select(IntegrationSyncState.status, func.count())
            .where(IntegrationSyncState.tenant_id == tid)
            .group_by(IntegrationSyncState.status)
        )).all()
        counts = {"ok": 0, "degraded": 0, "error": 0}
        for status, cnt in rows:
            if status in counts:
                counts[status] = cnt
        return {"healthy": counts["ok"], "degraded": counts["degraded"], "error": counts["error"]}

    # ── Compliance ───────────────────────────────────────────

    async def _compliance(self, db: AsyncSession, tenant_id: str) -> Dict[str, Any]:
        from app.services.saudi_compliance_matrix import saudi_compliance_matrix
        p = await saudi_compliance_matrix.get_posture(db, tenant_id=tenant_id)
        return {
            "compliant": p.get("compliant", 0),
            "partial": p.get("partial", 0),
            "non_compliant": p.get("non_compliant", 0),
            "posture": p.get("posture", "unknown"),
        }

    # ── Contradictions ───────────────────────────────────────

    async def _contradictions(self, db: AsyncSession, tenant_id: str) -> Dict[str, Any]:
        from app.services.contradiction_engine import contradiction_engine
        s = await contradiction_engine.get_stats(db, tenant_id=tenant_id)
        return {"active": s.get("active", 0), "critical": s.get("critical_active", 0)}

    # ── Strategic Deals ──────────────────────────────────────

    async def _strategic_deals(self, db: AsyncSession, tid: UUID) -> Dict[str, Any]:
        from app.models.strategic_deal import StrategicDeal
        active = int(
            (await db.execute(
                select(func.count()).select_from(StrategicDeal)
                .where(StrategicDeal.tenant_id == tid, StrategicDeal.status.notin_(["closed_won", "closed_lost"]))
            )).scalar() or 0
        )
        value = float(
            (await db.execute(
                select(func.coalesce(func.sum(StrategicDeal.estimated_value_sar), 0))
                .where(StrategicDeal.tenant_id == tid, StrategicDeal.status.notin_(["closed_won", "closed_lost"]))
            )).scalar() or 0
        )
        return {"active": active, "pipeline_value": value}

    # ── Evidence Packs ───────────────────────────────────────

    async def _evidence_packs(self, db: AsyncSession, tid: UUID) -> Dict[str, Any]:
        from app.models.evidence_pack import EvidencePack, EvidencePackStatus
        ready = int(
            (await db.execute(
                select(func.count()).select_from(EvidencePack)
                .where(EvidencePack.tenant_id == tid, EvidencePack.status == EvidencePackStatus.READY)
            )).scalar() or 0
        )
        pending = int(
            (await db.execute(
                select(func.count()).select_from(EvidencePack)
                .where(EvidencePack.tenant_id == tid, EvidencePack.status == EvidencePackStatus.ASSEMBLING)
            )).scalar() or 0
        )
        return {"ready": ready, "pending_review": pending}

    async def build_weekly_pack(self, db: AsyncSession, tenant_id: str) -> Dict[str, Any]:
        """Build ExecWeeklyPack contract — the CANONICAL executive surface data source."""
        from app.schemas.structured_outputs import ExecWeeklyPack, Provenance
        from datetime import datetime, timezone
        import uuid

        snapshot = await self.build_snapshot(db, tenant_id)
        rev = snapshot["revenue"]
        approvals = snapshot["approvals"]
        compliance = snapshot["compliance"]
        contradictions = snapshot["contradictions"]

        # Determine RAG status
        blockers = []
        if approvals["breach"] > 0:
            blockers.append(f"خرق SLA: {approvals['breach']} موافقة متجاوزة")
        if contradictions["critical"] > 0:
            blockers.append(f"تناقضات حرجة: {contradictions['critical']}")
        if compliance["non_compliant"] > 0:
            blockers.append(f"ضوابط غير ممتثلة: {compliance['non_compliant']}")

        rag = "red" if blockers else ("amber" if approvals["warning"] > 0 or compliance["partial"] > 0 else "green")

        pack = ExecWeeklyPack(
            week_of=datetime.now(timezone.utc).strftime("%Y-W%W"),
            overall_rag=rag,
            completed_this_week=[],
            planned_next_week=[],
            blockers=blockers,
            synergy_actual_sar=rev["actual"],
            synergy_target_sar=rev["forecast"],
            people_update="",
            risk_summary=[f"Approvals pending: {approvals['pending']}", f"Compliance posture: {compliance['posture']}"],
            provenance=Provenance(
                generated_by="executive_room_service.build_weekly_pack",
                model_provider="system",
                confidence=0.9,
                freshness_hours=0.0,
                trace_id=str(uuid.uuid4()),
            ),
        )
        return pack.model_dump(mode="json")


executive_room_service = ExecutiveRoomService()
