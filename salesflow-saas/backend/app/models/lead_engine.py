"""
Revenue Lead Engine — ICP, lawful sources, enrichment facts, intent signals,
stakeholder roles (no fabricated persons), scoring, routing, learning.

All tenant-scoped; integrates with existing Lead rows.
"""

from __future__ import annotations

from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, Index, Boolean, UniqueConstraint
from app.models.compat import JSONB, UUID
from app.models.base import TenantModel


class LeadEngineICPProfile(TenantModel):
    __tablename__ = "lead_engine_icp_profiles"
    __table_args__ = (UniqueConstraint("tenant_id", "slug", name="uq_le_icp_tenant_slug"),)

    slug = Column(String(80), nullable=False)
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=True)
    config_json = Column(JSONB, nullable=False, default=dict)
    is_active = Column(Boolean, nullable=False, default=True)


class LeadEngineSourceEvent(TenantModel):
    """Normalized ingestion audit trail (lawful sources only)."""

    __tablename__ = "lead_engine_source_events"
    __table_args__ = (Index("ix_le_src_lead", "tenant_id", "lead_id"),)

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=True, index=True)
    source_system = Column(String(80), nullable=False, index=True)
    acquisition_method = Column(String(120), nullable=False)
    confidence = Column(Integer, nullable=False, default=70)
    legal_basis = Column(String(80), nullable=True)
    dedup_key = Column(String(200), nullable=True, index=True)
    raw_payload = Column(JSONB, nullable=False, default=dict)
    status = Column(String(30), nullable=False, default="ingested", index=True)


class LeadEngineEnrichmentFact(TenantModel):
    __tablename__ = "lead_engine_enrichment_facts"
    __table_args__ = (Index("ix_le_enrich_lead", "tenant_id", "lead_id"),)

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    field_key = Column(String(120), nullable=False, index=True)
    value_json = Column(JSONB, nullable=False)
    source = Column(String(120), nullable=False)
    confidence = Column(Integer, nullable=False, default=60)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)


class LeadEngineSignal(TenantModel):
    """Intent, market, technographic, timing — explainable."""

    __tablename__ = "lead_engine_signals"
    __table_args__ = (Index("ix_le_sig_lead_cat", "tenant_id", "lead_id", "category"),)

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(40), nullable=False, index=True)
    sub_type = Column(String(80), nullable=True)
    score_contribution = Column(Float, nullable=False, default=0.0)
    explanation = Column(Text, nullable=True)
    evidence_json = Column(JSONB, nullable=False, default=dict)
    directness = Column(String(20), nullable=True)


class LeadEngineStakeholderRole(TenantModel):
    """Buying committee role template — no personal names (lawful B2B)."""

    __tablename__ = "lead_engine_stakeholder_roles"
    __table_args__ = (Index("ix_le_stk_lead", "tenant_id", "lead_id"),)

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    role_key = Column(String(60), nullable=False)
    seniority = Column(String(40), nullable=True)
    influence_0_100 = Column(Integer, nullable=False, default=50)
    confidence = Column(Integer, nullable=False, default=50)
    source = Column(String(80), nullable=False, default="icp_inferred")
    engagement_path_hint = Column(String(120), nullable=True)


class LeadEngineScoreSnapshot(TenantModel):
    __tablename__ = "lead_engine_score_snapshots"
    __table_args__ = (Index("ix_le_score_lead_created", "tenant_id", "lead_id", "created_at"),)

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    total_score = Column(Integer, nullable=False)
    priority_band = Column(String(8), nullable=False, index=True)
    dimension_scores = Column(JSONB, nullable=False, default=dict)
    reason_codes = Column(JSONB, nullable=False, default=list)


class LeadEngineRoutingDecision(TenantModel):
    __tablename__ = "lead_engine_routing_decisions"
    __table_args__ = (Index("ix_le_route_lead", "tenant_id", "lead_id"),)

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    motion = Column(String(40), nullable=False, index=True)
    playbook_key = Column(String(80), nullable=True, index=True)
    reason_codes = Column(JSONB, nullable=False, default=list)


class LeadEngineLearningEvent(TenantModel):
    """Outcomes for self-improvement (weights adjusted offline / future ML)."""

    __tablename__ = "lead_engine_learning_events"
    __table_args__ = (Index("ix_le_learn_tenant_type", "tenant_id", "event_type"),)

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(40), nullable=False, index=True)
    payload_json = Column(JSONB, nullable=False, default=dict)


class LeadEnginePlaybookRun(TenantModel):
    __tablename__ = "lead_engine_playbook_runs"

    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    playbook_key = Column(String(80), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="started", index=True)
    outcome_json = Column(JSONB, nullable=False, default=dict)
    completed_at = Column(DateTime(timezone=True), nullable=True)
