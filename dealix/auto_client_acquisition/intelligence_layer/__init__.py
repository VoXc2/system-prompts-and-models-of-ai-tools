"""
Intelligence Layer — the decision brain on top of platform_services.

Turns Dealix from "channels + actions" into a **Growth Neural Network**:
the system understands the customer fully, watches the market, decides,
executes (with approval), and learns from every outcome.

Modules:
  - growth_brain         : per-customer brain (context + preferences + priorities)
  - command_feed         : Arabic decision cards (what to do now)
  - action_graph         : signal→action→outcome typed relationships
  - mission_engine       : 7 outcome-shaped missions (durable workflows)
  - decision_memory      : learns from Accept/Skip/Edit signals
  - trust_score          : per-action safety verdict (safe/review/blocked)
  - revenue_dna          : best-channel/segment/angle/objection per customer
  - opportunity_simulator: forward simulation before sending
  - competitive_moves    : detect + respond to competitor signals
  - board_brief          : weekly founder/board-ready brief
"""

from auto_client_acquisition.intelligence_layer.action_graph import (
    ActionEdge,
    ActionGraph,
    EDGE_TYPES,
)
from auto_client_acquisition.intelligence_layer.board_brief import build_board_brief
from auto_client_acquisition.intelligence_layer.command_feed import (
    INTEL_CARD_TYPES,
    build_command_feed_demo,
)
from auto_client_acquisition.intelligence_layer.competitive_moves import (
    analyze_competitive_move,
)
from auto_client_acquisition.intelligence_layer.decision_memory import (
    DecisionMemory,
    learn_from_decision,
)
from auto_client_acquisition.intelligence_layer.growth_brain import (
    GrowthBrain,
    build_growth_brain,
)
from auto_client_acquisition.intelligence_layer.mission_engine import (
    INTEL_MISSIONS,
    list_intel_missions,
    recommend_missions,
)
from auto_client_acquisition.intelligence_layer.opportunity_simulator import (
    simulate_opportunity,
)
from auto_client_acquisition.intelligence_layer.revenue_dna import (
    build_revenue_dna_demo,
    extract_revenue_dna,
)
from auto_client_acquisition.intelligence_layer.trust_score import compute_trust_score

__all__ = [
    "GrowthBrain", "build_growth_brain",
    "INTEL_CARD_TYPES", "build_command_feed_demo",
    "ActionGraph", "ActionEdge", "EDGE_TYPES",
    "INTEL_MISSIONS", "list_intel_missions", "recommend_missions",
    "DecisionMemory", "learn_from_decision",
    "compute_trust_score",
    "extract_revenue_dna", "build_revenue_dna_demo",
    "simulate_opportunity",
    "analyze_competitive_move",
    "build_board_brief",
]
