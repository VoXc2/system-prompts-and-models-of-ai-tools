"""Revenue Company OS — multi-channel command feed + Revenue Work Units + self-improvement.

Sits above platform_services + intelligence_layer + service_tower:
  - event_to_card: any event → Arabic decision card
  - command_feed_engine: aggregate cards across channels for the day
  - action_graph: signal → action → outcome → proof
  - revenue_work_units: Dealix's unit of measurement (Salesforce-inspired)
  - channel_health: cross-channel reputation snapshot
  - opportunity_factory: turn signals into opportunity cards
  - service_factory: instantiate a service from a customer + intent
  - proof_ledger: revenue-tier proof aggregator (NOT platform_services.proof_ledger)
  - growth_memory: long-term cross-customer learning store
  - self_improvement_loop: weekly review + recommendations
"""

from __future__ import annotations

from .action_graph import (
    REVENUE_EDGE_TYPES,
    RevenueActionGraph,
    build_revenue_action_graph_demo,
)
from .channel_health import build_channel_health_snapshot
from .command_feed_engine import (
    build_command_feed_demo as revenue_os_command_feed_demo,
    build_command_feed_for_customer,
)
from .event_to_card import EVENT_TO_CARD_TYPES, build_card_from_event
from .growth_memory import GrowthMemory, build_growth_memory_demo
from .opportunity_factory import build_opportunity_factory_demo
from .proof_ledger import (
    RevenueProofLedger,
    build_revenue_proof_ledger_demo,
)
from .revenue_work_units import (
    REVENUE_WORK_UNIT_TYPES,
    aggregate_work_units,
    build_revenue_work_unit,
)
from .self_improvement_loop import build_weekly_self_improvement_report
from .service_factory import build_service_factory_demo, instantiate_service

__all__ = [
    # action_graph
    "REVENUE_EDGE_TYPES", "RevenueActionGraph",
    "build_revenue_action_graph_demo",
    # channel_health
    "build_channel_health_snapshot",
    # command_feed_engine
    "build_command_feed_for_customer",
    "revenue_os_command_feed_demo",
    # event_to_card
    "EVENT_TO_CARD_TYPES", "build_card_from_event",
    # growth_memory
    "GrowthMemory", "build_growth_memory_demo",
    # opportunity_factory
    "build_opportunity_factory_demo",
    # proof_ledger
    "RevenueProofLedger", "build_revenue_proof_ledger_demo",
    # revenue_work_units
    "REVENUE_WORK_UNIT_TYPES", "aggregate_work_units",
    "build_revenue_work_unit",
    # self_improvement_loop
    "build_weekly_self_improvement_report",
    # service_factory
    "build_service_factory_demo", "instantiate_service",
]
