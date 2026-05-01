"""Targeting & Acquisition OS — يستهدف بذكاء، يقيّم المخاطر، يقترح القنوات.

Account-first targeting (شركات قبل أشخاص) + buying-committee mapping +
contactability gate + multi-channel strategy + reputation guard +
daily autopilot + self-growth mode + free diagnostic + contract drafts.

كل شيء deterministic، عربي، draft/approval-first، لا scraping ولا cold WA.
"""

from __future__ import annotations

from .account_finder import (
    AccountSignal,
    explain_why_now,
    rank_accounts,
    recommend_account_source_strategy,
    recommend_accounts,
    score_account_fit,
)
from .acquisition_scorecard import (
    build_acquisition_scorecard,
    calculate_meetings_booked,
    calculate_pipeline_created,
    calculate_productivity_score,
    calculate_risks_blocked,
)
from .buyer_role_mapper import (
    ALL_BUYER_ROLES,
    draft_role_based_angle,
    map_buying_committee,
    recommend_decision_maker_roles,
    recommend_influencer_roles,
)
from .contact_source_policy import (
    ALL_SOURCES,
    allowed_channels_for_source,
    classify_source,
    required_review_level,
    retention_recommendation,
    source_risk_score,
)
from .contactability_matrix import (
    ACTION_MODES,
    BLOCK_REASONS,
    allowed_action_modes,
    block_reason_codes,
    evaluate_contactability,
    explain_contactability_ar,
)
from .contract_drafts import (
    draft_agency_partner_outline,
    draft_dpa_outline,
    draft_pilot_agreement_outline,
    draft_referral_agreement_outline,
    draft_scope_of_work,
)
from .daily_autopilot import (
    build_daily_targeting_brief,
    build_end_of_day_report,
    prioritize_cards,
    recommend_today_actions,
)
from .email_strategy import (
    build_followup_sequence,
    draft_b2b_email,
    include_unsubscribe_footer,
    recommend_pacing,
    score_email_risk,
)
from .free_diagnostic import (
    analyze_uploaded_list_preview,
    build_free_growth_diagnostic,
    build_mini_proof_plan,
    recommend_paid_pilot_offer,
)
from .linkedin_strategy import (
    build_lead_gen_form_plan,
    build_manual_research_task,
    build_safe_connection_message,
    linkedin_do_not_do,
    recommend_linkedin_strategy,
)
from .outreach_scheduler import (
    build_outreach_plan,
    enforce_daily_limits,
    schedule_followups,
    stop_on_opt_out,
    summarize_plan_ar,
)
from .reputation_guard import (
    calculate_channel_reputation,
    recommend_recovery_action,
    risk_thresholds,
    should_pause_channel,
    summarize_reputation_ar,
)
from .self_growth_mode import (
    build_dealix_self_growth_plan,
    build_free_service_offer,
    build_self_growth_daily_brief,
    build_weekly_learning_report,
    recommend_dealix_targets,
)
from .service_offers import (
    build_offer_card,
    estimate_service_price,
    list_targeting_services,
    recommend_service_offer,
)
from .social_strategy import (
    build_social_listening_plan,
    draft_public_reply,
    recommend_social_sources,
    social_do_not_do,
)
from .whatsapp_strategy import (
    build_opt_in_request_template,
    draft_whatsapp_message,
    requires_opt_in,
    score_whatsapp_risk,
    whatsapp_do_not_do,
)

__all__ = [
    # account_finder
    "AccountSignal", "explain_why_now", "rank_accounts",
    "recommend_account_source_strategy", "recommend_accounts", "score_account_fit",
    # acquisition_scorecard
    "build_acquisition_scorecard", "calculate_meetings_booked",
    "calculate_pipeline_created", "calculate_productivity_score",
    "calculate_risks_blocked",
    # buyer_role_mapper
    "ALL_BUYER_ROLES", "draft_role_based_angle", "map_buying_committee",
    "recommend_decision_maker_roles", "recommend_influencer_roles",
    # contact_source_policy
    "ALL_SOURCES", "allowed_channels_for_source", "classify_source",
    "required_review_level", "retention_recommendation", "source_risk_score",
    # contactability_matrix
    "ACTION_MODES", "BLOCK_REASONS", "allowed_action_modes",
    "block_reason_codes", "evaluate_contactability", "explain_contactability_ar",
    # contract_drafts
    "draft_agency_partner_outline", "draft_dpa_outline",
    "draft_pilot_agreement_outline", "draft_referral_agreement_outline",
    "draft_scope_of_work",
    # daily_autopilot
    "build_daily_targeting_brief", "build_end_of_day_report",
    "prioritize_cards", "recommend_today_actions",
    # email_strategy
    "build_followup_sequence", "draft_b2b_email",
    "include_unsubscribe_footer", "recommend_pacing", "score_email_risk",
    # free_diagnostic
    "analyze_uploaded_list_preview", "build_free_growth_diagnostic",
    "build_mini_proof_plan", "recommend_paid_pilot_offer",
    # linkedin_strategy
    "build_lead_gen_form_plan", "build_manual_research_task",
    "build_safe_connection_message", "linkedin_do_not_do",
    "recommend_linkedin_strategy",
    # outreach_scheduler
    "build_outreach_plan", "enforce_daily_limits",
    "schedule_followups", "stop_on_opt_out", "summarize_plan_ar",
    # reputation_guard
    "calculate_channel_reputation", "recommend_recovery_action",
    "risk_thresholds", "should_pause_channel", "summarize_reputation_ar",
    # self_growth_mode
    "build_dealix_self_growth_plan", "build_free_service_offer",
    "build_self_growth_daily_brief", "build_weekly_learning_report",
    "recommend_dealix_targets",
    # service_offers
    "build_offer_card", "estimate_service_price",
    "list_targeting_services", "recommend_service_offer",
    # social_strategy
    "build_social_listening_plan", "draft_public_reply",
    "recommend_social_sources", "social_do_not_do",
    # whatsapp_strategy
    "build_opt_in_request_template", "draft_whatsapp_message",
    "requires_opt_in", "score_whatsapp_risk", "whatsapp_do_not_do",
]
