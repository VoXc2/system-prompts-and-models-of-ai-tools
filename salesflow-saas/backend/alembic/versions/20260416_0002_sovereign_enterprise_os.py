"""Sovereign Enterprise Growth OS — new tables for all 5 planes

Revision ID: 20260416_0002
Revises: 20260403_0001_baseline
Create Date: 2026-04-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260416_0002"
down_revision = "20260403_0001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── evidence_packs ──────────────────────────────────────────
    op.create_table(
        "evidence_packs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_type", sa.String(80), nullable=False, index=True),
        sa.Column("decision_ref_type", sa.String(80), nullable=True),
        sa.Column("decision_ref_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("title_ar", sa.String(512), nullable=False),
        sa.Column("title_en", sa.String(512), nullable=True),
        sa.Column("summary_ar", sa.Text, nullable=True),
        sa.Column("sources", postgresql.JSONB, nullable=True),
        sa.Column("assumptions", postgresql.JSONB, nullable=True),
        sa.Column("alternatives", postgresql.JSONB, nullable=True),
        sa.Column("financial_model_version", sa.String(40), nullable=True),
        sa.Column("freshness_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("policy_notes", postgresql.JSONB, nullable=True),
        sa.Column("approval_class", sa.String(20), nullable=False, server_default="B"),
        sa.Column("reversibility_class", sa.String(20), nullable=False, server_default="partial"),
        sa.Column("sensitivity_level", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("rollback_notes", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
    )

    # ── sovereign_decisions ─────────────────────────────────────
    op.create_table(
        "sovereign_decisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_type", sa.String(80), nullable=False, index=True),
        sa.Column("lane", sa.String(40), nullable=False, server_default="executive_reasoning"),
        sa.Column("model_used", sa.String(80), nullable=True),
        sa.Column("prompt_version", sa.String(40), nullable=True),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("schema_valid", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("contradiction_detected", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("cost_sar", sa.Numeric(10, 4), nullable=True),
        sa.Column("recommendation_ar", sa.Text, nullable=True),
        sa.Column("recommendation_en", sa.Text, nullable=True),
        sa.Column("structured_output", postgresql.JSONB, nullable=True),
        sa.Column("next_best_action", postgresql.JSONB, nullable=True),
        sa.Column("evidence_pack_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("evidence_packs.id"), nullable=True),
        sa.Column("hitl_required", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("hitl_status", sa.String(20), nullable=True),
        sa.Column("hitl_reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("hitl_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("hitl_note", sa.Text, nullable=True),
    )

    # ── partners ────────────────────────────────────────────────
    op.create_table(
        "partners",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("name_ar", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
        sa.Column("partner_type", sa.String(60), nullable=False, server_default="channel"),
        sa.Column("status", sa.String(30), nullable=False, server_default="scouted"),
        sa.Column("strategic_fit_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("channel_economics", postgresql.JSONB, nullable=True),
        sa.Column("alliance_structure", postgresql.JSONB, nullable=True),
        sa.Column("term_sheet_draft", sa.Text, nullable=True),
        sa.Column("term_sheet_approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("quarterly_revenue_sar", sa.Numeric(18, 2), nullable=True),
        sa.Column("contribution_margin_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("active_deals_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("nps_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(50), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evidence_pack_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("evidence_packs.id"), nullable=True),
    )

    # ── partner_scorecards ──────────────────────────────────────
    op.create_table(
        "partner_scorecards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("partners.id"), nullable=False, index=True),
        sa.Column("period_label", sa.String(20), nullable=False),
        sa.Column("revenue_sar", sa.Numeric(18, 2), nullable=True),
        sa.Column("deals_closed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("contribution_margin_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("nps_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("notes_ar", sa.Text, nullable=True),
    )

    # ── ma_targets ──────────────────────────────────────────────
    op.create_table(
        "ma_targets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("company_name_ar", sa.String(255), nullable=False),
        sa.Column("company_name_en", sa.String(255), nullable=True),
        sa.Column("sector", sa.String(80), nullable=True),
        sa.Column("geography", sa.String(80), nullable=True, server_default="Saudi Arabia"),
        sa.Column("status", sa.String(40), nullable=False, server_default="sourced"),
        sa.Column("strategic_rationale_ar", sa.Text, nullable=True),
        sa.Column("synergy_model", postgresql.JSONB, nullable=True),
        sa.Column("valuation_low_sar", sa.Numeric(18, 2), nullable=True),
        sa.Column("valuation_high_sar", sa.Numeric(18, 2), nullable=True),
        sa.Column("offer_price_sar", sa.Numeric(18, 2), nullable=True),
        sa.Column("dd_room_url", sa.String(512), nullable=True),
        sa.Column("dd_access_policy", postgresql.JSONB, nullable=True),
        sa.Column("ic_memo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("evidence_packs.id"), nullable=True),
        sa.Column("signed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lead_advisor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )

    # ── dd_checklists ────────────────────────────────────────────
    op.create_table(
        "dd_checklists",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ma_target_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ma_targets.id"), nullable=False, index=True),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("item_ar", sa.String(512), nullable=False),
        sa.Column("item_en", sa.String(512), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes_ar", sa.Text, nullable=True),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="medium"),
    )

    # ── expansion_markets ────────────────────────────────────────
    op.create_table(
        "expansion_markets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("market_name_ar", sa.String(255), nullable=False),
        sa.Column("market_name_en", sa.String(255), nullable=True),
        sa.Column("country_code", sa.String(10), nullable=False),
        sa.Column("region", sa.String(80), nullable=True),
        sa.Column("status", sa.String(40), nullable=False, server_default="scanning"),
        sa.Column("priority_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("tam_sar", sa.Numeric(18, 2), nullable=True),
        sa.Column("compliance_readiness", postgresql.JSONB, nullable=True),
        sa.Column("localization_requirements", postgresql.JSONB, nullable=True),
        sa.Column("pricing_plan", postgresql.JSONB, nullable=True),
        sa.Column("channel_plan", postgresql.JSONB, nullable=True),
        sa.Column("launch_readiness_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("stop_loss_threshold", postgresql.JSONB, nullable=True),
        sa.Column("launched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evidence_pack_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("evidence_packs.id"), nullable=True),
    )

    # ── expansion_actuals ────────────────────────────────────────
    op.create_table(
        "expansion_actuals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("market_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("expansion_markets.id"), nullable=False, index=True),
        sa.Column("period_label", sa.String(20), nullable=False),
        sa.Column("revenue_forecast_sar", sa.Numeric(18, 2), nullable=True),
        sa.Column("revenue_actual_sar", sa.Numeric(18, 2), nullable=True),
        sa.Column("leads_forecast", sa.Integer, nullable=True),
        sa.Column("leads_actual", sa.Integer, nullable=True),
        sa.Column("variance_pct", sa.Numeric(7, 2), nullable=True),
        sa.Column("notes_ar", sa.Text, nullable=True),
    )

    # ── pmi_programs ─────────────────────────────────────────────
    op.create_table(
        "pmi_programs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("name_ar", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
        sa.Column("ma_target_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ma_targets.id"), nullable=True, index=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="day1_readiness"),
        sa.Column("day1_checklist", postgresql.JSONB, nullable=True),
        sa.Column("plan_30", postgresql.JSONB, nullable=True),
        sa.Column("plan_60", postgresql.JSONB, nullable=True),
        sa.Column("plan_90", postgresql.JSONB, nullable=True),
        sa.Column("synergy_realized_sar", sa.Numeric(18, 2), nullable=True),
        sa.Column("synergy_target_sar", sa.Numeric(18, 2), nullable=True),
        sa.Column("risk_register", postgresql.JSONB, nullable=True),
    )

    # ── pmi_tasks ────────────────────────────────────────────────
    op.create_table(
        "pmi_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("program_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("pmi_programs.id"), nullable=False, index=True),
        sa.Column("phase", sa.String(20), nullable=False),
        sa.Column("title_ar", sa.String(512), nullable=False),
        sa.Column("title_en", sa.String(512), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dependency_ids", postgresql.JSONB, nullable=True),
        sa.Column("escalated", sa.Boolean, nullable=False, server_default="false"),
    )

    # ── policy_violations ────────────────────────────────────────
    op.create_table(
        "policy_violations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("violation_type", sa.String(80), nullable=False, index=True),
        sa.Column("severity", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("resource_type", sa.String(80), nullable=True),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("triggered_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("policy_ref", sa.String(255), nullable=True),
        sa.Column("description_ar", sa.Text, nullable=False),
        sa.Column("description_en", sa.Text, nullable=True),
        sa.Column("remediation_ar", sa.Text, nullable=True),
        sa.Column("resolved", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )

    # ── tool_verification_ledger ─────────────────────────────────
    op.create_table(
        "tool_verification_ledger",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("agent_role", sa.String(80), nullable=False),
        sa.Column("tool_name", sa.String(120), nullable=False, index=True),
        sa.Column("intended_action", sa.Text, nullable=True),
        sa.Column("claimed_action", sa.Text, nullable=True),
        sa.Column("actual_tool_call", postgresql.JSONB, nullable=True),
        sa.Column("side_effects", postgresql.JSONB, nullable=True),
        sa.Column("contradiction_status", sa.String(20), nullable=False, server_default="none"),
        sa.Column("correlation_id", sa.String(80), nullable=True, index=True),
        sa.Column("trace_id", sa.String(80), nullable=True, index=True),
        sa.Column("span_id", sa.String(80), nullable=True),
        sa.Column("outcome", sa.String(20), nullable=False, server_default="success"),
        sa.Column("latency_ms", sa.Integer, nullable=True),
    )

    # ── contradiction_records ────────────────────────────────────
    op.create_table(
        "contradiction_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("agent_role", sa.String(80), nullable=False, index=True),
        sa.Column("tool_ledger_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tool_verification_ledger.id"), nullable=True),
        sa.Column("intended_action_summary", sa.Text, nullable=False),
        sa.Column("actual_action_summary", sa.Text, nullable=False),
        sa.Column("contradiction_type", sa.String(60), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("resolution_notes", sa.Text, nullable=True),
        sa.Column("correlation_id", sa.String(80), nullable=True, index=True),
    )

    # ── connector_registry ───────────────────────────────────────
    op.create_table(
        "connector_registry",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("connector_key", sa.String(80), nullable=False, index=True),
        sa.Column("display_name_ar", sa.String(255), nullable=False),
        sa.Column("display_name_en", sa.String(255), nullable=True),
        sa.Column("vendor", sa.String(80), nullable=True),
        sa.Column("api_version", sa.String(40), nullable=False),
        sa.Column("contract_schema", postgresql.JSONB, nullable=True),
        sa.Column("retry_policy", postgresql.JSONB, nullable=True),
        sa.Column("timeout_ms", sa.Integer, nullable=False, server_default="30000"),
        sa.Column("idempotency_key_strategy", sa.String(80), nullable=False, server_default="request_id"),
        sa.Column("approval_policy", sa.String(20), nullable=False, server_default="A"),
        sa.Column("audit_mapping", postgresql.JSONB, nullable=True),
        sa.Column("telemetry_mapping", postgresql.JSONB, nullable=True),
        sa.Column("rollback_notes", sa.Text, nullable=True),
        sa.Column("compensation_strategy", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("deprecated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("health_status", sa.String(20), nullable=False, server_default="unknown"),
        sa.Column("last_error", sa.Text, nullable=True),
    )

    # ── model_routing_configs ────────────────────────────────────
    op.create_table(
        "model_routing_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lane", sa.String(60), nullable=False, index=True),
        sa.Column("primary_model", sa.String(80), nullable=False),
        sa.Column("fallback_model", sa.String(80), nullable=True),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("max_tokens", sa.Integer, nullable=True),
        sa.Column("temperature", sa.Numeric(3, 2), nullable=True),
        sa.Column("requires_structured_output", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("output_schema", postgresql.JSONB, nullable=True),
        sa.Column("min_confidence_threshold", sa.Numeric(5, 2), nullable=True),
        sa.Column("arabic_quality_check", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("hitl_required", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("approval_class", sa.String(10), nullable=False, server_default="A"),
        sa.Column("avg_latency_ms", sa.Integer, nullable=True),
        sa.Column("schema_adherence_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("contradiction_rate_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("arabic_quality_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("cost_per_task_sar", sa.Numeric(10, 4), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
    )

    # ── saudi_compliance_controls ────────────────────────────────
    op.create_table(
        "saudi_compliance_controls",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("framework", sa.String(60), nullable=False, index=True),
        sa.Column("control_ref", sa.String(80), nullable=False),
        sa.Column("title_ar", sa.String(512), nullable=False),
        sa.Column("title_en", sa.String(512), nullable=True),
        sa.Column("description_ar", sa.Text, nullable=True),
        sa.Column("risk_category", sa.String(80), nullable=True),
        sa.Column("implementation_status", sa.String(30), nullable=False, server_default="planned"),
        sa.Column("platform_control_mapping", postgresql.JSONB, nullable=True),
        sa.Column("evidence_ref", postgresql.JSONB, nullable=True),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="high"),
        sa.Column("penalty_notes_ar", sa.Text, nullable=True),
    )

    # ── board_packs ──────────────────────────────────────────────
    op.create_table(
        "board_packs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("title_ar", sa.String(512), nullable=False),
        sa.Column("title_en", sa.String(512), nullable=True),
        sa.Column("pack_type", sa.String(60), nullable=False),
        sa.Column("period_label", sa.String(20), nullable=True),
        sa.Column("content_ar", sa.Text, nullable=True),
        sa.Column("structured_data", postgresql.JSONB, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("approval_items", postgresql.JSONB, nullable=True),
        sa.Column("policy_violations_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("risk_heatmap", postgresql.JSONB, nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("board_packs")
    op.drop_table("saudi_compliance_controls")
    op.drop_table("model_routing_configs")
    op.drop_table("connector_registry")
    op.drop_table("contradiction_records")
    op.drop_table("tool_verification_ledger")
    op.drop_table("policy_violations")
    op.drop_table("pmi_tasks")
    op.drop_table("pmi_programs")
    op.drop_table("expansion_actuals")
    op.drop_table("expansion_markets")
    op.drop_table("dd_checklists")
    op.drop_table("ma_targets")
    op.drop_table("partner_scorecards")
    op.drop_table("partners")
    op.drop_table("sovereign_decisions")
    op.drop_table("evidence_packs")
