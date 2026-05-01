"""
AI Agent Registry — 11 named agents that run the Revenue OS.

Each agent has: name, scope, tools it uses, what it can do autonomously
vs. needs human approval, and the events it emits via the webhooks
ecosystem layer.

This is the catalog the UI reads to render the Agents panel and routing
decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentSpec:
    """One agent's contract — discoverable + auditable."""

    agent_id: str
    name_ar: str
    name_en: str
    role_ar: str                 # 1-line role description
    capabilities: tuple[str, ...]
    tools_used: tuple[str, ...]
    runs_on: str                  # cron / webhook / manual / inbound
    autonomy_level: str           # safe_auto / human_approval / advisory
    emits_events: tuple[str, ...]
    requires_pii_access: bool
    pdpl_compliance_gates: tuple[str, ...]
    avg_runtime_seconds: int
    inputs_required: tuple[str, ...]
    outputs: tuple[str, ...]


# ── The canonical 11 agents ───────────────────────────────────────
PROSPECTING_AGENT = AgentSpec(
    agent_id="prospecting",
    name_ar="عميل الاكتشاف",
    name_en="Prospecting Agent",
    role_ar="يبحث يومياً عن الشركات السعودية المناسبة لـ ICP العميل ويصنّفها.",
    capabilities=(
        "google_maps_search",
        "google_search_business",
        "linkedin_company_search",
        "icp_match_scoring",
        "dedup_against_existing",
    ),
    tools_used=("google_maps_api", "serpapi", "linkedin_scraper", "icp_matcher"),
    runs_on="cron_daily_06_00_riyadh",
    autonomy_level="safe_auto",
    emits_events=("lead.created",),
    requires_pii_access=False,
    pdpl_compliance_gates=("public_data_only", "no_personal_phone_collection"),
    avg_runtime_seconds=120,
    inputs_required=("icp_definition", "target_sectors", "target_cities"),
    outputs=("ranked_lead_list", "discovery_provenance"),
)

SIGNAL_AGENT = AgentSpec(
    agent_id="signal",
    name_ar="عميل الإشارات",
    name_en="Signal Agent",
    role_ar="يلتقط إشارات الشراء — توظيف، توسع، صفحات حجز، إعلانات، مناقصات.",
    capabilities=(
        "hiring_signal_detection",
        "website_change_monitor",
        "tender_feed_watcher",
        "ads_volume_tracker",
        "exhibition_calendar_match",
    ),
    tools_used=("linkedin_jobs_api", "wayback_machine", "tender_feeds", "google_ads_transparency"),
    runs_on="cron_hourly",
    autonomy_level="safe_auto",
    emits_events=("lead.qualified",),
    requires_pii_access=False,
    pdpl_compliance_gates=("public_signals_only",),
    avg_runtime_seconds=30,
    inputs_required=("watched_companies",),
    outputs=("signal_event", "freshness_score"),
)

ENRICHMENT_AGENT = AgentSpec(
    agent_id="enrichment",
    name_ar="عميل الإثراء",
    name_en="Enrichment Agent",
    role_ar="يكمّل بيانات الشركة وصناع القرار من مصادر متعددة.",
    capabilities=(
        "domain_to_company_resolution",
        "decision_maker_finder",
        "company_size_estimator",
        "tech_stack_detection",
        "social_handle_resolution",
    ),
    tools_used=("apollo", "zoominfo", "clearbit", "linkedin_scraper", "wikidata"),
    runs_on="webhook_lead_created",
    autonomy_level="safe_auto",
    emits_events=("lead.enriched",),
    requires_pii_access=True,
    pdpl_compliance_gates=("business_contact_only", "purpose_limitation_check"),
    avg_runtime_seconds=15,
    inputs_required=("company_domain_or_name",),
    outputs=("enriched_profile", "confidence_per_field"),
)

PERSONALIZATION_AGENT = AgentSpec(
    agent_id="personalization",
    name_ar="عميل التخصيص",
    name_en="Personalization Agent",
    role_ar="يصنع رسالة فريدة لكل شركة بالعربي/الإنجليزي بنبرة قطاعية مناسبة.",
    capabilities=(
        "arabic_first_writing",
        "sector_tone_adaptation",
        "why_now_integration",
        "ab_variant_generation",
        "objection_preemption",
    ),
    tools_used=("groq_llm", "anthropic_claude", "deepseek", "objection_library"),
    runs_on="webhook_lead_enriched",
    autonomy_level="human_approval",
    emits_events=("draft.created",),
    requires_pii_access=True,
    pdpl_compliance_gates=("approved_template_only", "no_sensitive_data_in_body"),
    avg_runtime_seconds=8,
    inputs_required=("enriched_lead", "sector_playbook", "channel"),
    outputs=("draft_ar", "draft_en", "tone_notes"),
)

COMPLIANCE_AGENT = AgentSpec(
    agent_id="compliance",
    name_ar="عميل الامتثال",
    name_en="Compliance Agent",
    role_ar="يفحص PDPL، consent، opt-out، risk قبل الإرسال.",
    capabilities=(
        "consent_ledger_check",
        "opt_out_verification",
        "pdpl_purpose_limitation",
        "risky_phrase_detection",
        "list_unsubscribe_header_validation",
    ),
    tools_used=("consent_db", "opt_out_db", "compliance_rules_engine"),
    runs_on="webhook_draft_created",
    autonomy_level="safe_auto",
    emits_events=("draft.approved", "draft.disqualified"),
    requires_pii_access=True,
    pdpl_compliance_gates=(
        "consent_present",
        "purpose_logged",
        "opt_out_path_present",
        "data_minimization",
        "retention_policy_set",
    ),
    avg_runtime_seconds=2,
    inputs_required=("draft", "recipient_consent_state"),
    outputs=("approved_or_blocked", "reason_if_blocked"),
)

OUTREACH_AGENT = AgentSpec(
    agent_id="outreach",
    name_ar="عميل التواصل",
    name_en="Outreach Agent",
    role_ar="يختار القناة المناسبة (WhatsApp / إيميل / LinkedIn / مكالمة) ويُرسل.",
    capabilities=(
        "channel_selection",
        "send_time_optimization",
        "provider_chain_management",
        "rate_limit_obeyance",
        "delivery_verification",
    ),
    tools_used=(
        "whatsapp_smart_chain",
        "gmail_oauth",
        "linkedin_inmail",
        "twilio_voice",
    ),
    runs_on="webhook_draft_approved",
    autonomy_level="safe_auto",
    emits_events=("draft.sent",),
    requires_pii_access=True,
    pdpl_compliance_gates=("compliance_pre_send_pass",),
    avg_runtime_seconds=3,
    inputs_required=("approved_draft", "recipient_channel_preferences"),
    outputs=("send_receipt", "provider_used", "fallback_chain_record"),
)

REPLY_AGENT = AgentSpec(
    agent_id="reply",
    name_ar="عميل الردود",
    name_en="Reply Agent",
    role_ar="يصنّف كل رد: مهتم / ليس الآن / objection / unsubscribe / spam.",
    capabilities=(
        "intent_classification",
        "sentiment_analysis",
        "objection_extraction",
        "unsubscribe_detection",
        "auto_acknowledge_arabic",
    ),
    tools_used=("groq_llm", "objection_library", "consent_db"),
    runs_on="webhook_inbound_message",
    autonomy_level="safe_auto",
    emits_events=("reply.received", "reply.classified"),
    requires_pii_access=True,
    pdpl_compliance_gates=("opt_out_processed_immediately",),
    avg_runtime_seconds=4,
    inputs_required=("inbound_text", "thread_history"),
    outputs=("intent_label", "next_action_suggestion", "score_delta"),
)

MEETING_AGENT = AgentSpec(
    agent_id="meeting",
    name_ar="عميل الاجتماعات",
    name_en="Meeting Agent",
    role_ar="يقترح مواعيد، يرسل رابط حجز، ويتابع تأكيد الحضور.",
    capabilities=(
        "calendar_availability_check",
        "timezone_handling_riyadh",
        "calendly_link_generation",
        "no_show_followup",
        "agenda_pre_send",
    ),
    tools_used=("calendly_api", "google_calendar", "whatsapp_smart_chain"),
    runs_on="webhook_reply_classified_positive",
    autonomy_level="human_approval",
    emits_events=("demo.booked",),
    requires_pii_access=True,
    pdpl_compliance_gates=("data_retention_after_meeting",),
    avg_runtime_seconds=6,
    inputs_required=("contact", "host_calendar"),
    outputs=("booking_link", "confirmation_sent"),
)

DEAL_COACH_AGENT = AgentSpec(
    agent_id="deal_coach",
    name_ar="عميل الإغلاق",
    name_en="Deal Coach Agent",
    role_ar="يعطي next step + اعتراضات متوقعة + زاوية العرض لكل صفقة نشطة.",
    capabilities=(
        "deal_stage_diagnosis",
        "objection_prediction",
        "proposal_angle_recommendation",
        "multi_thread_advisor",
        "stalled_deal_recovery_plan",
    ),
    tools_used=("revenue_graph", "objection_library", "anthropic_claude"),
    runs_on="cron_daily_or_on_demand",
    autonomy_level="advisory",
    emits_events=(),
    requires_pii_access=True,
    pdpl_compliance_gates=("internal_use_only",),
    avg_runtime_seconds=10,
    inputs_required=("deal_record", "history"),
    outputs=("next_steps_list", "predicted_objections", "winning_angle"),
)

CUSTOMER_SUCCESS_AGENT = AgentSpec(
    agent_id="customer_success",
    name_ar="عميل نجاح العميل",
    name_en="Customer Success Agent",
    role_ar="يراقب health score، يكتب QBR، يقترح upsell، ينبّه قبل churn.",
    capabilities=(
        "health_score_monitoring",
        "qbr_drafting",
        "upsell_signal_detection",
        "churn_prediction",
        "expansion_likelihood_scoring",
    ),
    tools_used=("customer_success_engine", "benchmarks", "anthropic_claude"),
    runs_on="cron_weekly",
    autonomy_level="advisory",
    emits_events=("health.changed", "churn.predicted", "qbr.generated"),
    requires_pii_access=True,
    pdpl_compliance_gates=("aggregate_only_for_benchmarks",),
    avg_runtime_seconds=20,
    inputs_required=("customer_id", "30_day_signals"),
    outputs=("health_report", "qbr_markdown", "next_quarter_focus"),
)

EXECUTIVE_ANALYST_AGENT = AgentSpec(
    agent_id="executive_analyst",
    name_ar="المحلل التنفيذي",
    name_en="Executive Analyst Agent",
    role_ar="يكتب تقرير أسبوعي لصاحب الشركة: ماذا حدث، ماذا نفعل، أين المال.",
    capabilities=(
        "weekly_metrics_aggregation",
        "leak_summarization",
        "decision_recommendation",
        "forecast_30_60_90",
        "ar_executive_brief_writing",
    ),
    tools_used=("revenue_graph", "leak_detector", "proof_pack", "pulse_data"),
    runs_on="cron_weekly_sunday_07_00",
    autonomy_level="advisory",
    emits_events=("pulse.published",),
    requires_pii_access=True,
    pdpl_compliance_gates=("internal_brief_only",),
    avg_runtime_seconds=45,
    inputs_required=("customer_id", "week_window"),
    outputs=("executive_brief_ar", "top_3_decisions", "risk_alerts"),
)


ALL_AGENTS: tuple[AgentSpec, ...] = (
    PROSPECTING_AGENT,
    SIGNAL_AGENT,
    ENRICHMENT_AGENT,
    PERSONALIZATION_AGENT,
    COMPLIANCE_AGENT,
    OUTREACH_AGENT,
    REPLY_AGENT,
    MEETING_AGENT,
    DEAL_COACH_AGENT,
    CUSTOMER_SUCCESS_AGENT,
    EXECUTIVE_ANALYST_AGENT,
)


# ── Public API ────────────────────────────────────────────────────
def get_agent(agent_id: str) -> AgentSpec | None:
    for a in ALL_AGENTS:
        if a.agent_id == agent_id:
            return a
    return None


def list_agents_by_runtime(*, runs_on_substring: str) -> list[AgentSpec]:
    return [a for a in ALL_AGENTS if runs_on_substring in a.runs_on]


def list_agents_by_autonomy(level: str) -> list[AgentSpec]:
    return [a for a in ALL_AGENTS if a.autonomy_level == level]


def agents_summary() -> dict[str, int]:
    return {
        "total": len(ALL_AGENTS),
        "safe_auto": len(list_agents_by_autonomy("safe_auto")),
        "human_approval": len(list_agents_by_autonomy("human_approval")),
        "advisory": len(list_agents_by_autonomy("advisory")),
        "pdpl_gated": sum(1 for a in ALL_AGENTS if a.pdpl_compliance_gates),
        "pii_aware": sum(1 for a in ALL_AGENTS if a.requires_pii_access),
    }
