"""طبقة ابتكار deterministic للعرض والـ API — بدون شبكة أو LLM."""

from auto_client_acquisition.innovation.command_feed import build_demo_command_feed
from auto_client_acquisition.innovation.deal_rooms import analyze_deal_room
from auto_client_acquisition.innovation.experiments import recommend_experiments
from auto_client_acquisition.innovation.growth_missions import list_growth_missions
from auto_client_acquisition.innovation.proof_ledger import build_demo_proof_ledger

__all__ = [
    "analyze_deal_room",
    "build_demo_command_feed",
    "build_demo_proof_ledger",
    "list_growth_missions",
    "recommend_experiments",
]
