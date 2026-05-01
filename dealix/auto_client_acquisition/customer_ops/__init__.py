"""Customer Ops — onboarding + connector setup + support SLA + incidents.

Closes the gap between "great product" and "great customer experience":
  - onboarding_checklist: 8-step Pilot onboarding
  - connector_setup_status: per-connector readiness
  - support_ticket_router: P0–P3 categorization + routing
  - sla_tracker: time-to-first-response, MTTR, weekly health
  - customer_success_cadence: weekly check-in cadence + risk flags
  - incident_router: triage P0/P1 incidents with audit
"""

from __future__ import annotations

from .connector_setup_status import (
    SUPPORTED_CONNECTORS,
    build_connector_setup_summary,
    get_connector_status,
    update_connector_status,
)
from .customer_success_cadence import (
    CADENCE_TYPES,
    build_at_risk_alert,
    build_customer_success_plan,
    build_weekly_check_in,
)
from .incident_router import (
    INCIDENT_SEVERITIES,
    build_incident_response_plan,
    triage_incident,
)
from .onboarding_checklist import (
    ONBOARDING_STEPS,
    build_onboarding_checklist,
    update_onboarding_step,
)
from .sla_tracker import (
    SLA_TARGETS,
    build_sla_health_report,
    classify_sla_breach,
    record_sla_event,
)
from .support_ticket_router import (
    SUPPORT_PRIORITIES,
    build_first_response_template,
    classify_ticket_priority,
    route_ticket,
)

__all__ = [
    # connector_setup_status
    "SUPPORTED_CONNECTORS",
    "build_connector_setup_summary",
    "get_connector_status",
    "update_connector_status",
    # customer_success_cadence
    "CADENCE_TYPES",
    "build_at_risk_alert",
    "build_customer_success_plan",
    "build_weekly_check_in",
    # incident_router
    "INCIDENT_SEVERITIES",
    "build_incident_response_plan",
    "triage_incident",
    # onboarding_checklist
    "ONBOARDING_STEPS",
    "build_onboarding_checklist",
    "update_onboarding_step",
    # sla_tracker
    "SLA_TARGETS",
    "build_sla_health_report",
    "classify_sla_breach",
    "record_sla_event",
    # support_ticket_router
    "SUPPORT_PRIORITIES",
    "build_first_response_template",
    "classify_ticket_priority",
    "route_ticket",
]
