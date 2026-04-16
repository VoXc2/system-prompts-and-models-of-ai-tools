"""Pydantic v2 schemas for Dealix Sovereign OS — all five planes + six OS modules."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.sovereign_os import (
    ApprovalClass,
    ReversibilityClass,
    SensitivityClass,
    WorkflowStatus,
)


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------

class OsModuleEnum(str):
    sales = "sales"
    partnership = "partnership"
    ma = "ma"
    expansion = "expansion"
    pmi = "pmi"
    executive = "executive"


# ---------------------------------------------------------------------------
# DECISION PLANE
# ---------------------------------------------------------------------------

class DecisionTraceCreate(BaseModel):
    trace_id: str
    agent_id: Optional[str] = None
    model_used: str
    input_summary: Optional[str] = None
    structured_output: Optional[dict] = None
    tool_calls: Optional[List[dict]] = None
    guardrail_events: Optional[List[dict]] = None
    latency_ms: Optional[int] = None
    token_count: Optional[int] = None
    cost_usd: Optional[Decimal] = None
    schema_adhered: Optional[bool] = None
    contradiction_detected: bool = False
    arabic_quality_score: Optional[Decimal] = None
    os_module: Optional[str] = None
    correlation_id: Optional[str] = None


class DecisionTraceOut(DecisionTraceCreate):
    id: UUID
    tenant_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ModelBenchmarkRunCreate(BaseModel):
    model_name: str
    task_type: str
    language: str = "ar"
    latency_ms: Optional[int] = None
    success: bool
    schema_adherence: Optional[bool] = None
    tool_call_reliability: Optional[Decimal] = None
    contradiction_rate: Optional[Decimal] = None
    arabic_quality_score: Optional[Decimal] = None
    cost_usd: Optional[Decimal] = None
    benchmark_payload: Optional[dict] = None
    result_payload: Optional[dict] = None


class ModelBenchmarkRunOut(ModelBenchmarkRunCreate):
    id: UUID
    tenant_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ModelRoutingReport(BaseModel):
    """Aggregated routing report across all benchmark runs."""
    model_name: str
    total_runs: int
    success_rate: float
    avg_latency_ms: Optional[float]
    avg_cost_usd: Optional[float]
    schema_adherence_rate: Optional[float]
    avg_arabic_quality: Optional[float]
    avg_contradiction_rate: Optional[float]
    recommended_for: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# EXECUTION PLANE
# ---------------------------------------------------------------------------

class WorkflowRunCreate(BaseModel):
    workflow_type: str
    os_module: str
    state_snapshot: Optional[dict] = None
    deadline_at: Optional[datetime] = None
    correlation_id: Optional[str] = None
    external_ref: Optional[str] = None


class WorkflowRunOut(BaseModel):
    id: UUID
    tenant_id: UUID
    workflow_type: str
    os_module: str
    status: WorkflowStatus
    current_step: Optional[str]
    state_snapshot: dict
    started_by_id: Optional[UUID]
    completed_at: Optional[datetime]
    deadline_at: Optional[datetime]
    correlation_id: Optional[str]
    external_ref: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HITLInterruptOut(BaseModel):
    id: UUID
    run_id: UUID
    step_name: str
    action_description: str
    action_description_ar: Optional[str]
    approval_class: ApprovalClass
    reversibility: ReversibilityClass
    sensitivity: SensitivityClass
    financial_impact_sar: Optional[Decimal]
    alternatives: List[Any]
    risks: List[Any]
    resolved_at: Optional[datetime]
    resolution: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class HITLResolution(BaseModel):
    resolution: str = Field(..., pattern="^(approved|rejected)$")
    resolution_note: Optional[str] = None


# ---------------------------------------------------------------------------
# TRUST PLANE
# ---------------------------------------------------------------------------

class PolicyRuleCreate(BaseModel):
    rule_id: str
    name_ar: str
    name_en: Optional[str] = None
    category: str
    rego_snippet: Optional[str] = None
    json_condition: Optional[dict] = None
    approval_class: ApprovalClass = ApprovalClass.B
    reversibility: ReversibilityClass = ReversibilityClass.irreversible
    sensitivity: SensitivityClass = SensitivityClass.high
    is_active: bool = True
    pdpl_relevant: bool = False
    nca_relevant: bool = False


class PolicyRuleOut(PolicyRuleCreate):
    id: UUID
    tenant_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class GovernedApprovalCreate(BaseModel):
    title_ar: str
    title_en: Optional[str] = None
    description_ar: Optional[str] = None
    resource_type: str
    resource_id: Optional[UUID] = None
    os_module: str
    approval_class: ApprovalClass = ApprovalClass.B
    reversibility: ReversibilityClass = ReversibilityClass.irreversible
    sensitivity: SensitivityClass = SensitivityClass.high
    financial_impact_sar: Optional[Decimal] = None
    policy_rule_id: Optional[str] = None
    evidence: Optional[dict] = None
    alternatives: Optional[List[Any]] = None
    risks: Optional[List[Any]] = None
    assigned_to_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None
    workflow_run_id: Optional[UUID] = None
    correlation_id: Optional[str] = None


class GovernedApprovalOut(GovernedApprovalCreate):
    id: UUID
    tenant_id: UUID
    status: str
    requested_by_id: UUID
    reviewed_by_id: Optional[UUID]
    reviewed_at: Optional[datetime]
    review_note: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovalReview(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    review_note: Optional[str] = None


class EvidencePackCreate(BaseModel):
    title_ar: str
    title_en: Optional[str] = None
    os_module: str
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    evidence_items: Optional[List[Any]] = None
    summary_ar: Optional[str] = None
    summary_en: Optional[str] = None
    financial_summary: Optional[dict] = None
    risk_summary: Optional[List[Any]] = None
    recommendation_ar: Optional[str] = None
    assembled_by_agent: Optional[str] = None
    trace_id: Optional[str] = None
    correlation_id: Optional[str] = None


class EvidencePackOut(EvidencePackCreate):
    id: UUID
    tenant_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# DATA PLANE
# ---------------------------------------------------------------------------

class CloudEventCreate(BaseModel):
    event_type: str
    source: str
    subject: Optional[str] = None
    data_schema: Optional[str] = None
    data_content_type: str = "application/json"
    data: Optional[dict] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    os_module: Optional[str] = None


class CloudEventOut(CloudEventCreate):
    id: UUID
    tenant_id: UUID
    spec_version: str
    processed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DataQualityResult(BaseModel):
    checkpoint_name: str
    dataset_name: str
    os_module: Optional[str] = None
    passed: bool
    total_expectations: int
    passed_expectations: int
    failed_expectations: int
    failure_details: Optional[List[Any]] = None
    run_id: Optional[str] = None


class DataQualityResultOut(DataQualityResult):
    id: UUID
    tenant_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# OPERATING PLANE
# ---------------------------------------------------------------------------

class ReleaseGateCreate(BaseModel):
    release_tag: str
    environment: str
    required_checks: Optional[List[Any]] = None
    canary_percentage: int = 0
    rollback_plan_ar: Optional[str] = None
    audit_stream_url: Optional[str] = None


class ReleaseGateOut(ReleaseGateCreate):
    id: UUID
    tenant_id: UUID
    status: str
    passed_checks: List[Any]
    failed_checks: List[Any]
    oidc_verified: bool
    artifact_attestation_id: Optional[str]
    provenance_url: Optional[str]
    deployed_by_id: Optional[UUID]
    approved_by_id: Optional[UUID]
    deployed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# OS MODULE SCHEMAS
# ---------------------------------------------------------------------------

class SalesOpportunityCreate(BaseModel):
    title_ar: str
    title_en: Optional[str] = None
    lead_id: Optional[UUID] = None
    company_id: Optional[UUID] = None
    value_sar: Optional[Decimal] = None
    channel: Optional[str] = None
    extra_data: Optional[dict] = None


class SalesOpportunityOut(SalesOpportunityCreate):
    id: UUID
    tenant_id: UUID
    stage: str
    score: Optional[int]
    assigned_to_id: Optional[UUID]
    proposal_id: Optional[UUID]
    approval_id: Optional[UUID]
    workflow_run_id: Optional[UUID]
    margin_check_passed: Optional[bool]
    discount_approved: Optional[bool]
    esignature_sent_at: Optional[datetime]
    esignature_completed_at: Optional[datetime]
    onboarding_triggered_at: Optional[datetime]
    renewal_due_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PartnerRecordCreate(BaseModel):
    partner_name_ar: str
    partner_name_en: Optional[str] = None
    channel_type: Optional[str] = None
    rev_share_pct: Optional[Decimal] = None
    exclusivity: bool = False
    market_commitment: Optional[str] = None
    extra_data: Optional[dict] = None


class PartnerRecordOut(PartnerRecordCreate):
    id: UUID
    tenant_id: UUID
    stage: str
    strategic_fit_score: Optional[int]
    term_sheet_url: Optional[str]
    term_sheet_approved_at: Optional[datetime]
    signature_completed_at: Optional[datetime]
    activation_at: Optional[datetime]
    health_score: Optional[int]
    contribution_margin_sar: Optional[Decimal]
    renewal_due_at: Optional[datetime]
    workflow_run_id: Optional[UUID]
    approval_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MATargetCreate(BaseModel):
    target_name_ar: str
    target_name_en: Optional[str] = None
    extra_data: Optional[dict] = None


class MATargetOut(MATargetCreate):
    id: UUID
    tenant_id: UUID
    stage: str
    strategic_fit_score: Optional[int]
    ownership_structure: dict
    dd_status: dict
    valuation_range_sar: dict
    synergy_model: dict
    offer_sent_at: Optional[datetime]
    offer_amount_sar: Optional[Decimal]
    signing_at: Optional[datetime]
    close_at: Optional[datetime]
    pmi_triggered_at: Optional[datetime]
    workflow_run_id: Optional[UUID]
    approval_id: Optional[UUID]
    evidence_pack_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExpansionPlanCreate(BaseModel):
    market_ar: str
    market_en: Optional[str] = None
    segment: Optional[str] = None
    gtm_doc: Optional[dict] = None
    extra_data: Optional[dict] = None


class ExpansionPlanOut(ExpansionPlanCreate):
    id: UUID
    tenant_id: UUID
    stage: str
    readiness_score: Optional[int]
    canary_pct: int
    stop_loss_triggered: bool
    stop_loss_reason: Optional[str]
    launch_at: Optional[datetime]
    post_launch_review_at: Optional[datetime]
    workflow_run_id: Optional[UUID]
    approval_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PMIProjectCreate(BaseModel):
    name_ar: str
    name_en: Optional[str] = None
    ma_target_id: Optional[UUID] = None
    program_type: str = "pmi"
    extra_data: Optional[dict] = None


class PMIProjectOut(PMIProjectCreate):
    id: UUID
    tenant_id: UUID
    status: str
    day1_readiness: dict
    plan_30d: dict
    plan_60d: dict
    plan_90d: dict
    synergy_realized_pct: Optional[Decimal]
    risk_register: List[Any]
    issue_count_open: int
    workflow_run_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExecutiveKPIOut(BaseModel):
    id: UUID
    tenant_id: UUID
    period_label: str
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    revenue_actual_sar: Optional[Decimal]
    revenue_forecast_sar: Optional[Decimal]
    pipeline_value_sar: Optional[Decimal]
    partner_pipeline_sar: Optional[Decimal]
    ma_pipeline_value_sar: Optional[Decimal]
    open_approvals: int
    policy_violations: int
    risk_heatmap: dict
    next_best_actions: List[Any]
    escalations: List[Any]
    generated_by_agent: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class SaudiComplianceCheckOut(BaseModel):
    id: UUID
    tenant_id: UUID
    check_type: str
    resource_type: str
    resource_id: Optional[UUID]
    os_module: Optional[str]
    passed: bool
    control_ids: List[Any]
    violations: List[Any]
    remediation_steps: List[Any]
    remediation_steps_ar: List[Any]
    auto_remediated: bool
    created_at: datetime

    model_config = {"from_attributes": True}
