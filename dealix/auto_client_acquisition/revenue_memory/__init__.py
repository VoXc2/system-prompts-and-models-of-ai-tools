"""
Event-Sourced Revenue Memory.

Every meaningful action in Dealix is an immutable event written to the event
store. State is computed by replaying events into projections (timelines,
profiles, ledgers). This gives us:
  - Full audit trail (PDPL + customer-trust + debugging)
  - Ability to rebuild any view without losing history
  - Cross-customer learning without exposing PII (anonymized projections)
  - The defensive moat — every interaction strengthens the system

Public API:
    from auto_client_acquisition.revenue_memory import (
        RevenueEvent, EventStore, AccountTimeline,
        replay_for_account, append_event,
    )
"""

from auto_client_acquisition.revenue_memory.events import (
    EVENT_TYPES,
    RevenueEvent,
    make_event,
)
from auto_client_acquisition.revenue_memory.event_store import (
    EventStore,
    InMemoryEventStore,
    append_event,
)
from auto_client_acquisition.revenue_memory.projections import (
    AccountTimeline,
    AgentActionLedger,
    CampaignPerformanceProjection,
    ComplianceAuditProjection,
    CustomerROIProjection,
    DealHealthProjection,
)
from auto_client_acquisition.revenue_memory.replay import (
    replay_for_account,
    replay_for_customer,
)

__all__ = [
    "EVENT_TYPES",
    "RevenueEvent",
    "make_event",
    "EventStore",
    "InMemoryEventStore",
    "append_event",
    "AccountTimeline",
    "AgentActionLedger",
    "CampaignPerformanceProjection",
    "ComplianceAuditProjection",
    "CustomerROIProjection",
    "DealHealthProjection",
    "replay_for_account",
    "replay_for_customer",
]
