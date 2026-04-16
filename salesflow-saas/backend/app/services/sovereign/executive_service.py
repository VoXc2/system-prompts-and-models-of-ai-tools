"""Sovereign Executive Room — Aggregation service for the CEO dashboard."""

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.sovereign.decision_service import DecisionService
from app.services.sovereign.execution_service import ExecutionService
from app.services.sovereign.trust_service import TrustService
from app.services.sovereign.partnership_service import PartnershipService
from app.services.sovereign.ma_service import MAService
from app.services.sovereign.expansion_service import ExpansionService
from app.services.sovereign.pmi_service import PMIService
from app.services.sovereign.connector_service import ConnectorService
from app.services.sovereign.evidence_service import EvidenceService


class ExecutiveService:
    """Aggregates data from all sovereign planes into executive dashboards."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._decision = DecisionService(db)
        self._execution = ExecutionService(db)
        self._trust = TrustService(db)
        self._partnership = PartnershipService(db)
        self._ma = MAService(db)
        self._expansion = ExpansionService(db)
        self._pmi = PMIService(db)
        self._connector = ConnectorService(db)
        self._evidence = EvidenceService(db)

    async def get_executive_dashboard(self, tenant_id: str) -> dict:
        decision_data = await self._decision.get_decision_dashboard(tenant_id)
        partnership_data = await self._partnership.get_partnership_scorecards(tenant_id)
        ma_data = await self._ma.get_ma_pipeline(tenant_id)
        expansion_data = await self._expansion.get_expansion_console(tenant_id)
        pmi_data = await self._pmi.get_pmi_engine(tenant_id)
        connector_data = await self._connector.get_connector_health_board(tenant_id)
        evidence_data = await self._evidence.get_evidence_summary(tenant_id)
        compliance_data = await self._trust.get_compliance_matrix(tenant_id)

        return {
            "decision_plane": decision_data,
            "partnerships": partnership_data,
            "ma_pipeline": ma_data,
            "expansion": expansion_data,
            "pmi_engine": pmi_data,
            "connectors": connector_data,
            "evidence": evidence_data,
            "compliance": compliance_data,
        }

    async def get_approval_center(self, tenant_id: str) -> dict:
        pending_recommendations = await self._decision.list_recommendations(
            tenant_id, filters={"status": "draft"},
        )

        pending_evidence = await self._evidence.list_evidence_packs(
            tenant_id, status="pending_approval",
        )

        pending_workflows = await self._execution.list_workflows(
            tenant_id, status_filter="pending",
        )

        return {
            "pending_recommendations": [
                {
                    "id": str(r.id),
                    "title": r.title,
                    "title_ar": r.title_ar,
                    "type": r.recommendation_type,
                    "confidence_score": float(r.confidence_score) if r.confidence_score else 0.0,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in pending_recommendations
            ],
            "pending_evidence_packs": [
                {
                    "id": str(e.id),
                    "title": e.title,
                    "title_ar": e.title_ar,
                    "pack_type": e.pack_type,
                    "sensitivity": e.sensitivity,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in pending_evidence
            ],
            "pending_workflows": [
                {
                    "id": str(w.id),
                    "title": w.title,
                    "title_ar": w.title_ar,
                    "workflow_type": w.workflow_type,
                    "total_steps": w.total_steps,
                    "created_at": w.created_at.isoformat() if w.created_at else None,
                }
                for w in pending_workflows
            ],
            "total_pending": (
                len(pending_recommendations)
                + len(pending_evidence)
                + len(pending_workflows)
            ),
        }

    async def get_risk_board(self, tenant_id: str) -> dict:
        ma_data = await self._ma.get_ma_pipeline(tenant_id)
        expansion_data = await self._expansion.get_expansion_console(tenant_id)
        pmi_data = await self._pmi.get_pmi_engine(tenant_id)
        compliance_data = await self._trust.get_compliance_matrix(tenant_id)

        ma_risks = []
        for stage, info in ma_data.get("pipeline", {}).items():
            if info["count"] > 0 and stage in ("due_diligence", "negotiation"):
                ma_risks.append({
                    "category": "ma",
                    "level": "high",
                    "description": f"{info['count']} target(s) in {stage} stage",
                    "valuation_range": {
                        "low": info["valuation_low"],
                        "high": info["valuation_high"],
                    },
                })

        expansion_risks = []
        paused = expansion_data.get("by_status", {}).get("paused", 0)
        if paused > 0:
            expansion_risks.append({
                "category": "expansion",
                "level": "medium",
                "description": f"{paused} market(s) currently paused",
            })

        pmi_risks = []
        for phase, info in pmi_data.get("task_matrix", {}).items():
            if info["overdue"] > 0:
                pmi_risks.append({
                    "category": "pmi",
                    "level": "high" if info["overdue"] > 3 else "medium",
                    "description": f"{info['overdue']} overdue task(s) in phase {phase}",
                    "phase": phase,
                })

        compliance_risks = []
        for fw, info in compliance_data.get("frameworks", {}).items():
            high_risk = info.get("by_risk", {}).get("high", 0)
            critical_risk = info.get("by_risk", {}).get("critical", 0)
            if high_risk > 0 or critical_risk > 0:
                compliance_risks.append({
                    "category": "compliance",
                    "level": "critical" if critical_risk > 0 else "high",
                    "description": f"{fw}: {high_risk} high, {critical_risk} critical risk control(s)",
                    "framework": fw,
                })

        all_risks = ma_risks + expansion_risks + pmi_risks + compliance_risks
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_risks.sort(key=lambda r: severity_order.get(r["level"], 99))

        return {
            "risks": all_risks,
            "total_risks": len(all_risks),
            "by_category": {
                "ma": len(ma_risks),
                "expansion": len(expansion_risks),
                "pmi": len(pmi_risks),
                "compliance": len(compliance_risks),
            },
            "violations_total": compliance_data.get("total_violations", 0),
        }
