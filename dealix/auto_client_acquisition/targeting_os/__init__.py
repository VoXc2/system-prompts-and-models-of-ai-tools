"""Targeting & Acquisition OS — compliant account targeting and outreach planning."""

from auto_client_acquisition.targeting_os.account_finder import explain_why_now, rank_accounts, recommend_accounts
from auto_client_acquisition.targeting_os.acquisition_scorecard import build_acquisition_scorecard
from auto_client_acquisition.targeting_os.buyer_role_mapper import map_buying_committee
from auto_client_acquisition.targeting_os.contactability_matrix import evaluate_contactability
from auto_client_acquisition.targeting_os.contact_source_policy import classify_source
from auto_client_acquisition.targeting_os.daily_autopilot import build_daily_targeting_brief
from auto_client_acquisition.targeting_os.free_diagnostic import build_free_growth_diagnostic
from auto_client_acquisition.targeting_os.linkedin_strategy import recommend_linkedin_strategy
from auto_client_acquisition.targeting_os.outreach_scheduler import build_outreach_plan, summarize_plan_ar
from auto_client_acquisition.targeting_os.reputation_guard import calculate_channel_reputation, should_pause_channel
from auto_client_acquisition.targeting_os.self_growth_mode import build_self_growth_daily_brief
from auto_client_acquisition.targeting_os.service_offers import list_targeting_services

__all__ = [
    "build_acquisition_scorecard",
    "build_daily_targeting_brief",
    "build_free_growth_diagnostic",
    "build_outreach_plan",
    "build_self_growth_daily_brief",
    "calculate_channel_reputation",
    "classify_source",
    "evaluate_contactability",
    "explain_why_now",
    "list_targeting_services",
    "map_buying_committee",
    "rank_accounts",
    "recommend_accounts",
    "recommend_linkedin_strategy",
    "should_pause_channel",
    "summarize_plan_ar",
]
