"""
Platform Services Layer — Dealix's Growth Control Tower spine.

Turns the platform from "WhatsApp Growth Operator" into a multi-channel
growth platform that ingests events from every channel a Saudi B2B uses,
converts them into Arabic action cards, evaluates each action against
policy, and produces unified proof.

Modules:
  - event_bus           : typed events from all channels
  - identity_resolution : reconcile phone+email+social→one person
  - channel_registry    : 11 supported channels with capabilities
  - action_policy       : decide approval / block / allow
  - tool_gateway        : draft-only proxy (no live actions here)
  - unified_inbox       : 8 card types from events
  - action_ledger       : auditable record of every action lifecycle
  - proof_ledger        : value rolled up across the platform
  - service_catalog     : 12 sellable services
"""

from auto_client_acquisition.platform_services.action_ledger import (
    ActionLedger,
    LedgerEntry,
)
from auto_client_acquisition.platform_services.action_policy import (
    POLICY_RULES,
    PolicyDecision,
    evaluate_action,
)
from auto_client_acquisition.platform_services.channel_registry import (
    ALL_CHANNELS,
    Channel,
    get_channel,
)
from auto_client_acquisition.platform_services.event_bus import (
    EVENT_TYPES,
    PlatformEvent,
    make_event,
)
from auto_client_acquisition.platform_services.identity_resolution import (
    Identity,
    resolve_identity,
)
from auto_client_acquisition.platform_services.proof_ledger import (
    PlatformProofLedger,
    build_demo_platform_proof,
)
from auto_client_acquisition.platform_services.service_catalog import (
    SELLABLE_SERVICES,
    ServiceOffering,
    list_services,
)
from auto_client_acquisition.platform_services.tool_gateway import (
    GatewayResult,
    invoke_tool,
)
from auto_client_acquisition.platform_services.unified_inbox import (
    CARD_TYPES,
    InboxCard,
    build_card_from_event,
    build_demo_feed,
)

__all__ = [
    "EVENT_TYPES", "PlatformEvent", "make_event",
    "Identity", "resolve_identity",
    "ALL_CHANNELS", "Channel", "get_channel",
    "POLICY_RULES", "PolicyDecision", "evaluate_action",
    "GatewayResult", "invoke_tool",
    "CARD_TYPES", "InboxCard", "build_card_from_event", "build_demo_feed",
    "ActionLedger", "LedgerEntry",
    "PlatformProofLedger", "build_demo_platform_proof",
    "SELLABLE_SERVICES", "ServiceOffering", "list_services",
]
