"""Sovereign Trust Plane: policies, evaluations, tool verification, compliance."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sovereign_trust import (
    PolicyRule,
    PolicyEvaluation,
    ToolVerification,
    ComplianceMapping,
)
from app.schemas.sovereign import (
    PolicyRuleCreate,
    PolicyRuleResponse,
    PolicyEvaluateRequest,
    PolicyEvaluationResponse,
    ToolVerificationCreate,
    ToolVerificationResponse,
    ComplianceMappingCreate,
    ComplianceMappingResponse,
)

router = APIRouter(prefix="/sovereign/trust", tags=["Sovereign Trust Plane"])


# ── Policy Rules ──────────────────────────────────────────────

@router.post("/policies", response_model=PolicyRuleResponse, status_code=201)
async def create_policy(
    data: PolicyRuleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rule = PolicyRule(
        tenant_id=current_user.tenant_id,
        **data.model_dump(exclude_none=True),
    )
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return PolicyRuleResponse.model_validate(rule)


@router.get("/policies", response_model=List[PolicyRuleResponse])
async def list_policies(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(PolicyRule).where(PolicyRule.tenant_id == current_user.tenant_id)
    if category:
        q = q.where(PolicyRule.policy_category == category)
    q = q.order_by(PolicyRule.created_at.desc())
    result = await db.execute(q)
    return [PolicyRuleResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/policies/evaluate", response_model=PolicyEvaluationResponse, status_code=201)
async def evaluate_policy(
    data: PolicyEvaluateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rule_q = await db.execute(
        select(PolicyRule).where(
            PolicyRule.id == data.rule_id,
            PolicyRule.tenant_id == current_user.tenant_id,
        )
    )
    rule = rule_q.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Policy rule not found")

    evaluation_result = "pass" if rule.is_active else "skipped"

    evaluation = PolicyEvaluation(
        tenant_id=current_user.tenant_id,
        rule_id=data.rule_id,
        action_type=data.action_type,
        actor_id=current_user.id,
        target_entity_type=data.target_entity_type,
        target_entity_id=data.target_entity_id,
        evaluation_result=evaluation_result,
        input_context=data.input_context,
    )
    db.add(evaluation)
    await db.flush()
    await db.refresh(evaluation)
    return PolicyEvaluationResponse.model_validate(evaluation)


# ── Policy Violations ─────────────────────────────────────────

@router.get("/violations", response_model=List[PolicyEvaluationResponse])
async def list_violations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(PolicyEvaluation)
        .where(
            PolicyEvaluation.tenant_id == current_user.tenant_id,
            PolicyEvaluation.evaluation_result == "violation",
        )
        .order_by(PolicyEvaluation.created_at.desc())
    )
    result = await db.execute(q)
    return [PolicyEvaluationResponse.model_validate(r) for r in result.scalars().all()]


# ── Tool Verification ─────────────────────────────────────────

@router.post("/tool-verifications", response_model=ToolVerificationResponse, status_code=201)
async def log_tool_verification(
    data: ToolVerificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tv = ToolVerification(
        tenant_id=current_user.tenant_id,
        **data.model_dump(exclude_none=True),
    )
    db.add(tv)
    await db.flush()
    await db.refresh(tv)
    return ToolVerificationResponse.model_validate(tv)


@router.get("/tool-verifications", response_model=List[ToolVerificationResponse])
async def list_tool_verifications(
    tool_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(ToolVerification).where(ToolVerification.tenant_id == current_user.tenant_id)
    if tool_name:
        q = q.where(ToolVerification.tool_name == tool_name)
    q = q.order_by(ToolVerification.created_at.desc())
    result = await db.execute(q)
    return [ToolVerificationResponse.model_validate(r) for r in result.scalars().all()]


# ── Compliance Mappings ───────────────────────────────────────

@router.post("/compliance-mappings", response_model=ComplianceMappingResponse, status_code=201)
async def create_compliance_mapping(
    data: ComplianceMappingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    mapping = ComplianceMapping(
        tenant_id=current_user.tenant_id,
        owner_id=current_user.id,
        **data.model_dump(exclude_none=True),
    )
    db.add(mapping)
    await db.flush()
    await db.refresh(mapping)
    return ComplianceMappingResponse.model_validate(mapping)


@router.get("/compliance-mappings", response_model=List[ComplianceMappingResponse])
async def list_compliance_mappings(
    framework: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(ComplianceMapping).where(ComplianceMapping.tenant_id == current_user.tenant_id)
    if framework:
        q = q.where(ComplianceMapping.framework == framework)
    q = q.order_by(ComplianceMapping.created_at.desc())
    result = await db.execute(q)
    return [ComplianceMappingResponse.model_validate(r) for r in result.scalars().all()]


# ── Saudi Compliance Matrix ───────────────────────────────────

@router.get("/compliance-matrix")
async def compliance_matrix(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Saudi Compliance Matrix: aggregated status by framework."""
    tid = current_user.tenant_id
    q = await db.execute(
        select(ComplianceMapping.framework, ComplianceMapping.status, func.count())
        .where(ComplianceMapping.tenant_id == tid)
        .group_by(ComplianceMapping.framework, ComplianceMapping.status)
    )
    matrix: dict = {}
    for framework, status, count in q.all():
        matrix.setdefault(framework, {})[status] = count
    return {"frameworks": matrix}


# ── Tool Verification Ledger ──────────────────────────────────

@router.get("/tool-ledger")
async def tool_ledger(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Tool Verification Ledger: aggregated stats by tool."""
    tid = current_user.tenant_id
    q = await db.execute(
        select(
            ToolVerification.tool_name,
            func.count(),
            func.sum(func.cast(ToolVerification.success, type_=func.coalesce.type)),
        )
        .where(ToolVerification.tenant_id == tid)
        .group_by(ToolVerification.tool_name)
    )
    # Simpler aggregation avoiding cast issues
    all_q = await db.execute(
        select(ToolVerification).where(ToolVerification.tenant_id == tid)
    )
    rows = all_q.scalars().all()
    tools: dict = {}
    for tv in rows:
        entry = tools.setdefault(tv.tool_name, {"total": 0, "success": 0, "failure": 0})
        entry["total"] += 1
        if tv.success:
            entry["success"] += 1
        else:
            entry["failure"] += 1
    return {"tools": tools}
