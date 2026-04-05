"""Persistent store for autonomous SEO intelligence (tenant-scoped)."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index, Boolean
from app.models.compat import JSONB, UUID
from app.models.base import TenantModel


class SeoEngineRun(TenantModel):
    __tablename__ = "seo_engine_runs"
    __table_args__ = (Index("ix_seo_run_tenant_created", "tenant_id", "created_at"),)

    run_kind = Column(String(40), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    input_json = Column(JSONB, nullable=False, default=dict)
    output_json = Column(JSONB, nullable=True)
    error_text = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class SeoCompetitor(TenantModel):
    __tablename__ = "seo_competitors"
    __table_args__ = (Index("ix_seo_comp_domain", "tenant_id", "domain"),)

    domain = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    last_snapshot_at = Column(DateTime(timezone=True), nullable=True)
    snapshot_json = Column(JSONB, nullable=True)


class SeoKeywordOpportunity(TenantModel):
    __tablename__ = "seo_keyword_opportunities"
    __table_args__ = (Index("ix_seo_kw_tenant_score", "tenant_id", "score"),)

    keyword = Column(String(500), nullable=False)
    intent = Column(String(80), nullable=True)
    score = Column(Integer, nullable=False, default=50)
    priority = Column(String(20), nullable=False, default="medium")
    source_run_id = Column(UUID(as_uuid=True), ForeignKey("seo_engine_runs.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), nullable=False, default="suggested", index=True)
    evidence_json = Column(JSONB, nullable=False, default=dict)


class SeoContentGap(TenantModel):
    __tablename__ = "seo_content_gaps"
    __table_args__ = (Index("ix_seo_gap_tenant", "tenant_id", "priority"),)

    topic = Column(String(500), nullable=False)
    gap_type = Column(String(80), nullable=False)
    priority = Column(String(20), nullable=False, default="medium")
    evidence_json = Column(JSONB, nullable=False, default=dict)
    source_run_id = Column(UUID(as_uuid=True), ForeignKey("seo_engine_runs.id", ondelete="SET NULL"), nullable=True)


class SeoSchemaFinding(TenantModel):
    __tablename__ = "seo_schema_findings"
    __table_args__ = (Index("ix_seo_schema_page", "tenant_id", "page_url"),)

    page_url = Column(Text, nullable=False)
    page_kind = Column(String(80), nullable=True)
    finding_type = Column(String(40), nullable=False)
    detail = Column(Text, nullable=True)
    proposed_jsonld = Column(JSONB, nullable=True)
    status = Column(String(20), nullable=False, default="open", index=True)


class SeoContentDraft(TenantModel):
    __tablename__ = "seo_content_drafts"
    __table_args__ = (Index("ix_seo_draft_status", "tenant_id", "status"),)

    kind = Column(String(40), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    body_md = Column(Text, nullable=False, default="")
    target_keyword = Column(String(500), nullable=True)
    intent = Column(String(120), nullable=True)
    city = Column(String(120), nullable=True)
    locale = Column(String(10), nullable=False, default="ar")
    status = Column(String(20), nullable=False, default="draft", index=True)
    meta_json = Column(JSONB, nullable=False, default=dict)
