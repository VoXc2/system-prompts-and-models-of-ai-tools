"""Full Auto Ops: لقطة تشغيل، تدقيق، أحداث، موافقات، صحة تكامل."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user, get_optional_user, require_role
from app.models.user import User
from app.models.operations import ApprovalRequest
from app.config import get_settings
from app.services.audit_service import list_recent_audits
from app.services.operations_hub import (
    count_events_since,
    count_pending_approvals,
    emit_domain_event,
    list_integration_connectors,
    upsert_connector_status,
)
from app.openclaw.canary_context import get_canary_dashboard_context
from app.openclaw.observability_bridge import observability_bridge
from app.openclaw.memory_bridge import memory_bridge
from app.openclaw.media_bridge import media_bridge
from app.services.sla_escalation_alerts import (
    maybe_dispatch_sla_breach_alerts,
    refresh_pending_escalations,
)
from app.services.governance_contracts import build_governance_bundle

router = APIRouter(prefix="/operations", tags=["Full Auto Operations"])
settings = get_settings()

_EXECUTIVE_SURFACES: List[Dict[str, str]] = [
    {"key": "executive_room", "label": "Executive Room"},
    {"key": "approval_center", "label": "Approval Center"},
    {"key": "evidence_pack_viewer", "label": "Evidence Pack Viewer"},
    {"key": "partner_room", "label": "Partner Room"},
    {"key": "dd_room", "label": "DD Room"},
    {"key": "risk_board", "label": "Risk Board"},
    {"key": "policy_violations_board", "label": "Policy Violations Board"},
    {"key": "actual_vs_forecast_dashboard", "label": "Actual vs Forecast Dashboard"},
    {"key": "revenue_funnel_control_center", "label": "Revenue Funnel Control Center"},
    {"key": "partnership_scorecards", "label": "Partnership Scorecards"},
    {"key": "ma_pipeline_board", "label": "M&A Pipeline Board"},
    {"key": "expansion_launch_console", "label": "Expansion Launch Console"},
    {"key": "pmi_306090_engine", "label": "PMI 30/60/90 Engine"},
    {"key": "tool_verification_ledger", "label": "Tool Verification Ledger"},
    {"key": "connector_health_board", "label": "Connector Health Board"},
    {"key": "release_gate_dashboard", "label": "Release Gate Dashboard"},
    {"key": "saudi_compliance_matrix", "label": "Saudi Compliance Matrix"},
    {"key": "model_routing_dashboard", "label": "Model Routing Dashboard"},
]


def _hours_between(now: datetime, then: Optional[datetime]) -> float:
    if not then:
        return 0.0
    return max(0.0, (now - then).total_seconds() / 3600.0)


async def _approval_sla_metrics(db: AsyncSession, tenant_id) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    warn_h = max(1, int(settings.OPENCLAW_APPROVAL_SLA_HOURS_WARN))
    breach_h = max(warn_h, int(settings.OPENCLAW_APPROVAL_SLA_HOURS_BREACH))

    q_pending = await db.execute(
        select(ApprovalRequest).where(
            ApprovalRequest.tenant_id == tenant_id,
            ApprovalRequest.status == "pending",
        )
    )
    pending_rows = q_pending.scalars().all()
    pending_warn = 0
    pending_breach = 0
    for row in pending_rows:
        h = _hours_between(now, row.created_at)
        if h >= warn_h:
            pending_warn += 1
        if h >= breach_h:
            pending_breach += 1

    q_resolved = await db.execute(
        select(ApprovalRequest).where(
            ApprovalRequest.tenant_id == tenant_id,
            ApprovalRequest.status.in_(["approved", "rejected"]),
            ApprovalRequest.reviewed_at.is_not(None),
        )
    )
    resolved_rows = q_resolved.scalars().all()
    resolution_hours = []
    for row in resolved_rows:
        if row.created_at and row.reviewed_at:
            resolution_hours.append(max(0.0, (row.reviewed_at - row.created_at).total_seconds() / 3600.0))
    avg_hours = (sum(resolution_hours) / len(resolution_hours)) if resolution_hours else 0.0
    sla_health = "ok"
    if pending_breach > 0:
        sla_health = "breach"
    elif pending_warn > 0:
        sla_health = "warn"
    return {
        "pending_total": len(pending_rows),
        "pending_warn_count": pending_warn,
        "pending_breach_count": pending_breach,
        "resolved_count": len(resolved_rows),
        "avg_resolution_hours": round(avg_hours, 2),
        "warn_threshold_hours": warn_h,
        "breach_threshold_hours": breach_h,
        "health": sla_health,
        "alerts_config": {
            "enabled": bool(settings.OPENCLAW_SLA_ALERTS_ENABLED),
            "webhook_configured": bool((settings.OPENCLAW_SLA_WEBHOOK_URL or "").strip()),
            "slack_configured": bool((settings.OPENCLAW_SLA_SLACK_WEBHOOK_URL or "").strip()),
            "cooldown_minutes": int(settings.OPENCLAW_SLA_ALERT_COOLDOWN_MINUTES),
        },
    }


def _demo_snapshot() -> Dict[str, Any]:
    return {
        "demo_mode": True,
        "pending_approvals": 0,
        "domain_events_24h": 0,
        "audit_events_24h": 0,
        "connectors": [
            {"connector_key": "crm_salesforce", "display_name_ar": "Salesforce CRM", "status": "unknown", "last_success_at": None, "last_attempt_at": None, "last_error": None},
            {"connector_key": "whatsapp_cloud", "display_name_ar": "واتساب Cloud API", "status": "unknown", "last_success_at": None, "last_attempt_at": None, "last_error": None},
            {"connector_key": "stripe_billing", "display_name_ar": "Stripe — الفوترة", "status": "unknown", "last_success_at": None, "last_attempt_at": None, "last_error": None},
            {"connector_key": "email_sync", "display_name_ar": "مزامنة البريد", "status": "unknown", "last_success_at": None, "last_attempt_at": None, "last_error": None},
        ],
        "openclaw": {
            "recent_runs": [],
            "promoted_memories": 0,
            "media_drafts_pending": 0,
            "canary": get_canary_dashboard_context("00000000-0000-0000-0000-000000000000"),
            "approval_sla": {
                "pending_total": 0,
                "pending_warn_count": 0,
                "pending_breach_count": 0,
                "resolved_count": 0,
                "avg_resolution_hours": 0.0,
                "warn_threshold_hours": int(settings.OPENCLAW_APPROVAL_SLA_HOURS_WARN),
                "breach_threshold_hours": int(settings.OPENCLAW_APPROVAL_SLA_HOURS_BREACH),
                "health": "ok",
                "escalation_by_level": {"0": 0, "1": 0, "2": 0, "3": 0},
                "escalation_events_last_refresh": 0,
                "alert_dispatch": {"skipped_reason": "demo_mode"},
                "alerts_config": {
                    "enabled": bool(settings.OPENCLAW_SLA_ALERTS_ENABLED),
                    "webhook_configured": bool((settings.OPENCLAW_SLA_WEBHOOK_URL or "").strip()),
                    "slack_configured": bool((settings.OPENCLAW_SLA_SLACK_WEBHOOK_URL or "").strip()),
                    "cooldown_minutes": int(settings.OPENCLAW_SLA_ALERT_COOLDOWN_MINUTES),
                },
            },
        },
        "note_ar": "وضع توضيحي — سجّل الدخول لرؤية بيانات المستأجر.",
    }


def _surface_statuses(*, has_approvals: bool, has_evidence: bool, has_policy_board: bool, has_connector_board: bool) -> List[Dict[str, str]]:
    live_keys = {
        "executive_room": "live",
        "approval_center": "live" if has_approvals else "partial",
        "risk_board": "live" if has_approvals else "partial",
        "policy_violations_board": "live" if has_policy_board else "partial",
        "connector_health_board": "live" if has_connector_board else "partial",
        "evidence_pack_viewer": "live" if has_evidence else "partial",
        "tool_verification_ledger": "partial",
        "release_gate_dashboard": "partial",
        "saudi_compliance_matrix": "partial",
        "model_routing_dashboard": "partial",
    }
    items: List[Dict[str, str]] = []
    for s in _EXECUTIVE_SURFACES:
        st = live_keys.get(s["key"], "planned")
        items.append({"key": s["key"], "label": s["label"], "status": st})
    return items


def _demo_control_center() -> Dict[str, Any]:
    surfaces = _surface_statuses(
        has_approvals=False,
        has_evidence=False,
        has_policy_board=True,
        has_connector_board=True,
    )
    ready = sum(1 for s in surfaces if s["status"] == "live")
    return {
        "demo_mode": True,
        "decision_plane": {
            "approval_class_mix": {"auto": 0, "manager": 0, "executive": 0, "board": 0},
            "human_gate_rate_percent": 0.0,
        },
        "execution_plane": {"pending_commitments": 0, "approval_sla_health": "ok"},
        "trust_plane": {
            "policy_violations_24h": 0,
            "risk_heatmap": {"by_sensitivity": {"S0": 0, "S1": 0, "S2": 0, "S3": 0}, "by_reversibility": {"R0": 0, "R1": 0, "R2": 0, "R3": 0}},
        },
        "data_plane": {"evidence_coverage_percent": 0.0},
        "operating_plane": {"connector_health": {"ok": 0, "degraded": 0, "error": 0, "unknown": 4}},
        "policy_violations_board": [],
        "approval_center": [],
        "live_surfaces": surfaces,
        "live_surfaces_ready": ready,
        "live_surfaces_total": len(surfaces),
        "live_surfaces_readiness_percent": round(ready / len(surfaces) * 100, 2) if surfaces else 0.0,
        "next_best_actions_ar": [
            "اربط الهوية والسياسات قبل أي التزام خارجي.",
            "فعّل evidence refs لكل طلب موافقة تجاري.",
            "اعتمد لوحات المخاطر والمخالفات كمرجع يومي للإدارة العليا.",
        ],
    }


@router.get("/snapshot")
async def operations_snapshot(
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """لقطة تشغيل: موافقات معلّقة، أحداث، تدقيق، موصلات. بدون JWT: توضيحي."""
    if not user:
        return _demo_snapshot()
    from app.services.audit_service import count_audits_since

    pending = await count_pending_approvals(db, user.tenant_id)
    ev = await count_events_since(db, user.tenant_id, 24)
    aud = await count_audits_since(db, user.tenant_id, 24)
    connectors = await list_integration_connectors(db, user.tenant_id)
    tenant_id_str = str(user.tenant_id)
    esc = await refresh_pending_escalations(db, user.tenant_id)
    recent_runs = observability_bridge.list_runs(tenant_id=tenant_id_str, limit=5)
    promoted_memories = len(memory_bridge.list_items(tenant_id=tenant_id_str, promoted_only=True, limit=500))
    media_drafts_pending = len(media_bridge.list_drafts(tenant_id=tenant_id_str, limit=500))
    approval_sla = await _approval_sla_metrics(db, user.tenant_id)
    approval_sla["escalation_by_level"] = esc.get("by_level", {})
    approval_sla["escalation_events_last_refresh"] = int(esc.get("events_emitted") or 0)
    approval_sla["alert_dispatch"] = await maybe_dispatch_sla_breach_alerts(
        db,
        user.tenant_id,
        tenant_id_str=tenant_id_str,
        metrics=approval_sla,
    )
    return {
        "demo_mode": False,
        "pending_approvals": pending,
        "domain_events_24h": ev,
        "audit_events_24h": aud,
        "connectors": connectors,
        "openclaw": {
            "recent_runs": recent_runs,
            "promoted_memories": promoted_memories,
            "media_drafts_pending": media_drafts_pending,
            "canary": get_canary_dashboard_context(tenant_id_str),
            "approval_sla": approval_sla,
        },
        "note_ar": "حلقة التشغيل: أحداث مسجّلة + تدقيق + موصلات — تُوسَّع مع المزامنة الفعلية.",
    }


@router.get("/audit-logs")
async def get_audit_logs(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "manager")),
    limit: int = 80,
):
    items = await list_recent_audits(db, user.tenant_id, limit=limit)
    return {"items": items, "count": len(items)}


@router.get("/domain-events")
async def get_domain_events(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "manager")),
    limit: int = 50,
):
    from app.models.operations import DomainEvent

    q = await db.execute(
        select(DomainEvent)
        .where(DomainEvent.tenant_id == user.tenant_id)
        .order_by(DomainEvent.created_at.desc())
        .limit(limit)
    )
    rows = q.scalars().all()
    items: List[Dict[str, Any]] = []
    for e in rows:
        items.append(
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "source": e.source,
                "payload": e.payload,
                "correlation_id": e.correlation_id,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
        )
    return {"items": items, "count": len(items)}


@router.get("/executive-control-center")
async def executive_control_center(
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Executive-ready control center for governance, approvals, risks, and live surfaces."""
    if not user:
        return _demo_control_center()

    from app.models.operations import DomainEvent

    approvals_q = await db.execute(
        select(ApprovalRequest)
        .where(ApprovalRequest.tenant_id == user.tenant_id)
        .order_by(ApprovalRequest.created_at.desc())
        .limit(200)
    )
    approvals = approvals_q.scalars().all()
    connectors = await list_integration_connectors(db, user.tenant_id)
    policy_events_q = await db.execute(
        select(DomainEvent)
        .where(
            DomainEvent.tenant_id == user.tenant_id,
            DomainEvent.event_type.in_(["approval.policy_blocked", "approval.contract_violation"]),
        )
        .order_by(DomainEvent.created_at.desc())
        .limit(50)
    )
    policy_events = policy_events_q.scalars().all()

    approval_mix: Dict[str, int] = {"auto": 0, "manager": 0, "executive": 0, "board": 0}
    risk_by_sensitivity: Dict[str, int] = {"S0": 0, "S1": 0, "S2": 0, "S3": 0}
    risk_by_reversibility: Dict[str, int] = {"R0": 0, "R1": 0, "R2": 0, "R3": 0}
    approval_center: List[Dict[str, Any]] = []
    evidence_attached = 0
    gated_count = 0

    for row in approvals:
        payload = row.payload if isinstance(row.payload, dict) else {}
        gov = payload.get("_dealix_governance") if isinstance(payload.get("_dealix_governance"), dict) else {}
        policy = payload.get("_dealix_policy") if isinstance(payload.get("_dealix_policy"), dict) else {}
        trace = payload.get("_dealix_trace") if isinstance(payload.get("_dealix_trace"), dict) else {}
        evidence_refs = payload.get("_dealix_evidence") if isinstance(payload.get("_dealix_evidence"), list) else []
        violations = payload.get("_dealix_violations") if isinstance(payload.get("_dealix_violations"), list) else []

        approval_class = str(gov.get("approval_class") or "executive").lower()
        if approval_class in approval_mix:
            approval_mix[approval_class] += 1
        sensitivity = str(gov.get("sensitivity_class") or "S2").upper()
        if sensitivity in risk_by_sensitivity:
            risk_by_sensitivity[sensitivity] += 1
        reversibility = str(gov.get("reversibility_class") or "R2").upper()
        if reversibility in risk_by_reversibility:
            risk_by_reversibility[reversibility] += 1
        requires_human_approval = bool(gov.get("requires_human_approval", policy.get("requires_approval", True)))
        if requires_human_approval:
            gated_count += 1
        if evidence_refs:
            evidence_attached += 1

        approval_center.append(
            {
                "id": str(row.id),
                "status": row.status,
                "resource_type": row.resource_type,
                "approval_class": approval_class,
                "sensitivity_class": sensitivity,
                "reversibility_class": reversibility,
                "requires_human_approval": requires_human_approval,
                "policy_class": policy.get("class"),
                "trace_id": trace.get("trace_id"),
                "correlation_id": trace.get("correlation_id"),
                "violation_count": len(violations),
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
        )

    connector_health: Dict[str, int] = {"ok": 0, "degraded": 0, "error": 0, "unknown": 0}
    for c in connectors:
        st = str(c.get("status") or "unknown")
        if st not in connector_health:
            st = "unknown"
        connector_health[st] += 1

    violations_board = [
        {
            "event_type": e.event_type,
            "payload": e.payload if isinstance(e.payload, dict) else {},
            "correlation_id": e.correlation_id,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in policy_events
    ]
    evidence_coverage = (evidence_attached / len(approvals) * 100.0) if approvals else 0.0
    human_gate_rate = (gated_count / len(approvals) * 100.0) if approvals else 0.0
    surfaces = _surface_statuses(
        has_approvals=len(approvals) > 0,
        has_evidence=evidence_attached > 0,
        has_policy_board=len(violations_board) > 0,
        has_connector_board=len(connectors) > 0,
    )
    live_ready = sum(1 for s in surfaces if s["status"] == "live")
    return {
        "demo_mode": False,
        "decision_plane": {
            "approval_class_mix": approval_mix,
            "human_gate_rate_percent": round(human_gate_rate, 2),
        },
        "execution_plane": {
            "pending_commitments": sum(1 for a in approvals if a.status == "pending"),
            "approval_sla_health": "breach" if risk_by_reversibility["R3"] > 0 else "warn" if risk_by_reversibility["R2"] > 0 else "ok",
        },
        "trust_plane": {
            "policy_violations_24h": len(violations_board),
            "risk_heatmap": {"by_sensitivity": risk_by_sensitivity, "by_reversibility": risk_by_reversibility},
        },
        "data_plane": {"evidence_coverage_percent": round(evidence_coverage, 2)},
        "operating_plane": {"connector_health": connector_health},
        "policy_violations_board": violations_board[:20],
        "approval_center": approval_center[:50],
        "live_surfaces": surfaces,
        "live_surfaces_ready": live_ready,
        "live_surfaces_total": len(surfaces),
        "live_surfaces_readiness_percent": round(live_ready / len(surfaces) * 100, 2) if surfaces else 0.0,
        "next_best_actions_ar": [
            "ارفع تغطية evidence packs للطلبات الحساسة حتى 100٪.",
            "خفّض نسبة R3/S3 المفتوحة عبر تسريع دورة الاعتماد.",
            "فعّل ربط لوحات Partner/M&A/Expansion لتكتمل أسطح القيادة المؤسسية.",
        ],
    }


class ApprovalCreate(BaseModel):
    channel: str = Field(..., description="whatsapp | email | sms")
    resource_type: str
    resource_id: UUID
    payload: Dict[str, Any] = Field(default_factory=dict)
    action: Optional[str] = None
    governance: Dict[str, Any] = Field(default_factory=dict)
    evidence_refs: List[Dict[str, Any]] = Field(default_factory=list)
    correlation_id: Optional[str] = None


class ApprovalResolve(BaseModel):
    approve: bool
    note: Optional[str] = None


@router.post("/approvals")
async def create_approval(
    body: ApprovalCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """طلب موافقة قبل إرسال — يدخل طابور pending."""
    gov = build_governance_bundle(
        channel=body.channel,
        resource_type=body.resource_type,
        payload=body.payload,
        action_hint=body.action,
        governance_input=body.governance,
        evidence_refs=body.evidence_refs,
        correlation_id=body.correlation_id,
    )
    if not gov["policy"].get("allowed", True):
        await emit_domain_event(
            db,
            tenant_id=user.tenant_id,
            event_type="approval.policy_blocked",
            payload={
                "channel": body.channel,
                "resource_type": body.resource_type,
                "action": gov["contract"].get("action"),
                "reason": gov["policy"].get("reason"),
                "approval_class": gov["contract"].get("approval_class"),
            },
            source="api",
            correlation_id=gov["trace"].get("correlation_id"),
        )
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Policy blocked this commitment.",
                "policy": gov["policy"],
                "governance": gov["contract"],
            },
        )
    payload_data = dict(body.payload or {})
    payload_data["_dealix_governance"] = gov["contract"]
    payload_data["_dealix_policy"] = gov["policy"]
    payload_data["_dealix_trace"] = gov["trace"]
    payload_data["_dealix_evidence"] = gov["evidence_refs"]
    if gov["violations"]:
        payload_data["_dealix_violations"] = gov["violations"]
    row = ApprovalRequest(
        tenant_id=user.tenant_id,
        channel=body.channel,
        resource_type=body.resource_type,
        resource_id=body.resource_id,
        payload=payload_data,
        status="pending",
        requested_by_id=user.id,
    )
    db.add(row)
    await db.flush()
    await emit_domain_event(
        db,
        tenant_id=user.tenant_id,
        event_type="approval.requested",
        payload={
            "approval_id": str(row.id),
            "channel": body.channel,
            "resource_type": body.resource_type,
            "governance": {
                "approval_class": gov["contract"].get("approval_class"),
                "reversibility_class": gov["contract"].get("reversibility_class"),
                "sensitivity_class": gov["contract"].get("sensitivity_class"),
                "plane": gov["contract"].get("plane"),
            },
        },
        source="api",
        correlation_id=gov["trace"].get("correlation_id"),
    )
    if gov["violations"]:
        await emit_domain_event(
            db,
            tenant_id=user.tenant_id,
            event_type="approval.contract_violation",
            payload={
                "approval_id": str(row.id),
                "violations": gov["violations"],
            },
            source="api",
            correlation_id=gov["trace"].get("correlation_id"),
        )
    return {
        "id": str(row.id),
        "status": row.status,
        "governance": gov["contract"],
        "policy": gov["policy"],
        "trace": gov["trace"],
        "violations": gov["violations"],
    }


@router.get("/approvals")
async def list_approvals(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    status: Optional[str] = None,
):
    q = select(ApprovalRequest).where(ApprovalRequest.tenant_id == user.tenant_id)
    if status:
        q = q.where(ApprovalRequest.status == status)
    q = q.order_by(ApprovalRequest.created_at.desc()).limit(100)
    result = await db.execute(q)
    items = []
    for a in result.scalars().all():
        pl = a.payload if isinstance(a.payload, dict) else {}
        sla_meta = pl.get("_dealix_sla") if isinstance(pl.get("_dealix_sla"), dict) else None
        governance = pl.get("_dealix_governance") if isinstance(pl.get("_dealix_governance"), dict) else {}
        policy = pl.get("_dealix_policy") if isinstance(pl.get("_dealix_policy"), dict) else {}
        trace = pl.get("_dealix_trace") if isinstance(pl.get("_dealix_trace"), dict) else {}
        evidence_refs = pl.get("_dealix_evidence") if isinstance(pl.get("_dealix_evidence"), list) else []
        violations = pl.get("_dealix_violations") if isinstance(pl.get("_dealix_violations"), list) else []
        items.append(
            {
                "id": str(a.id),
                "channel": a.channel,
                "resource_type": a.resource_type,
                "resource_id": str(a.resource_id),
                "status": a.status,
                "requested_by_id": str(a.requested_by_id),
                "payload": pl,
                "sla_escalation": sla_meta,
                "governance": governance,
                "policy": policy,
                "trace": trace,
                "evidence_refs": evidence_refs,
                "violations": violations,
                "requires_human_approval": bool(
                    governance.get("requires_human_approval", policy.get("requires_approval", True))
                ),
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
        )
    return {"items": items, "count": len(items)}


@router.get("/approvals/sla")
async def approvals_sla(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "manager")),
):
    return await _approval_sla_metrics(db, user.tenant_id)


@router.put("/approvals/{approval_id}")
async def resolve_approval(
    approval_id: UUID,
    body: ApprovalResolve,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "manager")),
):
    q = await db.execute(
        select(ApprovalRequest).where(
            ApprovalRequest.id == approval_id,
            ApprovalRequest.tenant_id == user.tenant_id,
        )
    )
    row = q.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Approval not found")
    if row.status != "pending":
        raise HTTPException(status_code=400, detail="Not pending")
    row.status = "approved" if body.approve else "rejected"
    row.reviewed_by_id = user.id
    row.reviewed_at = datetime.now(timezone.utc)
    row.note = body.note
    await db.flush()
    await emit_domain_event(
        db,
        tenant_id=user.tenant_id,
        event_type="approval.resolved",
        payload={"approval_id": str(row.id), "result": row.status},
        source="api",
    )
    return {"id": str(row.id), "status": row.status}


class ConnectorUpdate(BaseModel):
    status: str
    success: bool = False
    last_error: Optional[str] = None


@router.put("/integration-connectors/{connector_key}")
async def update_connector(
    connector_key: str,
    body: ConnectorUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin")),
):
    """تحديث حالة موصل (مزامنة يدوية أو من عامل خلفي)."""
    await upsert_connector_status(
        db,
        user.tenant_id,
        connector_key,
        status=body.status,
        last_error=body.last_error,
        success=body.success,
    )
    return {"connector_key": connector_key, "ok": True}


@router.get("/integration-connectors")
async def get_connectors(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = await list_integration_connectors(db, user.tenant_id)
    return {"items": items, "count": len(items)}
