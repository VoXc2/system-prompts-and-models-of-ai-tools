"""Customer operations: onboarding, SLA, connectors, incidents (deterministic stubs)."""

from auto_client_acquisition.customer_ops.onboarding_checklist import build_onboarding_checklist
from auto_client_acquisition.customer_ops.sla_tracker import build_sla_summary

__all__ = ["build_onboarding_checklist", "build_sla_summary"]
