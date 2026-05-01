"""
Arabic Growth Operator — Dealix's customer-facing growth-execution layer.

This package bundles the building blocks for the operator experience:
  - client_profile       : Saudi B2B Growth Profile per customer
  - contact_importer     : safe upload + normalize + classify uploaded numbers
  - contactability       : per-contact "can we contact?" decision
  - targeting            : segmenting + ranking + Top-10 with Why-Now stub
  - message_planner      : Arabic drafts + follow-ups + objection responses
  - partnership_planner  : partner suggestions + outreach drafts + scorecard
  - meeting_planner      : agenda + calendar draft + post-meeting follow-up
  - payment_offer        : Moyasar payment-link draft (no charge)
  - proof_pack           : weekly evidence pack with revenue + risk metrics
  - mission_planner      : Growth Missions (10-in-10, recover-stalled, etc.)

DESIGN INVARIANTS
  - draft-only by default; nothing is sent / charged / scheduled live
  - every outbound has approval_required=True
  - PDPL: no cold WhatsApp without lawful basis; uploads classified safely
  - deterministic: same input → same output (testable without external APIs)
"""

from auto_client_acquisition.growth_operator.client_profile import (
    ClientGrowthProfile,
    build_demo_profile,
    profile_from_dict,
)
from auto_client_acquisition.growth_operator.contact_importer import (
    classify_contact_source,
    dedupe_contacts,
    detect_opt_out,
    normalize_phone,
    summarize_import,
)
from auto_client_acquisition.growth_operator.contactability import (
    CONTACTABILITY_LABELS,
    contactability_summary,
    score_contactability,
)
from auto_client_acquisition.growth_operator.message_planner import (
    draft_arabic_message,
    draft_followup,
    draft_objection_response,
)
from auto_client_acquisition.growth_operator.meeting_planner import (
    build_calendar_draft,
    build_meeting_agenda,
    build_post_meeting_followup,
)
from auto_client_acquisition.growth_operator.mission_planner import (
    GROWTH_MISSIONS,
    list_missions,
    run_mission,
)
from auto_client_acquisition.growth_operator.partnership_planner import (
    draft_partner_outreach,
    partner_scorecard,
    suggest_partner_types,
)
from auto_client_acquisition.growth_operator.payment_offer import (
    build_moyasar_payment_link_draft,
    sar_to_halalas,
)
from auto_client_acquisition.growth_operator.proof_pack import (
    build_weekly_proof_pack,
)
from auto_client_acquisition.growth_operator.targeting import (
    rank_targets,
    recommend_top_10,
    segment_contacts,
    why_now_stub,
)

__all__ = [
    # client_profile
    "ClientGrowthProfile", "build_demo_profile", "profile_from_dict",
    # contact_importer
    "normalize_phone", "dedupe_contacts", "classify_contact_source",
    "detect_opt_out", "summarize_import",
    # contactability
    "CONTACTABILITY_LABELS", "score_contactability", "contactability_summary",
    # targeting
    "segment_contacts", "rank_targets", "recommend_top_10", "why_now_stub",
    # message_planner
    "draft_arabic_message", "draft_followup", "draft_objection_response",
    # partnership_planner
    "suggest_partner_types", "draft_partner_outreach", "partner_scorecard",
    # meeting_planner
    "build_meeting_agenda", "build_calendar_draft", "build_post_meeting_followup",
    # payment_offer
    "build_moyasar_payment_link_draft", "sar_to_halalas",
    # proof_pack
    "build_weekly_proof_pack",
    # mission_planner
    "GROWTH_MISSIONS", "list_missions", "run_mission",
]
