"""Dealix GTM Intelligence API Routes — all dry-run safe, no real sending."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/gtm", tags=["GTM Intelligence"])

class CompanyRequest(BaseModel):
    company_name: str
    sector: str = ""
    city: str = ""
    email: str = ""
    website: str = ""

class ComplianceRequest(BaseModel):
    channel: str
    action: str = "send_message"

class ReplyRequest(BaseModel):
    reply_text: str

class ApprovalRequest(BaseModel):
    target_company: str
    action: str
    approved: bool = False

class OutcomeRequest(BaseModel):
    target_company: str
    outcome: str
    channel: str = ""
    notes: str = ""

@router.post("/company-intelligence")
async def company_intelligence(req: CompanyRequest):
    from dealix_gtm_os.agents.supervisor_agent import SupervisorAgent
    s = SupervisorAgent()
    return await s.run({"name": req.company_name, "sector": req.sector, "city": req.city, "email": req.email})

@router.post("/score-target")
async def score_target(req: CompanyRequest):
    from dealix_gtm_os.scoring.scoring_engine import score_target
    return score_target(req.company_name, req.sector, bool(req.email)).model_dump()

@router.post("/generate-outreach-pack")
async def generate_outreach_pack(req: CompanyRequest):
    from dealix_gtm_os.agents.supervisor_agent import SupervisorAgent
    s = SupervisorAgent()
    result = await s.run({"name": req.company_name, "sector": req.sector, "city": req.city, "email": req.email})
    return {"company": req.company_name, "message": result.get("message"), "channel_plan": result.get("channel_plan"), "compliance": result.get("compliance"), "proof_pack": result.get("proof_pack"), "approval_required": result.get("approval_required", True), "trace_id": result.get("trace_id")}

@router.post("/compliance-check")
async def compliance_check(req: ComplianceRequest):
    from dealix_gtm_os.compliance.compliance_engine import check_compliance
    return check_compliance(req.channel, req.action)

@router.post("/classify-reply")
async def classify_reply(req: ReplyRequest):
    from dealix_gtm_os.agents.negotiation_agent import NegotiationAgent
    n = NegotiationAgent()
    return await n.run({"objection": req.reply_text})

@router.post("/next-action")
async def next_action(req: CompanyRequest):
    from dealix_gtm_os.agents.supervisor_agent import SupervisorAgent
    s = SupervisorAgent()
    result = await s.run({"name": req.company_name, "sector": req.sector, "city": req.city})
    return {"company": req.company_name, "next_action": result.get("next_action"), "approval_required": result.get("approval_required"), "channel": result.get("channel_plan", {}).get("primary_channel")}

@router.post("/generate-daily-command-pack")
async def daily_command_pack(req: CompanyRequest):
    from dealix_gtm_os.agents.supervisor_agent import SupervisorAgent
    s = SupervisorAgent()
    result = await s.run({"name": req.company_name or "Daily Pack Target", "sector": req.sector or "agency", "city": req.city or "الرياض"})
    return {"pack_type": "daily", "target": result.get("company"), "score": result.get("score"), "message": result.get("message"), "channel": result.get("channel_plan"), "compliance": result.get("compliance"), "trace_id": result.get("trace_id"), "no_real_send": True}

@router.get("/targets")
async def list_targets():
    return {"targets": [], "note": "Connect to database for persistent targets. Currently uses file-based targets in FIRST_20_TARGETS.md"}

@router.get("/approvals")
async def list_approvals():
    from dealix_gtm_os.governance.approval_queue import get_pending
    return {"pending": get_pending()}

@router.post("/approve-action")
async def approve_action(req: ApprovalRequest):
    from dealix_gtm_os.governance.approval_queue import approve, reject
    if req.approved:
        return approve(req.target_company, req.action)
    return reject(req.target_company, req.action)

@router.post("/log-outcome")
async def log_outcome(req: OutcomeRequest):
    from dealix_gtm_os.governance.audit_log import log_entry
    return log_entry(req.target_company, req.outcome, req.channel, req.notes)
