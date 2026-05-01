"""Conversation router — single entry point for any operator message."""

from __future__ import annotations

from typing import Any

from .approval_manager import (
    build_approval_card,
    process_approval_decision,
)
from .intake_collector import build_intake_questions_for_intent
from .intent_classifier import classify_intent, intent_to_service
from .service_bundles import recommend_bundle
from .service_orchestrator import build_service_pipeline


# Map: intent → handler name
INTENT_TO_HANDLER: dict[str, str] = {
    "want_more_customers": "start_first_10_opportunities",
    "has_contact_list": "start_list_intelligence",
    "want_partnerships": "start_partner_sprint",
    "want_daily_growth": "start_growth_os",
    "want_meetings": "start_meeting_sprint",
    "want_email_rescue": "start_email_rescue",
    "want_whatsapp_setup": "start_whatsapp_compliance",
    "ask_pricing": "show_pricing",
    "approve_action": "process_approval",
    "edit_action": "process_edit",
    "skip_action": "process_skip",
    "ask_demo": "send_demo",
    "ask_proof": "send_proof_pack",
    "ask_services": "show_bundles",
    "ask_partnership": "show_agency_partner",
    "ask_revenue_today": "show_revenue_today_plan",
}


def route_message(message: str) -> dict[str, Any]:
    """Classify a message + return the routed handler + recommended service."""
    classification = classify_intent(message)
    intent = classification["intent"]
    handler = INTENT_TO_HANDLER.get(intent, "show_bundles")
    service_id = intent_to_service(intent)

    return {
        "message": (message or "")[:300],
        "classification": classification,
        "intent": intent,
        "handler": handler,
        "recommended_service_id": service_id,
    }


def handle_message(
    message: str,
    *,
    customer_id: str | None = None,
    has_contact_list: bool = False,
    is_agency: bool = False,
    is_local_business: bool = False,
    budget_sar: int = 1000,
) -> dict[str, Any]:
    """
    Full single-shot handler — classifies + plans + returns operator response.

    Never executes any external action. Just plans + drafts.
    """
    routed = route_message(message)
    intent = routed["intent"]
    handler = routed["handler"]

    # Recommend a bundle (high-level package).
    bundle_rec = recommend_bundle(
        intent=intent,
        has_contact_list=has_contact_list,
        is_agency=is_agency,
        is_local_business=is_local_business,
        budget_sar=budget_sar,
    )

    # If a service is recommended, build its initial pipeline + intake form.
    response: dict[str, Any] = {
        "intent": intent,
        "handler": handler,
        "bundle_recommendation": bundle_rec,
        "service_id": routed["recommended_service_id"],
        "approval_required": True,
        "live_send_allowed": False,
    }

    if intent in ("approve_action", "edit_action", "skip_action"):
        # Approvals are handled separately — surface a placeholder card.
        decision = (
            "approve" if intent == "approve_action"
            else "edit" if intent == "edit_action"
            else "skip"
        )
        sample_card = build_approval_card(
            action_type="example_action",
            title_ar="فعل مثال",
            summary_ar="هذا مثال على approval card",
        )
        response["decision_processed"] = process_approval_decision(
            sample_card, decision=decision, decided_by=customer_id or "user",
        )
        return response

    if routed["recommended_service_id"]:
        response["intake_questions"] = build_intake_questions_for_intent(intent)
        response["initial_pipeline"] = build_service_pipeline(
            routed["recommended_service_id"], customer_id=customer_id or "",
        )

    return response
