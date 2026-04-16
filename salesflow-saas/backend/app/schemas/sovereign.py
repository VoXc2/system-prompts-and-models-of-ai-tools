"""Pydantic schemas for Dealix Sovereign Enterprise Growth OS."""
from datetime import datetime
from typing import Optional, List, Any, Dict
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# ── Decision Plane ─────────────────────────────────────────────

class AIRecommendationCreate(BaseModel):
    recommendation_type: str = Field(..., max_length=80)
    title: str = Field(..., max_length=500)
    title_ar: Optional[str] = Field(None, max_length=500)
    summary: str
    summary_ar: Optional[str] = None
    evidence_sources: List[Dict[str, Any]] = Field(default_factory=list)
    assumptions: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_score: float = Field(0.0, ge=0, le=1)
    freshness_at: Optional[datetime] = None
    model_version: Optional[str] = None
    model_lane: Optional[str] = None
    policy_notes: Optional[str] = None
    alternatives: Optional[List[Dict[str, Any]]] = None
    target_entity_type: Optional[str] = None
    target_entity_id: Optional[UUID] = None

class AIRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    recommendation_type: str
    title: str
    title_ar: Optional[str] = None
    summary: str
    summary_ar: Optional[str] = None
    evidence_sources: List[Dict[str, Any]] = []
    assumptions: List[Dict[str, Any]] = []
    confidence_score: float
    freshness_at: Optional[datetime] = None
    model_version: Optional[str] = None
    model_lane: Optional[str] = None
    policy_notes: Optional[str] = None
    alternatives: Optional[List[Dict[str, Any]]] = None
    status: str
    approved_by_id: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    target_entity_type: Optional[str] = None
    target_entity_id: Optional[UUID] = None
    provenance_chain: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

class AIRecommendationUpdate(BaseModel):
    status: Optional[str] = None
    policy_notes: Optional[str] = None
    alternatives: Optional[List[Dict[str, Any]]] = None

class ContradictionRecordCreate(BaseModel):
    recommendation_id: Optional[UUID] = None
    intended_action: str
    claimed_action: str
    actual_tool_call: Optional[str] = None
    side_effects: Optional[Dict[str, Any]] = None
    contradiction_status: str = Field("none", max_length=30)

class ContradictionRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    recommendation_id: Optional[UUID] = None
    intended_action: str
    claimed_action: str
    actual_tool_call: Optional[str] = None
    side_effects: Optional[Dict[str, Any]] = None
    contradiction_status: str
    resolution_notes: Optional[str] = None
    resolved_by_id: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime


# ── Execution Plane ────────────────────────────────────────────

class DurableWorkflowCreate(BaseModel):
    workflow_type: str = Field(..., max_length=80)
    title: str = Field(..., max_length=500)
    title_ar: Optional[str] = Field(None, max_length=500)
    target_entity_type: Optional[str] = None
    target_entity_id: Optional[UUID] = None
    timeout_seconds: Optional[int] = None
    max_retries: int = 3
    compensation_plan: Optional[Dict[str, Any]] = None

class DurableWorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    workflow_type: str
    title: str
    title_ar: Optional[str] = None
    status: str
    current_step: Optional[str] = None
    total_steps: int
    completed_steps: int
    idempotency_key: str
    is_resumable: bool
    is_compensatable: bool
    compensation_plan: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    initiator_id: UUID
    target_entity_type: Optional[str] = None
    target_entity_id: Optional[UUID] = None
    retry_count: int
    max_retries: int
    correlation_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class DurableWorkflowUpdate(BaseModel):
    status: Optional[str] = None
    current_step: Optional[str] = None
    error_message: Optional[str] = None

class WorkflowStepCreate(BaseModel):
    step_name: str = Field(..., max_length=120)
    step_type: str = Field(..., max_length=50)
    input_data: Optional[Dict[str, Any]] = None
    assigned_to_id: Optional[UUID] = None

class WorkflowStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    workflow_id: UUID
    step_order: int
    step_name: str
    step_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    assigned_to_id: Optional[UUID] = None
    approval_status: Optional[str] = None
    approval_note: Optional[str] = None
    created_at: datetime

class WorkflowStepUpdate(BaseModel):
    status: Optional[str] = None
    error_message: Optional[str] = None


# ── Trust Plane ────────────────────────────────────────────────

class PolicyRuleCreate(BaseModel):
    rule_code: str = Field(..., max_length=120)
    rule_name: str = Field(..., max_length=255)
    rule_name_ar: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    policy_category: str = Field(..., max_length=80)
    rule_definition: Dict[str, Any]
    severity: str = Field("warning", max_length=30)
    is_active: bool = True
    applies_to_roles: Optional[List[str]] = None
    applies_to_entities: Optional[List[str]] = None

class PolicyRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    rule_code: str
    rule_name: str
    rule_name_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    policy_category: str
    rule_definition: Dict[str, Any]
    severity: str
    is_active: bool
    applies_to_roles: Optional[List[str]] = None
    applies_to_entities: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

class PolicyEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    rule_id: UUID
    action_type: str
    actor_id: UUID
    target_entity_type: Optional[str] = None
    target_entity_id: Optional[UUID] = None
    evaluation_result: str
    input_context: Optional[Dict[str, Any]] = None
    violation_details: Optional[str] = None
    violation_details_ar: Optional[str] = None
    created_at: datetime

class ToolVerificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    tool_name: str
    tool_version: Optional[str] = None
    invocation_id: str
    invoked_by: str
    input_hash: Optional[str] = None
    output_hash: Optional[str] = None
    execution_time_ms: Optional[int] = None
    success: bool
    error_message: Optional[str] = None
    side_effects: Optional[Dict[str, Any]] = None
    created_at: datetime

class PolicyEvaluateRequest(BaseModel):
    rule_id: UUID
    action_type: str
    target_entity_type: Optional[str] = None
    target_entity_id: Optional[UUID] = None
    input_context: Optional[Dict[str, Any]] = None

class ToolVerificationCreate(BaseModel):
    tool_name: str = Field(..., max_length=120)
    tool_version: Optional[str] = None
    invocation_id: str = Field(..., max_length=120)
    invoked_by: str = Field(..., max_length=80)
    input_hash: Optional[str] = None
    output_hash: Optional[str] = None
    execution_time_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    side_effects: Optional[Dict[str, Any]] = None

class ComplianceMappingCreate(BaseModel):
    framework: str = Field(..., max_length=80)
    control_id: str = Field(..., max_length=80)
    control_name: str = Field(..., max_length=255)
    control_name_ar: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_ar: Optional[str] = None
    status: str = "not_started"
    evidence_refs: Optional[List[Dict[str, Any]]] = None
    risk_level: str = "medium"

class ComplianceMappingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    framework: str
    control_id: str
    control_name: str
    control_name_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    status: str
    evidence_refs: Optional[List[Dict[str, Any]]] = None
    owner_id: Optional[UUID] = None
    last_assessed_at: Optional[datetime] = None
    next_review_at: Optional[datetime] = None
    risk_level: str
    created_at: datetime
    updated_at: datetime


# ── Partnership OS ─────────────────────────────────────────────

class PartnerCreate(BaseModel):
    name: str = Field(..., max_length=255)
    name_ar: Optional[str] = Field(None, max_length=255)
    partner_type: str = Field(..., max_length=80)
    strategic_fit_score: Optional[float] = None
    channel_economics: Optional[Dict[str, Any]] = None
    contribution_margin: Optional[float] = None
    currency: str = "SAR"
    alliance_structure: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None
    notes_ar: Optional[str] = None

class PartnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    name: str
    name_ar: Optional[str] = None
    partner_type: str
    status: str
    strategic_fit_score: Optional[float] = None
    channel_economics: Optional[Dict[str, Any]] = None
    contribution_margin: Optional[float] = None
    currency: str
    alliance_structure: Optional[str] = None
    term_sheet_url: Optional[str] = None
    activated_at: Optional[datetime] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None
    notes_ar: Optional[str] = None
    scorecard_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class PartnerUpdate(BaseModel):
    name: Optional[str] = None
    name_ar: Optional[str] = None
    status: Optional[str] = None
    strategic_fit_score: Optional[float] = None
    channel_economics: Optional[Dict[str, Any]] = None
    scorecard_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    notes_ar: Optional[str] = None


# ── M&A / CorpDev OS ──────────────────────────────────────────

class MATargetCreate(BaseModel):
    company_name: str = Field(..., max_length=255)
    company_name_ar: Optional[str] = Field(None, max_length=255)
    sector: Optional[str] = None
    valuation_low: Optional[float] = None
    valuation_high: Optional[float] = None
    currency: str = "SAR"
    synergy_model: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class MATargetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    company_name: str
    company_name_ar: Optional[str] = None
    sector: Optional[str] = None
    status: str
    valuation_low: Optional[float] = None
    valuation_high: Optional[float] = None
    currency: str
    synergy_model: Optional[Dict[str, Any]] = None
    dd_room_access: Optional[List[str]] = None
    investment_memo_url: Optional[str] = None
    board_pack_url: Optional[str] = None
    offer_strategy: Optional[Dict[str, Any]] = None
    signing_readiness: bool
    close_readiness: bool
    assigned_to_id: Optional[UUID] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class MATargetUpdate(BaseModel):
    status: Optional[str] = None
    valuation_low: Optional[float] = None
    valuation_high: Optional[float] = None
    synergy_model: Optional[Dict[str, Any]] = None
    offer_strategy: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


# ── Expansion OS ───────────────────────────────────────────────

class ExpansionMarketCreate(BaseModel):
    market_name: str = Field(..., max_length=255)
    market_name_ar: Optional[str] = Field(None, max_length=255)
    country_code: str = Field(..., max_length=3)
    region: Optional[str] = None
    priority_score: Optional[float] = None
    currency: str = "SAR"
    notes: Optional[str] = None

class ExpansionMarketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    market_name: str
    market_name_ar: Optional[str] = None
    country_code: str
    region: Optional[str] = None
    status: str
    priority_score: Optional[float] = None
    compliance_readiness: Optional[Dict[str, Any]] = None
    localization_status: Optional[Dict[str, Any]] = None
    pricing_plan: Optional[Dict[str, Any]] = None
    channel_plan: Optional[Dict[str, Any]] = None
    launch_date: Optional[datetime] = None
    stop_loss_threshold: Optional[float] = None
    actual_vs_forecast: Optional[Dict[str, Any]] = None
    currency: str
    assigned_to_id: Optional[UUID] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ExpansionMarketUpdate(BaseModel):
    status: Optional[str] = None
    priority_score: Optional[float] = None
    compliance_readiness: Optional[Dict[str, Any]] = None
    localization_status: Optional[Dict[str, Any]] = None
    pricing_plan: Optional[Dict[str, Any]] = None
    channel_plan: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


# ── PMI / PMO OS ───────────────────────────────────────────────

class PMIProgramCreate(BaseModel):
    title: str = Field(..., max_length=500)
    title_ar: Optional[str] = Field(None, max_length=500)
    ma_target_id: Optional[UUID] = None

class PMIProgramResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    title: str
    title_ar: Optional[str] = None
    ma_target_id: Optional[UUID] = None
    status: str
    day1_readiness: Optional[Dict[str, Any]] = None
    integration_plan_30: Optional[Dict[str, Any]] = None
    integration_plan_60: Optional[Dict[str, Any]] = None
    integration_plan_90: Optional[Dict[str, Any]] = None
    synergy_realization: Optional[Dict[str, Any]] = None
    risk_register: Optional[Dict[str, Any]] = None
    owner_id: Optional[UUID] = None
    next_review_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class PMITaskCreate(BaseModel):
    program_id: UUID
    title: str = Field(..., max_length=500)
    title_ar: Optional[str] = Field(None, max_length=500)
    priority: str = "medium"
    phase: str = "day30"
    assigned_to_id: Optional[UUID] = None
    depends_on: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None

class PMITaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    program_id: UUID
    title: str
    title_ar: Optional[str] = None
    status: str
    priority: str
    phase: str
    assigned_to_id: Optional[UUID] = None
    depends_on: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime


# ── Connector Facade ───────────────────────────────────────────

class ConnectorDefinitionCreate(BaseModel):
    connector_key: str = Field(..., max_length=80)
    display_name: str = Field(..., max_length=255)
    display_name_ar: Optional[str] = Field(None, max_length=255)
    version: str = Field(..., max_length=20)
    provider: str = Field(..., max_length=120)
    contract_schema: Dict[str, Any]
    retry_policy: Optional[Dict[str, Any]] = None
    timeout_seconds: int = 30
    idempotency_key_template: Optional[str] = None
    action_class: str = "auto"
    audit_events: Optional[List[str]] = None
    telemetry_config: Optional[Dict[str, Any]] = None
    compensation_notes: Optional[str] = None

class ConnectorDefinitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    connector_key: str
    display_name: str
    display_name_ar: Optional[str] = None
    version: str
    provider: str
    contract_schema: Dict[str, Any]
    retry_policy: Optional[Dict[str, Any]] = None
    timeout_seconds: int
    idempotency_key_template: Optional[str] = None
    action_class: str
    audit_events: Optional[List[str]] = None
    telemetry_config: Optional[Dict[str, Any]] = None
    compensation_notes: Optional[str] = None
    is_active: bool
    last_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ConnectorHealthUpdate(BaseModel):
    is_active: Optional[bool] = None
    last_verified_at: Optional[datetime] = None


# ── Evidence Packs ─────────────────────────────────────────────

class EvidencePackCreate(BaseModel):
    title: str = Field(..., max_length=500)
    title_ar: Optional[str] = Field(None, max_length=500)
    pack_type: str = Field(..., max_length=80)
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    assumptions: Optional[List[Dict[str, Any]]] = None
    financial_model_version: Optional[str] = None
    policy_notes: Optional[str] = None
    alternatives: Optional[List[Dict[str, Any]]] = None
    rollback_plan: Optional[str] = None
    approval_class: Optional[str] = None
    reversibility_class: Optional[str] = None
    sensitivity: str = "internal"

class EvidencePackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tenant_id: UUID
    title: str
    title_ar: Optional[str] = None
    pack_type: str
    status: str
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    sources: List[Dict[str, Any]] = []
    assumptions: Optional[List[Dict[str, Any]]] = None
    financial_model_version: Optional[str] = None
    policy_notes: Optional[str] = None
    alternatives: Optional[List[Dict[str, Any]]] = None
    rollback_plan: Optional[str] = None
    approval_class: Optional[str] = None
    reversibility_class: Optional[str] = None
    sensitivity: str
    assembled_by_id: Optional[UUID] = None
    approved_by_id: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class EvidencePackUpdate(BaseModel):
    status: Optional[str] = None
    policy_notes: Optional[str] = None


# ── Sovereign Dashboard Summary ────────────────────────────────

class SovereignDashboardSummary(BaseModel):
    """Summary for the Executive Room."""
    total_recommendations: int = 0
    pending_approvals: int = 0
    active_workflows: int = 0
    active_partners: int = 0
    ma_pipeline_count: int = 0
    expansion_markets: int = 0
    pmi_programs: int = 0
    policy_violations: int = 0
    contradiction_alerts: int = 0
    connector_health: Dict[str, int] = Field(default_factory=lambda: {"ok": 0, "degraded": 0, "error": 0})
    compliance_summary: Dict[str, int] = Field(default_factory=dict)
    evidence_packs_pending: int = 0
