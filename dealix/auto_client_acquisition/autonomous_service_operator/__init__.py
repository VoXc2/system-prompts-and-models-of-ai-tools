"""Autonomous Service Operator — البوت المركزي الذي يدير الخدمات.

Not a chatbot — a **service operator**: understands the customer's goal,
recommends a service, collects intake, runs workflow, requests approval,
delivers Proof Pack, suggests upgrade.
"""

from __future__ import annotations

from .agency_mode import (
    add_agency_client,
    build_agency_dashboard,
    build_co_branded_proof_pack,
    list_agency_revenue_share,
)
from .approval_manager import (
    APPROVAL_STATES,
    build_approval_card,
    process_approval_decision,
)
from .client_mode import (
    build_client_dashboard,
    build_client_session_summary,
)
from .self_growth_mode import (
    build_operator_self_growth_brief,
)
from .service_delivery_mode import (
    build_post_delivery_handoff,
    build_service_delivery_brief,
    build_sla_status_for_delivery,
)
from .conversation_router import (
    INTENT_TO_HANDLER,
    handle_message,
    route_message,
)
from .executive_mode import (
    build_ceo_command_center,
    build_executive_daily_brief,
    build_revenue_risks_summary,
)
from .intake_collector import (
    build_intake_questions_for_intent,
    parse_intake_payload,
    validate_intake_completeness,
)
from .intent_classifier import (
    SUPPORTED_INTENTS,
    classify_intent,
    intent_to_service,
)
from .operator_memory import (
    OperatorMemory,
    build_session_context,
)
from .proof_pack_dispatcher import (
    dispatch_proof_pack,
    proof_pack_for_service,
)
from .service_bundles import (
    BUNDLES,
    get_bundle,
    list_bundles,
    recommend_bundle,
)
from .service_orchestrator import (
    SERVICE_PIPELINE_STEPS,
    build_service_pipeline,
    run_service_step,
)
from .session_state import (
    SessionState,
    build_new_session,
    transition_session,
)
from .tool_action_planner import (
    plan_tool_action,
    review_planned_action,
)
from .upsell_engine import (
    build_upsell_card,
    recommend_upsell_after_service,
)
from .whatsapp_renderer import (
    render_approval_card_for_whatsapp,
    render_card_for_whatsapp,
    render_daily_brief_for_whatsapp,
)
from .workflow_runner import (
    advance_workflow,
    build_workflow_state,
    is_workflow_complete,
)

__all__ = [
    # conversation_router
    "INTENT_TO_HANDLER", "handle_message", "route_message",
    # intent_classifier
    "SUPPORTED_INTENTS", "classify_intent", "intent_to_service",
    # service_orchestrator
    "SERVICE_PIPELINE_STEPS", "build_service_pipeline", "run_service_step",
    # session_state
    "SessionState", "build_new_session", "transition_session",
    # intake_collector
    "build_intake_questions_for_intent", "parse_intake_payload",
    "validate_intake_completeness",
    # approval_manager
    "APPROVAL_STATES", "build_approval_card", "process_approval_decision",
    # workflow_runner
    "advance_workflow", "build_workflow_state", "is_workflow_complete",
    # tool_action_planner
    "plan_tool_action", "review_planned_action",
    # proof_pack_dispatcher
    "dispatch_proof_pack", "proof_pack_for_service",
    # upsell_engine
    "build_upsell_card", "recommend_upsell_after_service",
    # whatsapp_renderer
    "render_approval_card_for_whatsapp", "render_card_for_whatsapp",
    "render_daily_brief_for_whatsapp",
    # operator_memory
    "OperatorMemory", "build_session_context",
    # service_bundles
    "BUNDLES", "get_bundle", "list_bundles", "recommend_bundle",
    # executive_mode
    "build_ceo_command_center", "build_executive_daily_brief",
    "build_revenue_risks_summary",
    # client_mode
    "build_client_dashboard", "build_client_session_summary",
    # agency_mode
    "add_agency_client", "build_agency_dashboard",
    "build_co_branded_proof_pack", "list_agency_revenue_share",
    # self_growth_mode
    "build_operator_self_growth_brief",
    # service_delivery_mode
    "build_post_delivery_handoff",
    "build_service_delivery_brief",
    "build_sla_status_for_delivery",
]
