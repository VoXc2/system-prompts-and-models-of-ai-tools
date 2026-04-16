"""
Dealix Sovereign Enterprise Growth OS — Core Models
Covers: Decision Plane, Execution Plane, Trust Plane, Data Plane, Operating Plane
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer,
    Numeric, String, Text,
)
from sqlalchemy.orm import relationship

from app.models.base import TenantModel
from app.models.compat import UUID, JSONB, default_uuid


# ─────────────────────────────────────────────────────────────────
# DECISION PLANE — structured, evidence-backed recommendations
# ─────────────────────────────────────────────────────────────────

class EvidencePack(TenantModel):
    """Every major recommendation ships with a structured evidence pack."""
    __tablename__ = "evidence_packs"

    # What decision this pack supports
    decision_type = Column(String(80), nullable=False, index=True)
    # e.g. deal_close, market_launch, m_and_a_offer, partner_activation
    decision_ref_type = Column(String(80), nullable=True)
    decision_ref_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Structured evidence fields
    title_ar = Column(String(512), nullable=False)
    title_en = Column(String(512), nullable=True)
    summary_ar = Column(Text, nullable=True)
    sources = Column(JSONB, default=list)          # [{url, title, freshness_ts}]
    assumptions = Column(JSONB, default=list)      # [str]
    alternatives = Column(JSONB, default=list)     # [{option, pros, cons}]
    financial_model_version = Column(String(40), nullable=True)
    freshness_at = Column(DateTime(timezone=True), nullable=True)
    confidence_score = Column(Numeric(5, 2), nullable=True)   # 0-100

    # Governance metadata
    policy_notes = Column(JSONB, default=list)
    approval_class = Column(String(20), nullable=False, default="B")   # A, B, C
    reversibility_class = Column(String(20), nullable=False, default="partial")
    # full, partial, none
    sensitivity_level = Column(String(20), nullable=False, default="medium")
    # low, medium, high, critical
    rollback_notes = Column(Text, nullable=True)

    # Status
    status = Column(String(20), nullable=False, default="draft")
    # draft, pending_review, approved, rejected, archived
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    approved_by = relationship("User", foreign_keys=[approved_by_id])
    created_by = relationship("User", foreign_keys=[created_by_id])


class SovereignDecision(TenantModel):
    """Audit record of every structured AI recommendation made on this platform."""
    __tablename__ = "sovereign_decisions"

    decision_type = Column(String(80), nullable=False, index=True)
    lane = Column(String(40), nullable=False, default="executive_reasoning")
    # coding, executive_reasoning, throughput_drafting, fallback

    model_used = Column(String(80), nullable=True)
    prompt_version = Column(String(40), nullable=True)
    latency_ms = Column(Integer, nullable=True)
    schema_valid = Column(Boolean, nullable=False, default=True)
    contradiction_detected = Column(Boolean, nullable=False, default=False)
    cost_sar = Column(Numeric(10, 4), nullable=True)

    recommendation_ar = Column(Text, nullable=True)
    recommendation_en = Column(Text, nullable=True)
    structured_output = Column(JSONB, default=dict)
    next_best_action = Column(JSONB, default=dict)

    evidence_pack_id = Column(UUID(as_uuid=True), ForeignKey("evidence_packs.id"), nullable=True)
    evidence_pack = relationship("EvidencePack")

    # HITL result
    hitl_required = Column(Boolean, nullable=False, default=False)
    hitl_status = Column(String(20), nullable=True)   # pending, approved, rejected
    hitl_reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    hitl_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    hitl_note = Column(Text, nullable=True)


# ─────────────────────────────────────────────────────────────────
# PARTNERSHIP OS
# ─────────────────────────────────────────────────────────────────

class Partner(TenantModel):
    __tablename__ = "partners"

    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=True)
    partner_type = Column(String(60), nullable=False, default="channel")
    # channel, technology, strategic, reseller, referral

    status = Column(String(30), nullable=False, default="scouted")
    # scouted, scoring, negotiation, active, paused, terminated

    strategic_fit_score = Column(Numeric(5, 2), nullable=True)
    channel_economics = Column(JSONB, default=dict)
    # {revenue_share_pct, min_volume_sar, commission_model}

    alliance_structure = Column(JSONB, default=dict)
    term_sheet_draft = Column(Text, nullable=True)
    term_sheet_approved_at = Column(DateTime(timezone=True), nullable=True)

    # Scorecard
    quarterly_revenue_sar = Column(Numeric(18, 2), nullable=True)
    contribution_margin_pct = Column(Numeric(5, 2), nullable=True)
    active_deals_count = Column(Integer, nullable=False, default=0)
    nps_score = Column(Numeric(5, 2), nullable=True)

    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)

    activated_at = Column(DateTime(timezone=True), nullable=True)
    evidence_pack_id = Column(UUID(as_uuid=True), ForeignKey("evidence_packs.id"), nullable=True)
    evidence_pack = relationship("EvidencePack")


class PartnerScorecard(TenantModel):
    __tablename__ = "partner_scorecards"

    partner_id = Column(UUID(as_uuid=True), ForeignKey("partners.id"), nullable=False, index=True)
    period_label = Column(String(20), nullable=False)   # e.g. 2026-Q2
    revenue_sar = Column(Numeric(18, 2), nullable=True)
    deals_closed = Column(Integer, nullable=False, default=0)
    contribution_margin_pct = Column(Numeric(5, 2), nullable=True)
    nps_score = Column(Numeric(5, 2), nullable=True)
    notes_ar = Column(Text, nullable=True)

    partner = relationship("Partner")


# ─────────────────────────────────────────────────────────────────
# M&A / CORP DEV OS
# ─────────────────────────────────────────────────────────────────

class MATarget(TenantModel):
    __tablename__ = "ma_targets"

    company_name_ar = Column(String(255), nullable=False)
    company_name_en = Column(String(255), nullable=True)
    sector = Column(String(80), nullable=True)
    geography = Column(String(80), nullable=True, default="Saudi Arabia")

    status = Column(String(40), nullable=False, default="sourced")
    # sourced, screening, dd_active, ic_memo, offer, signed, closed, passed

    strategic_rationale_ar = Column(Text, nullable=True)
    synergy_model = Column(JSONB, default=dict)
    # {revenue_synergy_sar, cost_synergy_sar, timeline_months}

    valuation_low_sar = Column(Numeric(18, 2), nullable=True)
    valuation_high_sar = Column(Numeric(18, 2), nullable=True)
    offer_price_sar = Column(Numeric(18, 2), nullable=True)

    dd_room_url = Column(String(512), nullable=True)
    dd_access_policy = Column(JSONB, default=dict)
    # OpenFGA-style relation tuples for DD room access

    ic_memo_id = Column(UUID(as_uuid=True), ForeignKey("evidence_packs.id"), nullable=True)
    ic_memo = relationship("EvidencePack")

    signed_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    lead_advisor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    lead_advisor = relationship("User")


class DDChecklist(TenantModel):
    __tablename__ = "dd_checklists"

    ma_target_id = Column(UUID(as_uuid=True), ForeignKey("ma_targets.id"), nullable=False, index=True)
    category = Column(String(80), nullable=False)  # financial, legal, tech, hr, ops, regulatory
    item_ar = Column(String(512), nullable=False)
    item_en = Column(String(512), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    # pending, in_progress, complete, flagged
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    notes_ar = Column(Text, nullable=True)
    risk_level = Column(String(20), nullable=False, default="medium")

    ma_target = relationship("MATarget")
    owner = relationship("User")


# ─────────────────────────────────────────────────────────────────
# EXPANSION OS
# ─────────────────────────────────────────────────────────────────

class ExpansionMarket(TenantModel):
    __tablename__ = "expansion_markets"

    market_name_ar = Column(String(255), nullable=False)
    market_name_en = Column(String(255), nullable=True)
    country_code = Column(String(10), nullable=False)
    region = Column(String(80), nullable=True)

    status = Column(String(40), nullable=False, default="scanning")
    # scanning, prioritized, compliance_check, planning, launching, live, stopped

    priority_score = Column(Numeric(5, 2), nullable=True)
    tam_sar = Column(Numeric(18, 2), nullable=True)
    compliance_readiness = Column(JSONB, default=dict)
    localization_requirements = Column(JSONB, default=list)
    pricing_plan = Column(JSONB, default=dict)
    channel_plan = Column(JSONB, default=dict)
    launch_readiness_score = Column(Numeric(5, 2), nullable=True)
    stop_loss_threshold = Column(JSONB, default=dict)

    launched_at = Column(DateTime(timezone=True), nullable=True)
    evidence_pack_id = Column(UUID(as_uuid=True), ForeignKey("evidence_packs.id"), nullable=True)
    evidence_pack = relationship("EvidencePack")


class ExpansionActual(TenantModel):
    """Actual vs forecast tracking for each launched market."""
    __tablename__ = "expansion_actuals"

    market_id = Column(UUID(as_uuid=True), ForeignKey("expansion_markets.id"), nullable=False, index=True)
    period_label = Column(String(20), nullable=False)
    revenue_forecast_sar = Column(Numeric(18, 2), nullable=True)
    revenue_actual_sar = Column(Numeric(18, 2), nullable=True)
    leads_forecast = Column(Integer, nullable=True)
    leads_actual = Column(Integer, nullable=True)
    variance_pct = Column(Numeric(7, 2), nullable=True)
    notes_ar = Column(Text, nullable=True)

    market = relationship("ExpansionMarket")


# ─────────────────────────────────────────────────────────────────
# PMI / PMO OS
# ─────────────────────────────────────────────────────────────────

class PMIProgram(TenantModel):
    __tablename__ = "pmi_programs"

    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=True)
    ma_target_id = Column(UUID(as_uuid=True), ForeignKey("ma_targets.id"), nullable=True, index=True)
    status = Column(String(30), nullable=False, default="day1_readiness")
    # day1_readiness, day30, day60, day90, complete

    day1_checklist = Column(JSONB, default=list)
    plan_30 = Column(JSONB, default=list)
    plan_60 = Column(JSONB, default=list)
    plan_90 = Column(JSONB, default=list)
    synergy_realized_sar = Column(Numeric(18, 2), nullable=True)
    synergy_target_sar = Column(Numeric(18, 2), nullable=True)

    risk_register = Column(JSONB, default=list)
    # [{risk, owner_id, likelihood, impact, mitigation}]

    ma_target = relationship("MATarget")


class PMITask(TenantModel):
    __tablename__ = "pmi_tasks"

    program_id = Column(UUID(as_uuid=True), ForeignKey("pmi_programs.id"), nullable=False, index=True)
    phase = Column(String(20), nullable=False)  # day1, day30, day60, day90
    title_ar = Column(String(512), nullable=False)
    title_en = Column(String(512), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    due_date = Column(DateTime(timezone=True), nullable=True)
    dependency_ids = Column(JSONB, default=list)
    escalated = Column(Boolean, nullable=False, default=False)

    program = relationship("PMIProgram")
    owner = relationship("User")


# ─────────────────────────────────────────────────────────────────
# TRUST PLANE
# ─────────────────────────────────────────────────────────────────

class PolicyViolation(TenantModel):
    __tablename__ = "policy_violations"

    violation_type = Column(String(80), nullable=False, index=True)
    # discount_out_of_policy, unauthorized_access, missing_consent, tool_unverified, etc.

    severity = Column(String(20), nullable=False, default="medium")  # low, medium, high, critical
    resource_type = Column(String(80), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    triggered_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    policy_ref = Column(String(255), nullable=True)  # e.g. "PDPL.Art.5", "ECC.2-2024.Ctrl.7"
    description_ar = Column(Text, nullable=False)
    description_en = Column(Text, nullable=True)
    remediation_ar = Column(Text, nullable=True)
    resolved = Column(Boolean, nullable=False, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    triggered_by = relationship("User", foreign_keys=[triggered_by_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])


class ToolVerificationLedger(TenantModel):
    """Immutable log of every tool/connector call made by an AI agent."""
    __tablename__ = "tool_verification_ledger"

    agent_role = Column(String(80), nullable=False)
    tool_name = Column(String(120), nullable=False, index=True)
    intended_action = Column(Text, nullable=True)
    claimed_action = Column(Text, nullable=True)
    actual_tool_call = Column(JSONB, default=dict)
    side_effects = Column(JSONB, default=list)
    contradiction_status = Column(String(20), nullable=False, default="none")
    # none, suspected, confirmed
    correlation_id = Column(String(80), nullable=True, index=True)
    trace_id = Column(String(80), nullable=True, index=True)
    span_id = Column(String(80), nullable=True)
    outcome = Column(String(20), nullable=False, default="success")
    # success, failed, rolled_back
    latency_ms = Column(Integer, nullable=True)


class ContradictionRecord(TenantModel):
    """Captures detected contradictions between intended and actual agent behavior."""
    __tablename__ = "contradiction_records"

    agent_role = Column(String(80), nullable=False, index=True)
    tool_ledger_id = Column(UUID(as_uuid=True), ForeignKey("tool_verification_ledger.id"), nullable=True)
    intended_action_summary = Column(Text, nullable=False)
    actual_action_summary = Column(Text, nullable=False)
    contradiction_type = Column(String(60), nullable=False)
    # claim_mismatch, side_effect_unexpected, schema_violation, policy_breach
    severity = Column(String(20), nullable=False, default="medium")
    status = Column(String(20), nullable=False, default="open")
    # open, investigating, resolved, false_positive
    resolution_notes = Column(Text, nullable=True)
    correlation_id = Column(String(80), nullable=True, index=True)

    tool_ledger = relationship("ToolVerificationLedger")


# ─────────────────────────────────────────────────────────────────
# CONNECTOR GOVERNANCE PLANE
# ─────────────────────────────────────────────────────────────────

class ConnectorRegistry(TenantModel):
    """Versioned registry of all external integrations with governance metadata."""
    __tablename__ = "connector_registry"

    connector_key = Column(String(80), nullable=False, index=True)
    display_name_ar = Column(String(255), nullable=False)
    display_name_en = Column(String(255), nullable=True)
    vendor = Column(String(80), nullable=True)
    api_version = Column(String(40), nullable=False)
    contract_schema = Column(JSONB, default=dict)    # JSON Schema for input/output
    retry_policy = Column(JSONB, default=dict)
    # {max_retries, backoff_multiplier_ms, max_backoff_ms}
    timeout_ms = Column(Integer, nullable=False, default=30000)
    idempotency_key_strategy = Column(String(80), nullable=False, default="request_id")
    approval_policy = Column(String(20), nullable=False, default="A")  # A, B, C
    audit_mapping = Column(JSONB, default=dict)
    telemetry_mapping = Column(JSONB, default=dict)
    rollback_notes = Column(Text, nullable=True)
    compensation_strategy = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    deprecated_at = Column(DateTime(timezone=True), nullable=True)

    # Health state
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    health_status = Column(String(20), nullable=False, default="unknown")
    # ok, degraded, error, unknown
    last_error = Column(Text, nullable=True)


# ─────────────────────────────────────────────────────────────────
# SOVEREIGN MODEL ROUTING
# ─────────────────────────────────────────────────────────────────

class ModelRoutingConfig(TenantModel):
    """Policy-based routing config for the Sovereign Routing Fabric."""
    __tablename__ = "model_routing_configs"

    lane = Column(String(60), nullable=False, unique=False, index=True)
    # coding, executive_reasoning, throughput_drafting, arabic_nlp, fallback

    primary_model = Column(String(80), nullable=False)
    fallback_model = Column(String(80), nullable=True)
    provider = Column(String(40), nullable=False)    # groq, openai, anthropic, google, deepseek
    max_tokens = Column(Integer, nullable=True)
    temperature = Column(Numeric(3, 2), nullable=True)
    requires_structured_output = Column(Boolean, nullable=False, default=False)
    output_schema = Column(JSONB, default=dict)

    # Policy gates
    min_confidence_threshold = Column(Numeric(5, 2), nullable=True)
    arabic_quality_check = Column(Boolean, nullable=False, default=False)
    hitl_required = Column(Boolean, nullable=False, default=False)
    approval_class = Column(String(10), nullable=False, default="A")

    # Metrics (rolling)
    avg_latency_ms = Column(Integer, nullable=True)
    schema_adherence_pct = Column(Numeric(5, 2), nullable=True)
    contradiction_rate_pct = Column(Numeric(5, 2), nullable=True)
    arabic_quality_score = Column(Numeric(5, 2), nullable=True)
    cost_per_task_sar = Column(Numeric(10, 4), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)


# ─────────────────────────────────────────────────────────────────
# SAUDI COMPLIANCE MATRIX
# ─────────────────────────────────────────────────────────────────

class SaudiComplianceControl(TenantModel):
    """Maps every compliance requirement (PDPL, NCA ECC, NIST AI RMF, OWASP LLM) to platform controls."""
    __tablename__ = "saudi_compliance_controls"

    framework = Column(String(60), nullable=False, index=True)
    # PDPL, NCA_ECC_2024, NIST_AI_RMF, OWASP_LLM_TOP10
    control_ref = Column(String(80), nullable=False)
    # e.g. PDPL.Art.5, ECC.2-2024.Ctrl.7, NIST.GOVERN.1.1
    title_ar = Column(String(512), nullable=False)
    title_en = Column(String(512), nullable=True)
    description_ar = Column(Text, nullable=True)
    risk_category = Column(String(80), nullable=True)
    implementation_status = Column(String(30), nullable=False, default="planned")
    # planned, in_progress, implemented, verified, not_applicable
    platform_control_mapping = Column(JSONB, default=list)
    # [{"service": "pdpl.consent_manager", "notes": "..."}]
    evidence_ref = Column(JSONB, default=list)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    risk_level = Column(String(20), nullable=False, default="high")
    penalty_notes_ar = Column(Text, nullable=True)

    verified_by = relationship("User")


# ─────────────────────────────────────────────────────────────────
# EXECUTIVE / BOARD OS
# ─────────────────────────────────────────────────────────────────

class BoardPack(TenantModel):
    """Board-ready memo/pack generated by the Executive OS."""
    __tablename__ = "board_packs"

    title_ar = Column(String(512), nullable=False)
    title_en = Column(String(512), nullable=True)
    pack_type = Column(String(60), nullable=False)
    # board_memo, risk_heatmap, actual_vs_forecast, pipeline_review, approval_center

    period_label = Column(String(20), nullable=True)
    content_ar = Column(Text, nullable=True)
    structured_data = Column(JSONB, default=dict)
    # embedded KPIs, risks, recommendations

    status = Column(String(20), nullable=False, default="draft")
    # draft, review, approved, published

    approval_items = Column(JSONB, default=list)
    # [{item, approval_class, reversibility, status, approver_id}]

    policy_violations_count = Column(Integer, nullable=False, default=0)
    risk_heatmap = Column(JSONB, default=dict)

    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)

    created_by = relationship("User", foreign_keys=[created_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
