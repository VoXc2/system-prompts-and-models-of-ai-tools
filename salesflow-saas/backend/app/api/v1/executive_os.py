"""Executive / Board OS — Executive surfaces API."""
from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.sovereign import sovereign_os

router = APIRouter(prefix="/executive-os", tags=["Executive OS"])


@router.get("/room")
async def executive_room(tenant_id: str = Query(default="default")):
    return sovereign_os.get_executive_dashboard(tenant_id)


@router.get("/approval-center")
async def approval_center(tenant_id: str = Query(default="default")):
    pending_workflows = sovereign_os.list_pending_approvals(tenant_id)
    pending_decisions = [d.model_dump() for d in sovereign_os.decision_engine.list_pending()]
    return {
        "workflow_approvals": pending_workflows,
        "decision_approvals": pending_decisions,
        "total_pending": len(pending_workflows) + len(pending_decisions),
    }


@router.get("/evidence-packs")
async def evidence_pack_viewer():
    return {"packs": [], "total": 0}


@router.get("/risk-heatmap")
async def risk_heatmap(tenant_id: str = Query(default="default")):
    return sovereign_os.get_risk_heatmap(tenant_id)


@router.get("/actual-vs-forecast")
async def actual_vs_forecast(tenant_id: str = Query(default="default")):
    return {
        "tenant_id": tenant_id,
        "periods": [],
        "revenue_actual": 0,
        "revenue_forecast": 0,
        "variance_pct": 0,
    }


@router.get("/policy-violations")
async def policy_violations(tenant_id: str = Query(default="default")):
    return sovereign_os.get_policy_violations(tenant_id)


@router.get("/next-best-action")
async def next_best_action(tenant_id: str = Query(default="default")):
    pending = sovereign_os.list_pending_approvals(tenant_id)
    actions = []
    for p in pending[:5]:
        actions.append({
            "type": "approve_step",
            "priority": "high",
            "description": f"Approve: {p.get('step_name', '')}",
            "description_ar": f"اعتماد: {p.get('step_name', '')}",
            "instance_id": p.get("instance_id"),
            "step_id": p.get("step_id"),
        })
    return {"actions": actions, "total": len(actions)}


@router.get("/board-memo")
async def board_memo_view(tenant_id: str = Query(default="default")):
    dashboard = sovereign_os.get_executive_dashboard(tenant_id)
    return {
        "tenant_id": tenant_id,
        "memo_type": "board_ready",
        "sections": {
            "executive_summary": "",
            "executive_summary_ar": "",
            "financial_overview": {},
            "risk_assessment": sovereign_os.get_risk_heatmap(tenant_id),
            "compliance_status": {
                "pdpl": f"{dashboard.get('pdpl_controls_implemented', 0)}/{dashboard.get('pdpl_controls_total', 0)}",
                "nca": f"{dashboard.get('nca_controls_implemented', 0)}/{dashboard.get('nca_controls_total', 0)}",
            },
            "pending_decisions": dashboard.get("active_decisions", 0),
            "active_workflows": dashboard.get("active_workflows", 0),
        },
    }


@router.get("/connector-health")
async def connector_health():
    return {"connectors": [], "total": 0, "healthy": 0, "degraded": 0, "error": 0}


@router.get("/release-gates")
async def release_gate_dashboard():
    from app.planes.operating.release_governance import release_governance
    releases = release_governance.list_releases()
    return {"releases": [r.model_dump() for r in releases], "total": len(releases)}


@router.get("/saudi-compliance")
async def saudi_compliance_matrix(tenant_id: str = Query(default="default")):
    matrix = sovereign_os.check_compliance(tenant_id)
    return matrix.model_dump()


@router.get("/model-routing")
async def model_routing_dashboard():
    return sovereign_os.get_model_routing_dashboard()


@router.get("/tool-verification")
async def tool_verification_ledger():
    entries = sovereign_os.tool_ledger.list_all()
    return {"tools": [e.model_dump() for e in entries], "total": len(entries)}
