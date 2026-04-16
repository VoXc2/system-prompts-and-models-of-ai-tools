"""Dealix Sovereign Growth, Execution & Governance OS — core models.

Five planes:
  Decision  — structured outputs, tool traces, guardrail events
  Execution — durable workflow runs, checkpoints, HITL interrupts
  Trust     — policies, approvals with reversibility/sensitivity classes, audit entries
  Data      — cloud events, quality checks, connector health v2
  Operating — release gates, environment protection rules, provenance
"""

from __future__ import annotations

from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey, Integer,
    Numeric, String, Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import TenantModel


# ---------------------------------------------------------------------------
# Shared enumerations
# ---------------------------------------------------------------------------

class ApprovalClass(str, PyEnum):
    """A — auto-allowed | B — requires approval | C — forbidden."""
    A = "A"
    B = "B"
    C = "C"


class ReversibilityClass(str, PyEnum):
    reversible = "reversible"
    partially_reversible = "partially_reversible"
    irreversible = "irreversible"


class SensitivityClass(str, PyEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


# ---------------------------------------------------------------------------
# DECISION PLANE
# ---------------------------------------------------------------------------

class DecisionTrace(TenantModel):
    """Structured record of every AI decision emitted via Responses API."""
    __tablename__ = "decision_traces"

    trace_id = Column(String(128), nullable=False, unique=True, index=True)
    agent_id = Column(String(120), nullable=True, index=True)
    model_used = Column(String(80), nullable=False)
    input_summary = Column(Text, nullable=True)
    structured_output = Column(JSONB, default=dict)
    tool_calls = Column(JSONB, default=list)
    guardrail_events = Column(JSONB, default=list)
    latency_ms = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    cost_usd = Column(Numeric(12, 6), nullable=True)
    schema_adhered = Column(Boolean, nullable=True)
    contradiction_detected = Column(Boolean, default=False)
    arabic_quality_score = Column(Numeric(5, 2), nullable=True)
    os_module = Column(String(80), nullable=True, index=True)  # sales, partnership, ma, expansion, pmi, executive
    correlation_id = Column(String(128), nullable=True, index=True)


class ModelBenchmarkRun(TenantModel):
    """Benchmark harness result for a single model/task combination."""
    __tablename__ = "model_benchmark_runs"

    model_name = Column(String(80), nullable=False, index=True)
    task_type = Column(String(80), nullable=False)  # classification, memo, proposal, routing, ...
    language = Column(String(10), default="ar")
    latency_ms = Column(Integer, nullable=True)
    success = Column(Boolean, nullable=False)
    schema_adherence = Column(Boolean, nullable=True)
    tool_call_reliability = Column(Numeric(5, 2), nullable=True)
    contradiction_rate = Column(Numeric(5, 2), nullable=True)
    arabic_quality_score = Column(Numeric(5, 2), nullable=True)
    cost_usd = Column(Numeric(12, 6), nullable=True)
    benchmark_payload = Column(JSONB, default=dict)
    result_payload = Column(JSONB, default=dict)


# ---------------------------------------------------------------------------
# EXECUTION PLANE
# ---------------------------------------------------------------------------

class WorkflowStatus(str, PyEnum):
    pending = "pending"
    running = "running"
    waiting_hitl = "waiting_hitl"
    approved = "approved"
    rejected = "rejected"
    completed = "completed"
    failed = "failed"
    timed_out = "timed_out"


class DurableWorkflowRun(TenantModel):
    """Long-lived workflow run (days/weeks) that survives restarts."""
    __tablename__ = "durable_workflow_runs"

    workflow_type = Column(String(80), nullable=False, index=True)
    os_module = Column(String(40), nullable=False, index=True)
    status = Column(Enum(WorkflowStatus), nullable=False, default=WorkflowStatus.pending)
    current_step = Column(String(120), nullable=True)
    state_snapshot = Column(JSONB, default=dict)
    started_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    deadline_at = Column(DateTime(timezone=True), nullable=True)
    correlation_id = Column(String(128), nullable=True, index=True)
    external_ref = Column(String(255), nullable=True)

    started_by = relationship("User", foreign_keys=[started_by_id])
    checkpoints = relationship("WorkflowCheckpoint", back_populates="run", cascade="all, delete-orphan")
    hitl_interrupts = relationship("HITLInterrupt", back_populates="run", cascade="all, delete-orphan")


class WorkflowCheckpoint(TenantModel):
    """Immutable checkpoint saved at each step boundary."""
    __tablename__ = "workflow_checkpoints"

    run_id = Column(UUID(as_uuid=True), ForeignKey("durable_workflow_runs.id"), nullable=False, index=True)
    step_name = Column(String(120), nullable=False)
    state_at_checkpoint = Column(JSONB, default=dict)
    sequence_number = Column(Integer, nullable=False, default=0)

    run = relationship("DurableWorkflowRun", back_populates="checkpoints")


class HITLInterrupt(TenantModel):
    """Human-in-the-loop interrupt before an irreversible/sensitive action."""
    __tablename__ = "hitl_interrupts"

    run_id = Column(UUID(as_uuid=True), ForeignKey("durable_workflow_runs.id"), nullable=False, index=True)
    step_name = Column(String(120), nullable=False)
    action_description = Column(Text, nullable=False)
    action_description_ar = Column(Text, nullable=True)
    approval_class = Column(Enum(ApprovalClass), nullable=False, default=ApprovalClass.B)
    reversibility = Column(Enum(ReversibilityClass), nullable=False, default=ReversibilityClass.irreversible)
    sensitivity = Column(Enum(SensitivityClass), nullable=False, default=SensitivityClass.high)
    financial_impact_sar = Column(Numeric(18, 2), nullable=True)
    alternatives = Column(JSONB, default=list)
    risks = Column(JSONB, default=list)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolution = Column(String(20), nullable=True)  # approved, rejected
    resolution_note = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    run = relationship("DurableWorkflowRun", back_populates="hitl_interrupts")
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])


# ---------------------------------------------------------------------------
# TRUST PLANE
# ---------------------------------------------------------------------------

class PolicyRule(TenantModel):
    """OPA-style policy rule stored as JSON + Rego snippet."""
    __tablename__ = "policy_rules"

    rule_id = Column(String(120), nullable=False, unique=True, index=True)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=True)
    category = Column(String(80), nullable=False, index=True)  # discount, data_sharing, commitment, ...
    rego_snippet = Column(Text, nullable=True)
    json_condition = Column(JSONB, default=dict)
    approval_class = Column(Enum(ApprovalClass), nullable=False, default=ApprovalClass.B)
    reversibility = Column(Enum(ReversibilityClass), nullable=False, default=ReversibilityClass.irreversible)
    sensitivity = Column(Enum(SensitivityClass), nullable=False, default=SensitivityClass.high)
    is_active = Column(Boolean, default=True)
    pdpl_relevant = Column(Boolean, default=False)
    nca_relevant = Column(Boolean, default=False)


class GovernedApproval(TenantModel):
    """Enterprise-grade approval with full metadata, alternatives, and traceability."""
    __tablename__ = "governed_approvals"

    title_ar = Column(String(512), nullable=False)
    title_en = Column(String(512), nullable=True)
    description_ar = Column(Text, nullable=True)
    resource_type = Column(String(80), nullable=False, index=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    os_module = Column(String(40), nullable=False, index=True)
    approval_class = Column(Enum(ApprovalClass), nullable=False, default=ApprovalClass.B)
    reversibility = Column(Enum(ReversibilityClass), nullable=False, default=ReversibilityClass.irreversible)
    sensitivity = Column(Enum(SensitivityClass), nullable=False, default=SensitivityClass.high)
    financial_impact_sar = Column(Numeric(18, 2), nullable=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    policy_rule_id = Column(String(120), nullable=True)
    evidence = Column(JSONB, default=dict)
    alternatives = Column(JSONB, default=list)
    risks = Column(JSONB, default=list)
    requested_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_note = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("durable_workflow_runs.id"), nullable=True)
    correlation_id = Column(String(128), nullable=True, index=True)

    requested_by = relationship("User", foreign_keys=[requested_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
    workflow_run = relationship("DurableWorkflowRun")


class ToolVerificationEntry(TenantModel):
    """Tool Verification Ledger — immutable log of every tool call executed by an agent."""
    __tablename__ = "tool_verification_ledger"

    tool_name = Column(String(120), nullable=False, index=True)
    agent_id = Column(String(120), nullable=True)
    os_module = Column(String(40), nullable=True)
    input_hash = Column(String(128), nullable=True)
    output_hash = Column(String(128), nullable=True)
    success = Column(Boolean, nullable=False)
    error_code = Column(String(80), nullable=True)
    latency_ms = Column(Integer, nullable=True)
    trace_id = Column(String(128), nullable=True, index=True)
    approval_required = Column(Boolean, default=False)
    approval_id = Column(UUID(as_uuid=True), nullable=True)
    idempotency_key = Column(String(128), nullable=True, unique=True)


class EvidencePack(TenantModel):
    """Evidence pack assembled for a decision or approval."""
    __tablename__ = "evidence_packs"

    title_ar = Column(String(512), nullable=False)
    title_en = Column(String(512), nullable=True)
    os_module = Column(String(40), nullable=False, index=True)
    resource_type = Column(String(80), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    evidence_items = Column(JSONB, default=list)
    summary_ar = Column(Text, nullable=True)
    summary_en = Column(Text, nullable=True)
    financial_summary = Column(JSONB, default=dict)
    risk_summary = Column(JSONB, default=list)
    recommendation_ar = Column(Text, nullable=True)
    assembled_by_agent = Column(String(120), nullable=True)
    trace_id = Column(String(128), nullable=True)
    correlation_id = Column(String(128), nullable=True, index=True)


# ---------------------------------------------------------------------------
# DATA PLANE
# ---------------------------------------------------------------------------

class CloudEventLog(TenantModel):
    """CloudEvents-spec log entry for every domain event crossing system boundaries."""
    __tablename__ = "cloud_event_logs"

    spec_version = Column(String(10), default="1.0")
    event_type = Column(String(200), nullable=False, index=True)
    source = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=True)
    data_schema = Column(String(512), nullable=True)
    data_content_type = Column(String(80), default="application/json")
    data = Column(JSONB, default=dict)
    correlation_id = Column(String(128), nullable=True, index=True)
    trace_id = Column(String(128), nullable=True, index=True)
    processed = Column(Boolean, default=False, index=True)
    os_module = Column(String(40), nullable=True, index=True)


class DataQualityCheckpoint(TenantModel):
    """Great Expectations-style data quality result."""
    __tablename__ = "data_quality_checkpoints"

    checkpoint_name = Column(String(120), nullable=False)
    dataset_name = Column(String(120), nullable=False, index=True)
    os_module = Column(String(40), nullable=True, index=True)
    passed = Column(Boolean, nullable=False)
    total_expectations = Column(Integer, default=0)
    passed_expectations = Column(Integer, default=0)
    failed_expectations = Column(Integer, default=0)
    failure_details = Column(JSONB, default=list)
    run_id = Column(String(128), nullable=True)


class ConnectorHealthEntry(TenantModel):
    """Connector Health Board — granular health record per connector per tenant."""
    __tablename__ = "connector_health_entries"

    connector_key = Column(String(80), nullable=False, index=True)
    display_name_ar = Column(String(255), nullable=True)
    version = Column(String(20), nullable=True)
    status = Column(String(20), nullable=False, default="unknown")
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    last_error_at = Column(DateTime(timezone=True), nullable=True)
    last_error_code = Column(String(80), nullable=True)
    retry_count = Column(Integer, default=0)
    idempotency_supported = Column(Boolean, default=False)
    audit_mapped = Column(Boolean, default=False)
    schema_version = Column(String(20), nullable=True)


# ---------------------------------------------------------------------------
# OPERATING PLANE
# ---------------------------------------------------------------------------

class ReleaseGate(TenantModel):
    """Release Gate record — tracks status checks, OIDC, and provenance per release."""
    __tablename__ = "release_gates"

    release_tag = Column(String(120), nullable=False, index=True)
    environment = Column(String(40), nullable=False, index=True)  # staging, prod
    status = Column(String(20), nullable=False, default="pending")  # pending, passed, failed, blocked
    required_checks = Column(JSONB, default=list)
    passed_checks = Column(JSONB, default=list)
    failed_checks = Column(JSONB, default=list)
    oidc_verified = Column(Boolean, default=False)
    artifact_attestation_id = Column(String(255), nullable=True)
    provenance_url = Column(String(512), nullable=True)
    deployed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    rollback_plan_ar = Column(Text, nullable=True)
    canary_percentage = Column(Integer, default=0)
    audit_stream_url = Column(String(512), nullable=True)

    deployed_by = relationship("User", foreign_keys=[deployed_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])


# ---------------------------------------------------------------------------
# OS MODULE MODELS
# ---------------------------------------------------------------------------

class SalesOpportunity(TenantModel):
    """Sales & Revenue OS — full-cycle opportunity from capture to renewal."""
    __tablename__ = "sales_opportunities"

    title_ar = Column(String(512), nullable=False)
    title_en = Column(String(512), nullable=True)
    stage = Column(String(40), nullable=False, default="capture", index=True)
    # stages: capture, enrichment, scoring, qualified, outreach, meeting,
    #         proposal, approval, signature, onboarding, renewal
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True, index=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company_profiles.id"), nullable=True, index=True)
    value_sar = Column(Numeric(18, 2), nullable=True)
    score = Column(Integer, nullable=True)
    channel = Column(String(40), nullable=True)  # whatsapp, email, referral, form, import
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey("proposals.id"), nullable=True)
    approval_id = Column(UUID(as_uuid=True), nullable=True)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("durable_workflow_runs.id"), nullable=True)
    margin_check_passed = Column(Boolean, nullable=True)
    discount_approved = Column(Boolean, nullable=True)
    esignature_sent_at = Column(DateTime(timezone=True), nullable=True)
    esignature_completed_at = Column(DateTime(timezone=True), nullable=True)
    onboarding_triggered_at = Column(DateTime(timezone=True), nullable=True)
    renewal_due_at = Column(DateTime(timezone=True), nullable=True)
    extra_data = Column(JSONB, default=dict)

    assigned_to = relationship("User", foreign_keys=[assigned_to_id])


class PartnerRecord(TenantModel):
    """Partnership OS — full partnership lifecycle."""
    __tablename__ = "partner_records"

    partner_name_ar = Column(String(255), nullable=False)
    partner_name_en = Column(String(255), nullable=True)
    stage = Column(String(40), nullable=False, default="scouting", index=True)
    # stages: scouting, fit_scoring, economics, structure_design, term_sheet,
    #         approval, signature, activation, scorecard, expansion
    strategic_fit_score = Column(Integer, nullable=True)
    channel_type = Column(String(80), nullable=True)  # reseller, referral, technology, strategic
    rev_share_pct = Column(Numeric(5, 2), nullable=True)
    exclusivity = Column(Boolean, default=False)
    market_commitment = Column(String(255), nullable=True)
    term_sheet_url = Column(String(512), nullable=True)
    term_sheet_approved_at = Column(DateTime(timezone=True), nullable=True)
    signature_completed_at = Column(DateTime(timezone=True), nullable=True)
    activation_at = Column(DateTime(timezone=True), nullable=True)
    health_score = Column(Integer, nullable=True)
    contribution_margin_sar = Column(Numeric(18, 2), nullable=True)
    renewal_due_at = Column(DateTime(timezone=True), nullable=True)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("durable_workflow_runs.id"), nullable=True)
    approval_id = Column(UUID(as_uuid=True), nullable=True)
    extra_data = Column(JSONB, default=dict)


class MATarget(TenantModel):
    """M&A / Corporate Development OS — full target lifecycle."""
    __tablename__ = "ma_targets"

    target_name_ar = Column(String(255), nullable=False)
    target_name_en = Column(String(255), nullable=True)
    stage = Column(String(60), nullable=False, default="sourcing", index=True)
    # stages: sourcing, screening, ownership_mapping, dd_orchestration, dd_room,
    #         valuation, synergy_model, ic_pack, board_pack, offer_strategy,
    #         negotiation, signing, close, pmi_trigger
    strategic_fit_score = Column(Integer, nullable=True)
    ownership_structure = Column(JSONB, default=dict)
    dd_status = Column(JSONB, default=dict)
    valuation_range_sar = Column(JSONB, default=dict)  # {low, mid, high}
    synergy_model = Column(JSONB, default=dict)
    offer_sent_at = Column(DateTime(timezone=True), nullable=True)
    offer_amount_sar = Column(Numeric(18, 2), nullable=True)
    signing_at = Column(DateTime(timezone=True), nullable=True)
    close_at = Column(DateTime(timezone=True), nullable=True)
    pmi_triggered_at = Column(DateTime(timezone=True), nullable=True)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("durable_workflow_runs.id"), nullable=True)
    approval_id = Column(UUID(as_uuid=True), nullable=True)
    evidence_pack_id = Column(UUID(as_uuid=True), ForeignKey("evidence_packs.id"), nullable=True)
    extra_data = Column(JSONB, default=dict)

    evidence_pack = relationship("EvidencePack")


class ExpansionPlan(TenantModel):
    """Expansion OS — market expansion lifecycle."""
    __tablename__ = "expansion_plans"

    market_ar = Column(String(255), nullable=False)
    market_en = Column(String(255), nullable=True)
    segment = Column(String(120), nullable=True)
    stage = Column(String(60), nullable=False, default="scanning", index=True)
    # stages: scanning, prioritization, regulatory_assessment, pricing_strategy,
    #         localized_gtm, launch_readiness, canary_launch, stop_loss,
    #         partner_entry, post_launch
    readiness_score = Column(Integer, nullable=True)
    canary_pct = Column(Integer, default=0)
    stop_loss_triggered = Column(Boolean, default=False)
    stop_loss_reason = Column(Text, nullable=True)
    launch_at = Column(DateTime(timezone=True), nullable=True)
    post_launch_review_at = Column(DateTime(timezone=True), nullable=True)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("durable_workflow_runs.id"), nullable=True)
    approval_id = Column(UUID(as_uuid=True), nullable=True)
    gtm_doc = Column(JSONB, default=dict)
    extra_data = Column(JSONB, default=dict)


class PMIProject(TenantModel):
    """PMI / Strategic PMO OS — post-merger integration or strategic program."""
    __tablename__ = "pmi_projects"

    name_ar = Column(String(512), nullable=False)
    name_en = Column(String(512), nullable=True)
    ma_target_id = Column(UUID(as_uuid=True), ForeignKey("ma_targets.id"), nullable=True, index=True)
    program_type = Column(String(40), nullable=False, default="pmi")  # pmi, expansion_pmo, partnership_pmo
    status = Column(String(20), nullable=False, default="planning", index=True)
    day1_readiness = Column(JSONB, default=dict)
    plan_30d = Column(JSONB, default=dict)
    plan_60d = Column(JSONB, default=dict)
    plan_90d = Column(JSONB, default=dict)
    synergy_realized_pct = Column(Numeric(5, 2), nullable=True)
    risk_register = Column(JSONB, default=list)
    issue_count_open = Column(Integer, default=0)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("durable_workflow_runs.id"), nullable=True)
    extra_data = Column(JSONB, default=dict)

    ma_target = relationship("MATarget")


class ExecutiveKPI(TenantModel):
    """Executive / Board OS — live KPI snapshot per period."""
    __tablename__ = "executive_kpis"

    period_label = Column(String(40), nullable=False)  # e.g. "2026-Q2"
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    revenue_actual_sar = Column(Numeric(18, 2), nullable=True)
    revenue_forecast_sar = Column(Numeric(18, 2), nullable=True)
    pipeline_value_sar = Column(Numeric(18, 2), nullable=True)
    partner_pipeline_sar = Column(Numeric(18, 2), nullable=True)
    ma_pipeline_value_sar = Column(Numeric(18, 2), nullable=True)
    open_approvals = Column(Integer, default=0)
    policy_violations = Column(Integer, default=0)
    risk_heatmap = Column(JSONB, default=dict)
    next_best_actions = Column(JSONB, default=list)
    escalations = Column(JSONB, default=list)
    generated_by_agent = Column(String(120), nullable=True)
    trace_id = Column(String(128), nullable=True)


class SaudiComplianceCheck(TenantModel):
    """Saudi compliance check record — PDPL + NCA ECC mapping."""
    __tablename__ = "saudi_compliance_checks"

    check_type = Column(String(40), nullable=False, index=True)  # pdpl, nca_ecc, both
    resource_type = Column(String(80), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    os_module = Column(String(40), nullable=True)
    passed = Column(Boolean, nullable=False)
    control_ids = Column(JSONB, default=list)
    violations = Column(JSONB, default=list)
    remediation_steps = Column(JSONB, default=list)
    remediation_steps_ar = Column(JSONB, default=list)
    reviewed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    auto_remediated = Column(Boolean, default=False)

    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
