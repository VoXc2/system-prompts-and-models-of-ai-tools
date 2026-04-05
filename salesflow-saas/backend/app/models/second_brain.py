"""
Second Brain — unified system memory, knowledge, graph edges, reasoning, learning, actions.

Additive layer: does not replace AuditLog, DomainEvent, AIConversation, Activity.
Ingestion writes SystemMemoryRecord rows + optional KnowledgeFact; graph and rules consume them.
"""

from __future__ import annotations

import enum
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    SmallInteger,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.models.compat import JSONB, UUID
from app.models.base import TenantModel


class MemorySource(str, enum.Enum):
    LOG = "log"
    EVENT = "event"
    API = "api"
    USER_ACTION = "user_action"
    MESSAGE = "message"
    ERROR = "error"
    PAYMENT = "payment"
    TASK = "task"
    REPORT = "report"
    DOCUMENT = "document"


class InsightPeriod(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class SuggestionStatus(str, enum.Enum):
    PENDING = "pending"
    APPLIED = "applied"
    DISMISSED = "dismissed"


class PendingActionStatus(str, enum.Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SystemMemoryRecord(TenantModel):
    """Canonical row: one structured fact the brain can query and link."""

    __tablename__ = "system_memory_records"
    __table_args__ = (
        Index("ix_memory_tenant_created", "tenant_id", "created_at"),
        Index("ix_memory_canonical", "tenant_id", "canonical_type"),
    )

    source = Column(String(32), nullable=False, index=True)  # MemorySource value
    source_table = Column(String(120), nullable=True)  # e.g. domain_events, audit_logs
    source_id = Column(UUID(as_uuid=True), nullable=True)
    canonical_type = Column(String(160), nullable=False, index=True)  # e.g. lead.created, api.GET.5xx
    payload = Column(JSONB, nullable=False, default=dict)
    correlation_id = Column(String(80), nullable=True, index=True)
    dedup_key = Column(String(200), nullable=True)


class KnowledgeFact(TenantModel):
    """Derived layer: summary, taxonomy, salience, entity links (Phase 2)."""

    __tablename__ = "knowledge_facts"
    __table_args__ = (Index("ix_kfact_memory", "memory_record_id"),)

    memory_record_id = Column(
        UUID(as_uuid=True), ForeignKey("system_memory_records.id", ondelete="CASCADE"), nullable=False
    )
    summary = Column(Text, nullable=False)
    category = Column(String(80), nullable=False, index=True)
    tags = Column(JSONB, nullable=False, default=list)
    importance = Column(SmallInteger, nullable=False, default=3)  # 1–5
    related_entities = Column(JSONB, nullable=False, default=list)
    embedding_model = Column(String(80), nullable=True)
    # Optional: link to pgvector row id elsewhere; keep facts table slim

    memory_record = relationship("SystemMemoryRecord", foreign_keys=[memory_record_id])


class MemoryGraphEdge(TenantModel):
    """Directed edges between unified memory records (Phase 3)."""

    __tablename__ = "memory_graph_edges"
    __table_args__ = (
        Index("ix_graph_head", "tenant_id", "head_memory_record_id"),
        Index("ix_graph_tail", "tenant_id", "tail_memory_record_id"),
    )

    head_memory_record_id = Column(
        UUID(as_uuid=True), ForeignKey("system_memory_records.id", ondelete="CASCADE"), nullable=False
    )
    tail_memory_record_id = Column(
        UUID(as_uuid=True), ForeignKey("system_memory_records.id", ondelete="CASCADE"), nullable=False
    )
    relation_type = Column(String(80), nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=1.0)
    edge_metadata = Column(JSONB, nullable=False, default=dict)


class ReasoningRule(TenantModel):
    """Declarative rules evaluated against metrics + memory (Phase 4)."""

    __tablename__ = "reasoning_rules"

    name = Column(String(160), nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    priority = Column(Integer, nullable=False, default=100, index=True)
    condition = Column(JSONB, nullable=False, default=dict)
    actions = Column(JSONB, nullable=False, default=list)
    risk_delta = Column(SmallInteger, nullable=True)
    opportunity_delta = Column(SmallInteger, nullable=True)


class LearningMetricSnapshot(TenantModel):
    """Aggregates for feedback loops (Phase 5)."""

    __tablename__ = "learning_metric_snapshots"
    __table_args__ = (
        UniqueConstraint("tenant_id", "period_start", "metric_key", name="uq_learning_metric_period"),
    )

    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False)
    metric_key = Column(String(120), nullable=False, index=True)
    dimensions = Column(JSONB, nullable=False, default=dict)
    value = Column(JSONB, nullable=False, default=dict)


class AutomationRunRecord(TenantModel):
    """Automation audit trail (Phase 8)."""

    __tablename__ = "automation_run_records"
    __table_args__ = (Index("ix_automation_tenant_started", "tenant_id", "started_at"),)

    automation_key = Column(String(200), nullable=False, index=True)
    trigger_memory_id = Column(
        UUID(as_uuid=True), ForeignKey("system_memory_records.id", ondelete="SET NULL"), nullable=True
    )
    reason_summary = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="success")
    result = Column(JSONB, nullable=False, default=dict)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)


class GeneratedInsight(TenantModel):
    """Wiki / digest content (Phase 7)."""

    __tablename__ = "generated_insights"
    __table_args__ = (
        UniqueConstraint("tenant_id", "period", "period_key", name="uq_generated_insight_period"),
    )

    period = Column(String(16), nullable=False)  # InsightPeriod value
    period_key = Column(String(32), nullable=False)
    title = Column(String(255), nullable=False)
    body_md = Column(Text, nullable=False)
    sources = Column(JSONB, nullable=False, default=list)


class SelfImprovementSuggestion(TenantModel):
    """Outputs from daily analysis (Phase 9); complements DurableTaskFlow checkpoints."""

    __tablename__ = "self_improvement_suggestions"

    category = Column(String(40), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    detail = Column(JSONB, nullable=False, default=dict)
    severity = Column(SmallInteger, nullable=False, default=2)
    status = Column(String(20), nullable=False, default="pending", index=True)


class PendingAction(TenantModel):
    """Action queue from rules or planner (Phase 6)."""

    __tablename__ = "pending_actions"
    __table_args__ = (Index("ix_pending_status_due", "tenant_id", "status", "scheduled_at"),)

    reasoning_rule_id = Column(
        UUID(as_uuid=True), ForeignKey("reasoning_rules.id", ondelete="SET NULL"), nullable=True
    )
    action_type = Column(String(64), nullable=False, index=True)
    payload = Column(JSONB, nullable=False, default=dict)
    status = Column(String(20), nullable=False, default="pending", index=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
