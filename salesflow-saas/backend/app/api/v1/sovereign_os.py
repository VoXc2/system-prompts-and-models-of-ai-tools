"""Dealix Sovereign Growth, Execution & Governance OS — unified API router.

Endpoints grouped by plane and OS module:

  /sovereign/decision/*       — Decision Plane traces + model benchmark
  /sovereign/execution/*      — Durable workflow runs + HITL interrupts
  /sovereign/trust/*          — Policies, governed approvals, evidence packs, tool ledger
  /sovereign/data/*           — Cloud events, data quality, connector health
  /sovereign/operating/*      — Release gates
  /sovereign/sales/*          — Sales & Revenue OS
  /sovereign/partnership/*    — Partnership OS
  /sovereign/ma/*             — M&A / Corporate Development OS
  /sovereign/expansion/*      — Expansion OS
  /sovereign/pmi/*            — PMI / Strategic PMO OS
  /sovereign/executive/*      — Executive / Board OS (KPIs + compliance)
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sovereign_os import (
    ApprovalClass,
    CloudEventLog,
    ConnectorHealthEntry,
    DataQualityCheckpoint,
    DecisionTrace,
    DurableWorkflowRun,
    EvidencePack,
    ExecutiveKPI,
    ExpansionPlan,
    GovernedApproval,
    HITLInterrupt,
    MATarget,
    ModelBenchmarkRun,
    PMIProject,
    PartnerRecord,
    PolicyRule,
    ReleaseGate,
    SalesOpportunity,
    SaudiComplianceCheck,
    ToolVerificationEntry,
    WorkflowStatus,
)
from app.schemas.sovereign_os import (
    ApprovalReview,
    CloudEventCreate,
    CloudEventOut,
    DataQualityResult,
    DataQualityResultOut,
    DecisionTraceCreate,
    DecisionTraceOut,
    EvidencePackCreate,
    EvidencePackOut,
    ExecutiveKPIOut,
    ExpansionPlanCreate,
    ExpansionPlanOut,
    GovernedApprovalCreate,
    GovernedApprovalOut,
    HITLInterruptOut,
    HITLResolution,
    MATargetCreate,
    MATargetOut,
    ModelBenchmarkRunCreate,
    ModelBenchmarkRunOut,
    ModelRoutingReport,
    PMIProjectCreate,
    PMIProjectOut,
    PartnerRecordCreate,
    PartnerRecordOut,
    PolicyRuleCreate,
    PolicyRuleOut,
    ReleaseGateCreate,
    ReleaseGateOut,
    SalesOpportunityCreate,
    SalesOpportunityOut,
    SaudiComplianceCheckOut,
    WorkflowRunCreate,
    WorkflowRunOut,
)

router = APIRouter(prefix="/sovereign", tags=["Sovereign OS"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# DECISION PLANE
# ---------------------------------------------------------------------------

@router.post("/decision/traces", response_model=DecisionTraceOut, status_code=status.HTTP_201_CREATED)
async def log_decision_trace(
    body: DecisionTraceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trace = DecisionTrace(tenant_id=current_user.tenant_id, **body.model_dump())
    db.add(trace)
    await db.commit()
    await db.refresh(trace)
    return trace


@router.get("/decision/traces", response_model=List[DecisionTraceOut])
async def list_decision_traces(
    os_module: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(DecisionTrace).where(DecisionTrace.tenant_id == current_user.tenant_id)
    if os_module:
        q = q.where(DecisionTrace.os_module == os_module)
    if agent_id:
        q = q.where(DecisionTrace.agent_id == agent_id)
    q = q.order_by(desc(DecisionTrace.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/decision/benchmarks", response_model=ModelBenchmarkRunOut, status_code=status.HTTP_201_CREATED)
async def record_benchmark_run(
    body: ModelBenchmarkRunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = ModelBenchmarkRun(tenant_id=current_user.tenant_id, **body.model_dump())
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


@router.get("/decision/benchmarks/report", response_model=List[ModelRoutingReport])
async def get_model_routing_report(
    task_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregate benchmark stats per model to drive routing decisions."""
    q = select(ModelBenchmarkRun).where(ModelBenchmarkRun.tenant_id == current_user.tenant_id)
    if task_type:
        q = q.where(ModelBenchmarkRun.task_type == task_type)
    result = await db.execute(q)
    rows = result.scalars().all()

    by_model: dict[str, list] = {}
    for r in rows:
        by_model.setdefault(r.model_name, []).append(r)

    reports = []
    for model_name, runs in by_model.items():
        n = len(runs)
        successes = sum(1 for r in runs if r.success)
        latencies = [r.latency_ms for r in runs if r.latency_ms is not None]
        costs = [float(r.cost_usd) for r in runs if r.cost_usd is not None]
        schema_ok = [r for r in runs if r.schema_adherence is not None]
        arabic_scores = [float(r.arabic_quality_score) for r in runs if r.arabic_quality_score is not None]
        contradiction_rates = [float(r.contradiction_rate) for r in runs if r.contradiction_rate is not None]

        report = ModelRoutingReport(
            model_name=model_name,
            total_runs=n,
            success_rate=successes / n if n else 0,
            avg_latency_ms=sum(latencies) / len(latencies) if latencies else None,
            avg_cost_usd=sum(costs) / len(costs) if costs else None,
            schema_adherence_rate=sum(1 for r in schema_ok if r.schema_adherence) / len(schema_ok) if schema_ok else None,
            avg_arabic_quality=sum(arabic_scores) / len(arabic_scores) if arabic_scores else None,
            avg_contradiction_rate=sum(contradiction_rates) / len(contradiction_rates) if contradiction_rates else None,
            recommended_for=[task_type] if task_type and successes / n > 0.85 else [],
        )
        reports.append(report)

    return sorted(reports, key=lambda r: r.success_rate, reverse=True)


# ---------------------------------------------------------------------------
# EXECUTION PLANE
# ---------------------------------------------------------------------------

@router.post("/execution/workflows", response_model=WorkflowRunOut, status_code=status.HTTP_201_CREATED)
async def create_workflow_run(
    body: WorkflowRunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = DurableWorkflowRun(
        tenant_id=current_user.tenant_id,
        started_by_id=current_user.id,
        **body.model_dump(),
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


@router.get("/execution/workflows", response_model=List[WorkflowRunOut])
async def list_workflow_runs(
    os_module: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(DurableWorkflowRun).where(DurableWorkflowRun.tenant_id == current_user.tenant_id)
    if os_module:
        q = q.where(DurableWorkflowRun.os_module == os_module)
    if status_filter:
        q = q.where(DurableWorkflowRun.status == status_filter)
    q = q.order_by(desc(DurableWorkflowRun.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/execution/workflows/{run_id}", response_model=WorkflowRunOut)
async def get_workflow_run(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(DurableWorkflowRun).where(
            DurableWorkflowRun.id == run_id,
            DurableWorkflowRun.tenant_id == current_user.tenant_id,
        )
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return run


@router.get("/execution/hitl", response_model=List[HITLInterruptOut])
async def list_pending_hitl(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all unresolved HITL interrupts for this tenant."""
    q = (
        select(HITLInterrupt)
        .join(DurableWorkflowRun, HITLInterrupt.run_id == DurableWorkflowRun.id)
        .where(
            DurableWorkflowRun.tenant_id == current_user.tenant_id,
            HITLInterrupt.resolved_at.is_(None),
        )
        .order_by(HITLInterrupt.created_at)
    )
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/execution/hitl/{interrupt_id}/resolve", response_model=HITLInterruptOut)
async def resolve_hitl_interrupt(
    interrupt_id: uuid.UUID,
    body: HITLResolution,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(HITLInterrupt)
        .join(DurableWorkflowRun, HITLInterrupt.run_id == DurableWorkflowRun.id)
        .where(
            HITLInterrupt.id == interrupt_id,
            DurableWorkflowRun.tenant_id == current_user.tenant_id,
        )
    )
    interrupt = result.scalar_one_or_none()
    if not interrupt:
        raise HTTPException(status_code=404, detail="HITL interrupt not found")
    if interrupt.resolved_at:
        raise HTTPException(status_code=409, detail="Already resolved")

    interrupt.resolved_at = _now()
    interrupt.resolved_by_id = current_user.id
    interrupt.resolution = body.resolution
    interrupt.resolution_note = body.resolution_note

    run_result = await db.execute(select(DurableWorkflowRun).where(DurableWorkflowRun.id == interrupt.run_id))
    run = run_result.scalar_one_or_none()
    if run:
        run.status = WorkflowStatus.approved if body.resolution == "approved" else WorkflowStatus.rejected

    await db.commit()
    await db.refresh(interrupt)
    return interrupt


# ---------------------------------------------------------------------------
# TRUST PLANE
# ---------------------------------------------------------------------------

@router.post("/trust/policies", response_model=PolicyRuleOut, status_code=status.HTTP_201_CREATED)
async def create_policy_rule(
    body: PolicyRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    policy = PolicyRule(tenant_id=current_user.tenant_id, **body.model_dump())
    db.add(policy)
    await db.commit()
    await db.refresh(policy)
    return policy


@router.get("/trust/policies", response_model=List[PolicyRuleOut])
async def list_policy_rules(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(PolicyRule).where(PolicyRule.tenant_id == current_user.tenant_id)
    if category:
        q = q.where(PolicyRule.category == category)
    q = q.order_by(PolicyRule.name_ar)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/trust/approvals", response_model=GovernedApprovalOut, status_code=status.HTTP_201_CREATED)
async def create_governed_approval(
    body: GovernedApprovalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    approval = GovernedApproval(
        tenant_id=current_user.tenant_id,
        requested_by_id=current_user.id,
        **body.model_dump(),
    )
    db.add(approval)
    await db.commit()
    await db.refresh(approval)
    return approval


@router.get("/trust/approvals", response_model=List[GovernedApprovalOut])
async def list_governed_approvals(
    os_module: Optional[str] = None,
    approval_status: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(GovernedApproval).where(GovernedApproval.tenant_id == current_user.tenant_id)
    if os_module:
        q = q.where(GovernedApproval.os_module == os_module)
    if approval_status:
        q = q.where(GovernedApproval.status == approval_status)
    q = q.order_by(desc(GovernedApproval.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/trust/approvals/{approval_id}/review", response_model=GovernedApprovalOut)
async def review_governed_approval(
    approval_id: uuid.UUID,
    body: ApprovalReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(GovernedApproval).where(
            GovernedApproval.id == approval_id,
            GovernedApproval.tenant_id == current_user.tenant_id,
        )
    )
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval.status != "pending":
        raise HTTPException(status_code=409, detail="Approval is not pending")

    approval.status = body.status
    approval.reviewed_by_id = current_user.id
    approval.reviewed_at = _now()
    approval.review_note = body.review_note
    await db.commit()
    await db.refresh(approval)
    return approval


@router.post("/trust/evidence-packs", response_model=EvidencePackOut, status_code=status.HTTP_201_CREATED)
async def create_evidence_pack(
    body: EvidencePackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pack = EvidencePack(tenant_id=current_user.tenant_id, **body.model_dump())
    db.add(pack)
    await db.commit()
    await db.refresh(pack)
    return pack


@router.get("/trust/evidence-packs", response_model=List[EvidencePackOut])
async def list_evidence_packs(
    os_module: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(EvidencePack).where(EvidencePack.tenant_id == current_user.tenant_id)
    if os_module:
        q = q.where(EvidencePack.os_module == os_module)
    q = q.order_by(desc(EvidencePack.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/trust/evidence-packs/{pack_id}", response_model=EvidencePackOut)
async def get_evidence_pack(
    pack_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(EvidencePack).where(
            EvidencePack.id == pack_id,
            EvidencePack.tenant_id == current_user.tenant_id,
        )
    )
    pack = result.scalar_one_or_none()
    if not pack:
        raise HTTPException(status_code=404, detail="Evidence pack not found")
    return pack


@router.get("/trust/tool-ledger")
async def get_tool_ledger(
    tool_name: Optional[str] = None,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(ToolVerificationEntry).where(ToolVerificationEntry.tenant_id == current_user.tenant_id)
    if tool_name:
        q = q.where(ToolVerificationEntry.tool_name == tool_name)
    q = q.order_by(desc(ToolVerificationEntry.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# DATA PLANE
# ---------------------------------------------------------------------------

@router.post("/data/events", response_model=CloudEventOut, status_code=status.HTTP_201_CREATED)
async def publish_cloud_event(
    body: CloudEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = CloudEventLog(tenant_id=current_user.tenant_id, **body.model_dump())
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.get("/data/events", response_model=List[CloudEventOut])
async def list_cloud_events(
    event_type: Optional[str] = None,
    os_module: Optional[str] = None,
    unprocessed_only: bool = False,
    limit: int = Query(100, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(CloudEventLog).where(CloudEventLog.tenant_id == current_user.tenant_id)
    if event_type:
        q = q.where(CloudEventLog.event_type == event_type)
    if os_module:
        q = q.where(CloudEventLog.os_module == os_module)
    if unprocessed_only:
        q = q.where(CloudEventLog.processed == False)  # noqa: E712
    q = q.order_by(desc(CloudEventLog.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/data/quality", response_model=DataQualityResultOut, status_code=status.HTTP_201_CREATED)
async def record_quality_checkpoint(
    body: DataQualityResult,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = DataQualityCheckpoint(tenant_id=current_user.tenant_id, **body.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/data/quality", response_model=List[DataQualityResultOut])
async def list_quality_checkpoints(
    dataset_name: Optional[str] = None,
    passed_only: Optional[bool] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(DataQualityCheckpoint).where(DataQualityCheckpoint.tenant_id == current_user.tenant_id)
    if dataset_name:
        q = q.where(DataQualityCheckpoint.dataset_name == dataset_name)
    if passed_only is not None:
        q = q.where(DataQualityCheckpoint.passed == passed_only)
    q = q.order_by(desc(DataQualityCheckpoint.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/data/connectors")
async def list_connector_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = (
        select(ConnectorHealthEntry)
        .where(ConnectorHealthEntry.tenant_id == current_user.tenant_id)
        .order_by(ConnectorHealthEntry.connector_key)
    )
    result = await db.execute(q)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# OPERATING PLANE
# ---------------------------------------------------------------------------

@router.post("/operating/release-gates", response_model=ReleaseGateOut, status_code=status.HTTP_201_CREATED)
async def create_release_gate(
    body: ReleaseGateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    gate = ReleaseGate(
        tenant_id=current_user.tenant_id,
        deployed_by_id=current_user.id,
        **body.model_dump(),
    )
    db.add(gate)
    await db.commit()
    await db.refresh(gate)
    return gate


@router.get("/operating/release-gates", response_model=List[ReleaseGateOut])
async def list_release_gates(
    environment: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(ReleaseGate).where(ReleaseGate.tenant_id == current_user.tenant_id)
    if environment:
        q = q.where(ReleaseGate.environment == environment)
    q = q.order_by(desc(ReleaseGate.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# SALES & REVENUE OS
# ---------------------------------------------------------------------------

@router.post("/sales/opportunities", response_model=SalesOpportunityOut, status_code=status.HTTP_201_CREATED)
async def create_sales_opportunity(
    body: SalesOpportunityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    opp = SalesOpportunity(
        tenant_id=current_user.tenant_id,
        assigned_to_id=current_user.id,
        **body.model_dump(),
    )
    db.add(opp)
    await db.commit()
    await db.refresh(opp)
    return opp


@router.get("/sales/opportunities", response_model=List[SalesOpportunityOut])
async def list_sales_opportunities(
    stage: Optional[str] = None,
    channel: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(SalesOpportunity).where(SalesOpportunity.tenant_id == current_user.tenant_id)
    if stage:
        q = q.where(SalesOpportunity.stage == stage)
    if channel:
        q = q.where(SalesOpportunity.channel == channel)
    q = q.order_by(desc(SalesOpportunity.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.patch("/sales/opportunities/{opp_id}/advance")
async def advance_sales_stage(
    opp_id: uuid.UUID,
    stage: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(SalesOpportunity).where(
            SalesOpportunity.id == opp_id,
            SalesOpportunity.tenant_id == current_user.tenant_id,
        )
    )
    opp = result.scalar_one_or_none()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    opp.stage = stage
    await db.commit()
    await db.refresh(opp)
    return opp


# ---------------------------------------------------------------------------
# PARTNERSHIP OS
# ---------------------------------------------------------------------------

@router.post("/partnership/partners", response_model=PartnerRecordOut, status_code=status.HTTP_201_CREATED)
async def create_partner_record(
    body: PartnerRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    partner = PartnerRecord(tenant_id=current_user.tenant_id, **body.model_dump())
    db.add(partner)
    await db.commit()
    await db.refresh(partner)
    return partner


@router.get("/partnership/partners", response_model=List[PartnerRecordOut])
async def list_partners(
    stage: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(PartnerRecord).where(PartnerRecord.tenant_id == current_user.tenant_id)
    if stage:
        q = q.where(PartnerRecord.stage == stage)
    q = q.order_by(desc(PartnerRecord.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.patch("/partnership/partners/{partner_id}/advance")
async def advance_partner_stage(
    partner_id: uuid.UUID,
    stage: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(PartnerRecord).where(
            PartnerRecord.id == partner_id,
            PartnerRecord.tenant_id == current_user.tenant_id,
        )
    )
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    partner.stage = stage
    await db.commit()
    await db.refresh(partner)
    return partner


# ---------------------------------------------------------------------------
# M&A / CORPORATE DEVELOPMENT OS
# ---------------------------------------------------------------------------

@router.post("/ma/targets", response_model=MATargetOut, status_code=status.HTTP_201_CREATED)
async def create_ma_target(
    body: MATargetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = MATarget(tenant_id=current_user.tenant_id, **body.model_dump())
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return target


@router.get("/ma/targets", response_model=List[MATargetOut])
async def list_ma_targets(
    stage: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(MATarget).where(MATarget.tenant_id == current_user.tenant_id)
    if stage:
        q = q.where(MATarget.stage == stage)
    q = q.order_by(desc(MATarget.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.patch("/ma/targets/{target_id}/advance")
async def advance_ma_stage(
    target_id: uuid.UUID,
    stage: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MATarget).where(
            MATarget.id == target_id,
            MATarget.tenant_id == current_user.tenant_id,
        )
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="M&A target not found")
    target.stage = stage
    await db.commit()
    await db.refresh(target)
    return target


# ---------------------------------------------------------------------------
# EXPANSION OS
# ---------------------------------------------------------------------------

@router.post("/expansion/plans", response_model=ExpansionPlanOut, status_code=status.HTTP_201_CREATED)
async def create_expansion_plan(
    body: ExpansionPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = ExpansionPlan(tenant_id=current_user.tenant_id, **body.model_dump())
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


@router.get("/expansion/plans", response_model=List[ExpansionPlanOut])
async def list_expansion_plans(
    stage: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(ExpansionPlan).where(ExpansionPlan.tenant_id == current_user.tenant_id)
    if stage:
        q = q.where(ExpansionPlan.stage == stage)
    q = q.order_by(desc(ExpansionPlan.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# PMI / STRATEGIC PMO OS
# ---------------------------------------------------------------------------

@router.post("/pmi/projects", response_model=PMIProjectOut, status_code=status.HTTP_201_CREATED)
async def create_pmi_project(
    body: PMIProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = PMIProject(tenant_id=current_user.tenant_id, **body.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/pmi/projects", response_model=List[PMIProjectOut])
async def list_pmi_projects(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(PMIProject).where(PMIProject.tenant_id == current_user.tenant_id)
    if status_filter:
        q = q.where(PMIProject.status == status_filter)
    q = q.order_by(desc(PMIProject.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


# ---------------------------------------------------------------------------
# EXECUTIVE / BOARD OS
# ---------------------------------------------------------------------------

@router.get("/executive/kpis", response_model=List[ExecutiveKPIOut])
async def list_executive_kpis(
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = (
        select(ExecutiveKPI)
        .where(ExecutiveKPI.tenant_id == current_user.tenant_id)
        .order_by(desc(ExecutiveKPI.created_at))
        .limit(limit)
    )
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/executive/dashboard")
async def get_executive_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Composite executive dashboard — aggregates all live surfaces."""
    tenant_id = current_user.tenant_id

    async def count_q(model, **filters):
        q = select(func.count()).select_from(model).where(model.tenant_id == tenant_id)
        for col, val in filters.items():
            q = q.where(getattr(model, col) == val)
        r = await db.execute(q)
        return r.scalar() or 0

    open_approvals = await count_q(GovernedApproval, status="pending")
    policy_violations = await count_q(SaudiComplianceCheck, passed=False)
    active_workflows = await count_q(DurableWorkflowRun, status=WorkflowStatus.running.value)
    pending_hitl = await count_q(HITLInterrupt)

    ma_pipeline = await db.execute(
        select(func.count()).select_from(MATarget).where(MATarget.tenant_id == tenant_id)
    )
    partner_pipeline = await db.execute(
        select(func.count()).select_from(PartnerRecord).where(PartnerRecord.tenant_id == tenant_id)
    )
    sales_pipeline = await db.execute(
        select(func.count()).select_from(SalesOpportunity).where(SalesOpportunity.tenant_id == tenant_id)
    )

    latest_kpi_r = await db.execute(
        select(ExecutiveKPI)
        .where(ExecutiveKPI.tenant_id == tenant_id)
        .order_by(desc(ExecutiveKPI.created_at))
        .limit(1)
    )
    latest_kpi = latest_kpi_r.scalar_one_or_none()

    return {
        "open_approvals": open_approvals,
        "policy_violations": policy_violations,
        "active_workflows": active_workflows,
        "pending_hitl": pending_hitl,
        "ma_pipeline_count": ma_pipeline.scalar() or 0,
        "partner_pipeline_count": partner_pipeline.scalar() or 0,
        "sales_pipeline_count": sales_pipeline.scalar() or 0,
        "latest_kpi": latest_kpi,
        "generated_at": _now().isoformat(),
    }


@router.get("/executive/compliance", response_model=List[SaudiComplianceCheckOut])
async def list_compliance_checks(
    check_type: Optional[str] = None,
    passed_only: Optional[bool] = None,
    os_module: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(SaudiComplianceCheck).where(SaudiComplianceCheck.tenant_id == current_user.tenant_id)
    if check_type:
        q = q.where(SaudiComplianceCheck.check_type == check_type)
    if passed_only is not None:
        q = q.where(SaudiComplianceCheck.passed == passed_only)
    if os_module:
        q = q.where(SaudiComplianceCheck.os_module == os_module)
    q = q.order_by(desc(SaudiComplianceCheck.created_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()
