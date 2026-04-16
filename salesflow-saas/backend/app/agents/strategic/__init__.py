"""
Dealix Strategic Growth Agents — Layer 8 (Strategic Operations)
══════════════════════════════════════════════════════════════
10 autonomous agents that transform Dealix from a CRM into
an Autonomous Revenue & Strategic Growth OS.

Registration: called from agents/__init__.py via initialize_strategic_agents()
"""
from app.agents.strategic.partnership_scout import PartnershipScoutAgent
from app.agents.strategic.alliance_structuring import AllianceStructuringAgent
from app.agents.strategic.ma_screener import MATargetScreenerAgent
from app.agents.strategic.dd_analyst import DueDiligenceAnalystAgent
from app.agents.strategic.valuation_synergy import ValuationSynergyAgent
from app.agents.strategic.strategic_pmo import StrategicPMOAgent
from app.agents.strategic.expansion_playbook import ExpansionPlaybookAgent
from app.agents.strategic.executive_negotiator import ExecutiveNegotiatorAgent
from app.agents.strategic.post_merger import PostMergerIntegrationAgent
from app.agents.strategic.sovereign_growth import SovereignGrowthAgent


STRATEGIC_AGENTS = [
    PartnershipScoutAgent,
    AllianceStructuringAgent,
    MATargetScreenerAgent,
    DueDiligenceAnalystAgent,
    ValuationSynergyAgent,
    StrategicPMOAgent,
    ExpansionPlaybookAgent,
    ExecutiveNegotiatorAgent,
    PostMergerIntegrationAgent,
    SovereignGrowthAgent,
]


def initialize_strategic_agents(message_bus):
    """Instantiate and register all 10 strategic agents."""
    agents = []
    for AgentClass in STRATEGIC_AGENTS:
        agent = AgentClass()
        agent._message_bus = message_bus
        message_bus.register(agent)
        agents.append(agent)
    return agents
