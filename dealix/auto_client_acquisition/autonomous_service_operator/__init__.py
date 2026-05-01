"""Autonomous Service Operator — intent to service, approval-first, deterministic MVP."""

from auto_client_acquisition.autonomous_service_operator.conversation_router import handle_message
from auto_client_acquisition.autonomous_service_operator.service_bundles import get_bundle, list_bundles

__all__ = ["handle_message", "list_bundles", "get_bundle"]
