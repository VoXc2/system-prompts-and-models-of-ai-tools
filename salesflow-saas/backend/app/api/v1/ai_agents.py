"""
AI Agents API - Manage AI sales agents, campaigns, and conversations.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.api.deps import get_current_user, get_db
from app.services.ai_brain import ai_brain
from app.services.smart_sales import SmartSalesAgent
from app.services.lead_discovery import LeadDiscoveryAgent, IndustryLeadFinder
from app.services.auto_outreach import AutoOutreachEngine, OutreachScheduler

router = APIRouter()


# ─── Schemas ───

class AgentCreateRequest(BaseModel):
    name: str
    agent_type: str = "sales"  # sales, discovery, support, qualifier
    industry: str = "general"
    auto_reply: bool = True
    auto_discover: bool = False
    auto_outreach: bool = False
    max_messages_per_day: int = 100

class ChatRequest(BaseModel):
    message: str
    lead_id: Optional[str] = None
    lead_name: Optional[str] = None
    lead_phone: Optional[str] = None
    lead_company: Optional[str] = None
    industry: str = "general"
    conversation_history: Optional[list] = None

class OutreachRequest(BaseModel):
    lead_name: str
    lead_phone: Optional[str] = None
    lead_business: Optional[str] = None
    industry: str = "general"
    message_type: str = "أول تواصل"
    channel: str = "whatsapp"

class DiscoveryRequest(BaseModel):
    industry: str
    location: str = "الرياض"
    max_leads: int = 20

class CampaignRequest(BaseModel):
    name: str
    campaign_type: str = "cold_outreach"
    industry: str = "general"
    channel: str = "whatsapp"
    sequence_length: int = 5
    target_criteria: Optional[dict] = None

class ObjectionRequest(BaseModel):
    objection: str
    industry: str = "general"
    product: str = ""

class QualifyRequest(BaseModel):
    lead_data: dict
    conversation: str = ""


# ─── Agent Management ───

@router.post("/agents")
async def create_agent(req: AgentCreateRequest):
    """Create a new AI sales agent."""
    return {
        "status": "success",
        "agent": {
            "name": req.name,
            "type": req.agent_type,
            "industry": req.industry,
            "auto_reply": req.auto_reply,
            "auto_discover": req.auto_discover,
            "auto_outreach": req.auto_outreach,
            "status": "active",
        },
        "message": f"تم إنشاء الوكيل الذكي '{req.name}' بنجاح",
    }


@router.get("/agents")
async def list_agents():
    """List all AI agents for the tenant."""
    return {
        "agents": [
            {
                "name": "ديليكس - وكيل المبيعات",
                "type": "sales",
                "status": "active",
                "auto_reply": True,
                "messages_today": 0,
                "total_messages": 0,
                "deals_closed": 0,
            }
        ]
    }


# ─── AI Chat (Smart Sales) ───

@router.post("/chat")
async def ai_chat(req: ChatRequest):
    """
    Chat with the AI sales agent. Send a customer message,
    get an intelligent sales response back.
    """
    agent = SmartSalesAgent(tenant_id="default", industry=req.industry)

    lead_data = {
        "name": req.lead_name or "عميل",
        "phone": req.lead_phone or "",
        "company_name": req.lead_company or "",
        "source": "api",
        "status": "new",
        "score": 50,
    }

    result = await agent.handle_incoming_message(
        message=req.message,
        lead_data=lead_data,
        conversation_history=req.conversation_history,
    )

    return {
        "response": result["response"],
        "sentiment": result["sentiment"],
        "intent": result["intent"],
        "urgency": result["urgency"],
        "action": result["action"],
        "should_escalate": result["should_escalate"],
        "score_change": result["score_change"],
    }


@router.post("/chat/reply")
async def ai_auto_reply(req: ChatRequest):
    """
    Process incoming WhatsApp message and auto-reply.
    This is what the webhook calls for automatic responses.
    """
    engine = AutoOutreachEngine(tenant_id="default", industry=req.industry)

    lead_data = {
        "name": req.lead_name or "عميل",
        "phone": req.lead_phone or "",
        "company_name": req.lead_company or "",
        "source": "whatsapp",
        "status": "contacted",
        "score": 50,
    }

    result = await engine.smart_reply(
        incoming_message=req.message,
        lead_data=lead_data,
        history=req.conversation_history,
    )

    return result


# ─── Lead Discovery ───

@router.post("/discover")
async def discover_leads(req: DiscoveryRequest):
    """
    Launch AI lead discovery agent.
    Searches Google Maps, social media, and directories.
    """
    agent = LeadDiscoveryAgent(
        tenant_id="default",
        industry=req.industry,
        location=req.location,
    )

    leads = await agent.run_full_discovery(max_leads=req.max_leads)

    return {
        "status": "success",
        "industry": req.industry,
        "location": req.location,
        "total_discovered": len(leads),
        "leads": leads,
        "message": f"تم اكتشاف {len(leads)} عميل محتمل في {req.location}",
    }


@router.get("/discover/keywords/{industry}")
async def get_industry_keywords(industry: str):
    """Get search keywords for an industry."""
    keywords = IndustryLeadFinder.get_keywords_for_industry(industry)
    return {"industry": industry, "keywords": keywords}


# ─── Auto-Outreach ───

@router.post("/outreach/message")
async def generate_outreach_message(req: OutreachRequest):
    """Generate a personalized outreach message for a lead."""
    agent = SmartSalesAgent(tenant_id="default", industry=req.industry)

    lead_data = {
        "name": req.lead_name,
        "phone": req.lead_phone or "",
        "company_name": req.lead_business or "",
        "city": "الرياض",
        "source": "manual",
    }

    message = await agent.generate_outreach_message(lead_data, req.message_type)

    return {
        "message": message,
        "lead_name": req.lead_name,
        "message_type": req.message_type,
        "channel": req.channel,
        "ready_to_send": bool(req.lead_phone),
    }


@router.post("/outreach/sequence")
async def create_outreach_sequence(req: OutreachRequest):
    """Create a complete automated sales sequence for a lead."""
    agent = SmartSalesAgent(tenant_id="default", industry=req.industry)

    lead_data = {
        "name": req.lead_name,
        "company_name": req.lead_business or "",
    }

    sequence = await agent.create_sales_sequence(lead_data, num_messages=5)

    return {
        "lead_name": req.lead_name,
        "sequence_length": len(sequence),
        "sequence": sequence,
        "message": f"تم إنشاء سلسلة مبيعات من {len(sequence)} رسائل لـ {req.lead_name}",
    }


@router.post("/outreach/campaign")
async def launch_campaign(req: CampaignRequest):
    """Launch an automated outreach campaign."""
    return {
        "status": "created",
        "campaign": {
            "name": req.name,
            "type": req.campaign_type,
            "industry": req.industry,
            "channel": req.channel,
            "sequence_length": req.sequence_length,
            "status": "ready",
        },
        "message": f"تم إنشاء حملة '{req.name}' - جاهزة للإطلاق",
        "next_optimal_send_time": OutreachScheduler.get_next_send_time().isoformat(),
    }


# ─── AI Tools ───

@router.post("/qualify")
async def qualify_lead(req: QualifyRequest):
    """AI-powered lead qualification and scoring."""
    result = await ai_brain.qualify_lead(req.lead_data, req.conversation)
    return {"qualification": result}


@router.post("/objection")
async def handle_objection(req: ObjectionRequest):
    """AI-powered objection handling."""
    result = await ai_brain.handle_objection(
        req.objection, req.industry, req.product
    )
    return {"handling": result}


@router.post("/analyze-sentiment")
async def analyze_sentiment(message: str):
    """Analyze customer message sentiment and intent."""
    result = await ai_brain.analyze_sentiment(message)
    return {"analysis": result}


@router.get("/stats")
async def agent_stats():
    """Get AI agent performance statistics."""
    return {
        "agents_active": 1,
        "total_conversations": 0,
        "total_messages_sent": 0,
        "total_leads_discovered": 0,
        "total_deals_from_ai": 0,
        "avg_response_time_seconds": 2.5,
        "customer_satisfaction": 0,
        "conversion_rate": 0,
        "best_performing_agent": "ديليكس - وكيل المبيعات",
        "is_sending_optimal": OutreachScheduler.should_send_now(),
        "next_optimal_time": OutreachScheduler.get_next_send_time().isoformat(),
    }
