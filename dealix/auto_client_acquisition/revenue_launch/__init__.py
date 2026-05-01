"""Revenue Launch — turn Dealix into actual paid pilots TODAY.

Scope:
  - offer_builder: build today's paid offers (499 Pilot, Growth OS Pilot, free case study)
  - pipeline_tracker: deterministic pipeline schema + add/update/summarize
  - outreach_sequence: build first-20 with day-by-day cadence
  - demo_closer: 12-min demo wrapper + close script + objection bank
  - pilot_delivery: 24-hour delivery template per service
  - proof_pack_template: client-facing summary
  - payment_manual_flow: Moyasar invoice/payment-link manual instructions
"""

from __future__ import annotations

from .demo_closer import (
    build_12_min_demo_flow as demo_12_min,
    build_close_script as demo_close_script,
    build_discovery_questions as demo_discovery,
    build_objection_responses as demo_objections,
)
from .offer_builder import (
    build_499_pilot_offer,
    build_case_study_free_offer,
    build_growth_os_pilot_offer,
    build_private_beta_offer,
    recommend_offer_for_segment,
)
from .payment_manual_flow import (
    build_moyasar_invoice_instructions,
    build_payment_confirmation_checklist,
    build_payment_link_message,
)
from .pilot_delivery import (
    build_24h_delivery_plan,
    build_client_intake_form,
    build_first_10_opportunities_delivery,
    build_growth_diagnostic_delivery,
    build_list_intelligence_delivery,
)
from .pipeline_tracker import (
    PIPELINE_STAGES,
    add_prospect,
    build_pipeline_schema,
    summarize_pipeline,
    update_stage,
)
from .proof_pack_template import (
    build_client_summary,
    build_next_step_recommendation,
    build_private_beta_proof_pack,
)
from .outreach_sequence import (
    build_first_20_segments_v2,
    build_followup_1,
    build_followup_2,
    build_outreach_message_v2,
    build_reply_handlers_v2,
)

__all__ = [
    # offer_builder
    "build_499_pilot_offer", "build_case_study_free_offer",
    "build_growth_os_pilot_offer", "build_private_beta_offer",
    "recommend_offer_for_segment",
    # pipeline_tracker
    "PIPELINE_STAGES", "add_prospect", "build_pipeline_schema",
    "summarize_pipeline", "update_stage",
    # outreach_sequence
    "build_first_20_segments_v2", "build_followup_1",
    "build_followup_2", "build_outreach_message_v2",
    "build_reply_handlers_v2",
    # demo_closer
    "demo_12_min", "demo_close_script", "demo_discovery", "demo_objections",
    # pilot_delivery
    "build_24h_delivery_plan", "build_client_intake_form",
    "build_first_10_opportunities_delivery",
    "build_growth_diagnostic_delivery",
    "build_list_intelligence_delivery",
    # proof_pack_template
    "build_client_summary", "build_next_step_recommendation",
    "build_private_beta_proof_pack",
    # payment_manual_flow
    "build_moyasar_invoice_instructions",
    "build_payment_confirmation_checklist",
    "build_payment_link_message",
]
