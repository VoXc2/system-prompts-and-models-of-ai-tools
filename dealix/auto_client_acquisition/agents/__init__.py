"""Phase 8 agents package."""

from auto_client_acquisition.agents.booking import BookingAgent
from auto_client_acquisition.agents.crm import CRMAgent
from auto_client_acquisition.agents.followup import FollowUpAgent
from auto_client_acquisition.agents.icp_matcher import ICP, FitScore, ICPMatcherAgent
from auto_client_acquisition.agents.intake import IntakeAgent, Lead, LeadSource, LeadStatus
from auto_client_acquisition.agents.outreach import OutreachAgent
from auto_client_acquisition.agents.pain_extractor import (
    ExtractionResult,
    PainExtractorAgent,
    PainPoint,
)
from auto_client_acquisition.agents.proposal import ProposalAgent
from auto_client_acquisition.agents.qualification import QualificationAgent

__all__ = [
    "ICP",
    "BookingAgent",
    "CRMAgent",
    "ExtractionResult",
    "FitScore",
    "FollowUpAgent",
    "ICPMatcherAgent",
    "IntakeAgent",
    "Lead",
    "LeadSource",
    "LeadStatus",
    "OutreachAgent",
    "PainExtractorAgent",
    "PainPoint",
    "ProposalAgent",
    "QualificationAgent",
]
