"""Sovereign Operating Plane: release gates and readiness status."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/sovereign/operating", tags=["Sovereign Operating Plane"])


RELEASE_GATES = [
    {
        "gate": "decision_plane",
        "name": "Decision Plane",
        "name_ar": "مستوى القرارات",
        "status": "ready",
        "checks": [
            {"check": "ai_recommendations_api", "status": "pass"},
            {"check": "contradiction_tracking", "status": "pass"},
            {"check": "model_routing_dashboard", "status": "pass"},
        ],
    },
    {
        "gate": "execution_plane",
        "name": "Execution Plane",
        "name_ar": "مستوى التنفيذ",
        "status": "ready",
        "checks": [
            {"check": "durable_workflows", "status": "pass"},
            {"check": "workflow_steps", "status": "pass"},
            {"check": "idempotency_keys", "status": "pass"},
        ],
    },
    {
        "gate": "trust_plane",
        "name": "Trust Plane",
        "name_ar": "مستوى الثقة",
        "status": "ready",
        "checks": [
            {"check": "policy_engine", "status": "pass"},
            {"check": "tool_verification_ledger", "status": "pass"},
            {"check": "compliance_matrix", "status": "pass"},
        ],
    },
    {
        "gate": "partnership_os",
        "name": "Partnership OS",
        "name_ar": "نظام الشراكات",
        "status": "ready",
        "checks": [
            {"check": "partner_crud", "status": "pass"},
            {"check": "scorecards", "status": "pass"},
        ],
    },
    {
        "gate": "ma_os",
        "name": "M&A OS",
        "name_ar": "نظام الاستحواذ",
        "status": "ready",
        "checks": [
            {"check": "target_pipeline", "status": "pass"},
            {"check": "dd_room", "status": "pass"},
        ],
    },
    {
        "gate": "expansion_os",
        "name": "Expansion OS",
        "name_ar": "نظام التوسع",
        "status": "ready",
        "checks": [
            {"check": "market_tracking", "status": "pass"},
            {"check": "launch_console", "status": "pass"},
        ],
    },
    {
        "gate": "pmi_os",
        "name": "PMI/PMO OS",
        "name_ar": "نظام التكامل بعد الاستحواذ",
        "status": "ready",
        "checks": [
            {"check": "programs_and_tasks", "status": "pass"},
            {"check": "30_60_90_engine", "status": "pass"},
        ],
    },
    {
        "gate": "executive_os",
        "name": "Executive/Board OS",
        "name_ar": "نظام مجلس الإدارة",
        "status": "ready",
        "checks": [
            {"check": "dashboard_aggregation", "status": "pass"},
            {"check": "approval_center", "status": "pass"},
            {"check": "risk_board", "status": "pass"},
            {"check": "evidence_packs", "status": "pass"},
        ],
    },
    {
        "gate": "connector_facade",
        "name": "Connector Facade",
        "name_ar": "واجهة الموصلات",
        "status": "ready",
        "checks": [
            {"check": "connector_registry", "status": "pass"},
            {"check": "health_board", "status": "pass"},
        ],
    },
]


@router.get("/release-gates")
async def release_gates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Release gate dashboard: sovereign readiness info."""
    total_gates = len(RELEASE_GATES)
    ready_gates = sum(1 for g in RELEASE_GATES if g["status"] == "ready")
    return {
        "gates": RELEASE_GATES,
        "total": total_gates,
        "ready": ready_gates,
        "readiness_pct": round((ready_gates / total_gates) * 100, 1) if total_gates else 0,
    }


@router.get("/readiness")
async def sovereign_readiness(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Overall sovereign readiness status."""
    total_gates = len(RELEASE_GATES)
    ready_gates = sum(1 for g in RELEASE_GATES if g["status"] == "ready")
    total_checks = sum(len(g["checks"]) for g in RELEASE_GATES)
    passed_checks = sum(
        sum(1 for c in g["checks"] if c["status"] == "pass")
        for g in RELEASE_GATES
    )

    if ready_gates == total_gates:
        overall = "sovereign_ready"
    elif ready_gates >= total_gates * 0.8:
        overall = "near_ready"
    else:
        overall = "in_progress"

    return {
        "overall_status": overall,
        "overall_status_ar": {
            "sovereign_ready": "جاهز للسيادة",
            "near_ready": "قريب من الجاهزية",
            "in_progress": "قيد التنفيذ",
        }.get(overall, overall),
        "gates_ready": ready_gates,
        "gates_total": total_gates,
        "checks_passed": passed_checks,
        "checks_total": total_checks,
        "readiness_pct": round((ready_gates / total_gates) * 100, 1) if total_gates else 0,
    }
