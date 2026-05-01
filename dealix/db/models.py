"""
SQLAlchemy 2.0 async ORM models.
نماذج قاعدة البيانات.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core.utils import utcnow


class Base(DeclarativeBase):
    """Base class for all models."""


class LeadRecord(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    company_name: Mapped[str] = mapped_column(String(255), default="")
    contact_name: Mapped[str] = mapped_column(String(255), default="")
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    sector: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    region: Mapped[str | None] = mapped_column(String(128), nullable=True)
    company_size: Mapped[str | None] = mapped_column(String(32), nullable=True)
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="new", index=True)
    fit_score: Mapped[float] = mapped_column(Float, default=0.0)
    urgency_score: Mapped[float] = mapped_column(Float, default=0.0)
    locale: Mapped[str] = mapped_column(String(4), default="ar")
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    pain_points: Mapped[list] = mapped_column(JSON, default=list)
    meta_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    dedup_hash: Mapped[str] = mapped_column(String(32), default="", index=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    deals: Mapped[list[DealRecord]] = relationship(back_populates="lead")


class DealRecord(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id"), index=True)
    hubspot_deal_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hubspot_contact_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(8), default="SAR")
    stage: Mapped[str] = mapped_column(String(64), default="new")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    lead: Mapped[LeadRecord] = relationship(back_populates="deals")


class AgentRunRecord(Base):
    """Audit log — every agent invocation."""

    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    agent_name: Mapped[str] = mapped_column(String(64), index=True)
    lead_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(16), default="success")
    duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    input_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)


class ConversationRecord(Base):
    """Inbound message + outbound auto-response — full audit log."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    lead_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    channel: Mapped[str] = mapped_column(String(32), index=True)  # whatsapp/email/form/sms/linkedin
    sender: Mapped[str | None] = mapped_column(String(255), nullable=True)
    inbound_message: Mapped[str] = mapped_column(Text, default="")
    outbound_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    classification: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    sentiment: Mapped[str | None] = mapped_column(String(16), nullable=True)
    next_action: Mapped[str | None] = mapped_column(String(64), nullable=True)
    escalation_required: Mapped[bool] = mapped_column(default=False)
    auto_sent: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)


class TaskRecord(Base):
    """Follow-up tasks scheduled by the autonomous engine."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    lead_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    deal_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    task_type: Mapped[str] = mapped_column(String(32), index=True)  # follow_up, demo, payment_check, onboarding
    due_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)  # pending, done, skipped
    owner: Mapped[str] = mapped_column(String(64), default="auto")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)


class CompanyRecord(Base):
    """Subscriber company profile — one per Dealix customer."""

    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    products: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_customer_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    average_deal_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    sales_cycle_length_days: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_lead_sources: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_crm: Mapped[str | None] = mapped_column(String(64), nullable=True)
    booking_link: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sales_team_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    whatsapp_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tone_of_voice: Mapped[str] = mapped_column(String(64), default="professional_khaliji")
    languages: Mapped[str] = mapped_column(String(64), default="ar,en")
    pricing_rules: Mapped[str | None] = mapped_column(Text, nullable=True)
    handoff_rules: Mapped[str | None] = mapped_column(Text, nullable=True)
    privacy_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    success_metric: Mapped[str | None] = mapped_column(Text, nullable=True)
    icp_profile: Mapped[dict] = mapped_column("icp_profile", JSON, default=dict)
    channel_plan: Mapped[dict] = mapped_column("channel_plan", JSON, default=dict)
    offer_ladder: Mapped[dict] = mapped_column("offer_ladder", JSON, default=dict)
    automation_policy: Mapped[dict] = mapped_column("automation_policy", JSON, default=dict)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class PartnerRecord(Base):
    """Partner/agency record for distribution channel."""

    __tablename__ = "partners"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    company_name: Mapped[str] = mapped_column(String(255))
    partner_type: Mapped[str] = mapped_column(String(32), index=True)  # AGENCY/IMPLEMENTATION/REFERRAL/STRATEGIC
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="prospecting", index=True)  # prospecting/active/paused
    commission_terms: Mapped[str | None] = mapped_column(Text, nullable=True)
    setup_fee_sar: Mapped[float] = mapped_column(Float, default=0.0)
    mrr_share_pct: Mapped[float] = mapped_column(Float, default=0.0)
    clients_signed: Mapped[int] = mapped_column(default=0)
    next_action: Mapped[str | None] = mapped_column(String(64), nullable=True)
    next_action_at: Mapped[datetime | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class CustomerRecord(Base):
    """Customer = subscribed paying company. One per closed deal."""

    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    company_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    deal_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    plan: Mapped[str] = mapped_column(String(32), default="pilot")  # pilot/starter/growth/scale
    onboarding_status: Mapped[str] = mapped_column(String(32), default="kickoff_pending", index=True)
    pilot_start_at: Mapped[datetime | None] = mapped_column(nullable=True)
    pilot_end_at: Mapped[datetime | None] = mapped_column(nullable=True)
    success_metric: Mapped[str | None] = mapped_column(Text, nullable=True)
    daily_report_sent: Mapped[int] = mapped_column(default=0)
    nps_score: Mapped[int | None] = mapped_column(nullable=True)
    churn_risk: Mapped[str] = mapped_column(String(16), default="low")  # low/medium/high
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class OutreachQueueRecord(Base):
    """Outreach message queue — auto or human-approval."""

    __tablename__ = "outreach_queue"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    lead_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    channel: Mapped[str] = mapped_column(String(32), index=True)
    message: Mapped[str] = mapped_column(Text)
    approval_required: Mapped[bool] = mapped_column(default=True)
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)  # queued/approved/sent/skipped
    due_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    risk_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


# ── Data Lake + Lead Graph (Phase 12) ──────────────────────────────
# Compliant ingestion: every row carries source/allowed_use/risk/opt-out.

class RawLeadImport(Base):
    """One row per uploaded dataset (CSV/Excel/JSON)."""

    __tablename__ = "raw_lead_imports"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_name: Mapped[str] = mapped_column(String(255), index=True)
    source_type: Mapped[str] = mapped_column(String(32), index=True)  # owned/public/paid/partner/google_maps/google_search/manual
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    imported_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    allowed_use: Mapped[str] = mapped_column(String(128), default="business_contact_research_only")
    consent_status: Mapped[str] = mapped_column(String(32), default="unknown")  # unknown/opted_in/legitimate_interest/owned
    risk_level: Mapped[str] = mapped_column(String(16), default="medium", index=True)  # low/medium/high
    rows_total: Mapped[int] = mapped_column(Integer, default=0)
    rows_normalized: Mapped[int] = mapped_column(Integer, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0)
    rows_duplicate: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="raw", index=True)  # raw/normalizing/normalized/deduped/done/error
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class RawLeadRow(Base):
    """One row per record inside an import."""

    __tablename__ = "raw_lead_rows"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    import_id: Mapped[str] = mapped_column(String(64), index=True)
    raw_json: Mapped[dict] = mapped_column(JSON, default=dict)
    normalized_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)  # pending/ok/rejected/duplicate
    account_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class AccountRecord(Base):
    """Canonical company entity in the lead graph."""

    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    company_name: Mapped[str] = mapped_column(String(255), index=True)
    normalized_name: Mapped[str] = mapped_column(String(255), index=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True, default="SA")
    sector: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    google_place_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    source_count: Mapped[int] = mapped_column(Integer, default=1)
    best_source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    risk_level: Mapped[str] = mapped_column(String(16), default="medium", index=True)
    status: Mapped[str] = mapped_column(String(32), default="new", index=True)  # new/enriched/qualified/blocked
    data_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    extra: Mapped[dict] = mapped_column("extra_json", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class ContactRecord(Base):
    """Person attached to an account. PDPL-aware: opt_out + consent_status mandatory."""

    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str | None] = mapped_column(String(128), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="manual", index=True)
    consent_status: Mapped[str] = mapped_column(String(32), default="unknown", index=True)
    opt_out: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    risk_level: Mapped[str] = mapped_column(String(16), default="medium")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class SignalRecord(Base):
    """Time-series signals attached to an account (tech, intent, hire, news)."""

    __tablename__ = "signals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(64), index=True)
    signal_type: Mapped[str] = mapped_column(String(64), index=True)  # tech/intent/hire/news/funding/integration
    signal_value: Mapped[str] = mapped_column(String(500))
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    detected_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)


class LeadScoreRecord(Base):
    """Latest score per account (one current row per account)."""

    __tablename__ = "lead_scores"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(64), index=True)
    fit_score: Mapped[float] = mapped_column(Float, default=0.0)
    intent_score: Mapped[float] = mapped_column(Float, default=0.0)
    urgency_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    total_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    priority: Mapped[str] = mapped_column(String(8), default="P3", index=True)  # P0/P1/P2/P3/BACKLOG
    recommended_channel: Mapped[str | None] = mapped_column(String(32), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)


class SuppressionRecord(Base):
    """Opt-out / do-not-contact list. Checked before any outbound queue write."""

    __tablename__ = "data_suppression_list"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    reason: Mapped[str] = mapped_column(String(128), default="opt_out")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class GmailDraftRecord(Base):
    """Gmail draft created by the revenue machine — Sami reviews + sends."""

    __tablename__ = "gmail_drafts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    queue_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    to_email: Mapped[str] = mapped_column(String(255), index=True)
    subject: Mapped[str] = mapped_column(String(500))
    body_plain: Mapped[str] = mapped_column(Text)
    sender_email: Mapped[str] = mapped_column(String(255), default="")
    gmail_draft_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    gmail_message_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="created", index=True)
    # created | reviewed | sent | discarded | failed
    sequence_step: Mapped[int] = mapped_column(Integer, default=0)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True, index=True)
    discarded_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class LinkedInDraftRecord(Base):
    """LinkedIn drafts — manual send only (no automation per LinkedIn ToS)."""

    __tablename__ = "linkedin_drafts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255))
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_search_query: Mapped[str] = mapped_column(String(500))
    company_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason_for_outreach: Mapped[str | None] = mapped_column(Text, nullable=True)
    message_ar: Mapped[str] = mapped_column(Text)
    message_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    followup_day_3: Mapped[str | None] = mapped_column(Text, nullable=True)
    followup_day_7: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    # draft | sent | replied | unreachable
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    reply_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    reply_received_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class DataSourceProvenance(Base):
    """Provenance record — every signal/account/contact pointer back to source.

    Required for PDPL audit trail + to dedupe "same lead from 3 sources".
    """

    __tablename__ = "data_source_provenance"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(32), index=True)  # account|contact|signal|deal
    entity_id: Mapped[str] = mapped_column(String(64), index=True)
    source_name: Mapped[str] = mapped_column(String(255), index=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_type: Mapped[str] = mapped_column(String(32))  # public|paid|partner|owned|google_maps|google_search|manual
    allowed_use: Mapped[str] = mapped_column(String(128), default="business_contact_research_only")
    collected_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    refresh_needed: Mapped[bool] = mapped_column(Boolean, default=False)


class EmailSendLog(Base):
    """Auditable log of every email send attempt — required for compliance + bounce tracking."""

    __tablename__ = "email_send_log"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    queue_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    to_email: Mapped[str] = mapped_column(String(255), index=True)
    subject: Mapped[str] = mapped_column(String(500))
    body_preview: Mapped[str] = mapped_column(Text, default="")
    sender_email: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    # queued | sent | bounced | replied | opt_out | blocked_compliance | failed
    gmail_message_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    bounce_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reply_classification: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reply_received_at: Mapped[datetime | None] = mapped_column(nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True, index=True)
    batch_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    sequence_step: Mapped[int] = mapped_column(Integer, default=0)  # 0=initial, 2/5/10 for follow-ups
    compliance_check: Mapped[dict] = mapped_column("compliance_check_json", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class WebhookSubscriptionRecord(Base):
    """Outbound webhook subscription — Scale tier ecosystem play.

    Customers register an HTTPS endpoint + secret. Dealix POSTs signed events
    when matching activity occurs (lead.created, deal.won, payment.received...).
    """

    __tablename__ = "webhook_subscriptions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(64), index=True)
    endpoint_url: Mapped[str] = mapped_column(String(500))
    secret: Mapped[str] = mapped_column(String(128))  # HMAC signing key — never exposed back
    events: Mapped[list] = mapped_column(JSON, default=list)  # empty list = all events
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_delivery_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class ProofLedgerEventRecord(Base):
    """أحداث إثبات إيراد — تقديرات تشغيلية حتى ربط CRM محاسبي."""

    __tablename__ = "proof_ledger_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), default="default", index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    revenue_influenced_sar_estimate: Mapped[float] = mapped_column(Float, default=0.0)
    notes_ar: Mapped[str] = mapped_column(Text, default="")
    extra_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)


class WebhookDeliveryRecord(Base):
    """Per-attempt delivery audit — debug + replay support."""

    __tablename__ = "webhook_deliveries"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    subscription_id: Mapped[str] = mapped_column(String(64), index=True)
    customer_id: Mapped[str] = mapped_column(String(64), index=True)
    event_id: Mapped[str] = mapped_column(String(64), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    endpoint_url: Mapped[str] = mapped_column(String(500))
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    request_signature: Mapped[str] = mapped_column(String(255), default="")
    payload: Mapped[dict] = mapped_column("payload_json", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, index=True)
