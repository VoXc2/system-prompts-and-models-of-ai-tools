"""Intelligence layer — deterministic JSON, optional bridge to innovation."""

from auto_client_acquisition.intelligence_layer.action_graph import build_action_graph_trace
from auto_client_acquisition.intelligence_layer.board_brief import build_board_brief
from auto_client_acquisition.intelligence_layer.competitive_moves import build_competitive_moves
from auto_client_acquisition.intelligence_layer.decision_memory import list_decisions, record_decision
from auto_client_acquisition.intelligence_layer.growth_brain import build_growth_profile
from auto_client_acquisition.intelligence_layer.intel_command_feed import build_intel_command_feed
from auto_client_acquisition.intelligence_layer.mission_engine import get_mission, list_mission_catalog
from auto_client_acquisition.intelligence_layer.opportunity_simulator import simulate_opportunities
from auto_client_acquisition.intelligence_layer.revenue_dna import build_revenue_dna
from auto_client_acquisition.intelligence_layer.trust_score import compute_trust_score

__all__ = [
    "build_action_graph_trace",
    "build_board_brief",
    "build_competitive_moves",
    "build_growth_profile",
    "build_intel_command_feed",
    "build_revenue_dna",
    "compute_trust_score",
    "get_mission",
    "list_decisions",
    "list_mission_catalog",
    "record_decision",
    "simulate_opportunities",
]
