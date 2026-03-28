"""
Dealix AI Agent Background Tasks - Autonomous operations via Celery.
These tasks run 24/7 in the background discovering leads,
sending follow-ups, and qualifying prospects.
"""
from celery import shared_task
from datetime import datetime, timezone
import asyncio
import json


def run_async(coro):
    """Helper to run async functions in Celery tasks."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task(name="app.workers.ai_agent_tasks.discover_leads")
def discover_leads(tenant_id: str, industry: str, location: str = "الرياض", max_leads: int = 20):
    """
    Background task: Discover new leads using AI agents.
    Runs periodically to find new potential customers.
    """
    from app.services.lead_discovery import LeadDiscoveryAgent

    async def _discover():
        agent = LeadDiscoveryAgent(tenant_id, industry, location)
        leads = await agent.run_full_discovery(max_leads=max_leads)
        return leads

    leads = run_async(_discover())

    return {
        "task": "discover_leads",
        "tenant_id": tenant_id,
        "industry": industry,
        "location": location,
        "leads_found": len(leads),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@shared_task(name="app.workers.ai_agent_tasks.auto_qualify_leads")
def auto_qualify_leads(tenant_id: str, leads_data: list):
    """
    Background task: Automatically qualify and score leads using AI.
    """
    from app.services.ai_brain import ai_brain

    async def _qualify():
        results = []
        for lead in leads_data:
            qualification = await ai_brain.qualify_lead(lead)
            results.append({
                "lead_name": lead.get("name", ""),
                "score": qualification.get("score", 50),
                "status": qualification.get("status", "new"),
                "priority": qualification.get("priority", "medium"),
                "next_action": qualification.get("next_action", ""),
            })
        return results

    results = run_async(_qualify())

    return {
        "task": "auto_qualify_leads",
        "tenant_id": tenant_id,
        "leads_qualified": len(results),
        "results": results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@shared_task(name="app.workers.ai_agent_tasks.smart_followup")
def smart_followup(tenant_id: str, lead_data: dict, industry: str = "general", days_since: int = 3):
    """
    Background task: Send AI-generated follow-up message to a lead.
    """
    from app.services.auto_outreach import AutoOutreachEngine

    async def _followup():
        engine = AutoOutreachEngine(tenant_id, industry)
        result = await engine._warm_followup(lead_data, "whatsapp")
        return result

    result = run_async(_followup())

    return {
        "task": "smart_followup",
        "tenant_id": tenant_id,
        "lead_name": lead_data.get("name", ""),
        "success": result.get("success", False),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@shared_task(name="app.workers.ai_agent_tasks.run_outreach_campaign")
def run_outreach_campaign(tenant_id: str, campaign_config: dict):
    """
    Background task: Execute an outreach campaign.
    Sends messages to leads based on campaign configuration.
    """
    from app.services.auto_outreach import AutoOutreachEngine, OutreachScheduler

    # Only send during optimal hours
    if not OutreachScheduler.should_send_now():
        return {
            "task": "run_outreach_campaign",
            "status": "skipped",
            "reason": "Not optimal sending time",
            "next_optimal": OutreachScheduler.get_next_send_time().isoformat(),
        }

    async def _run():
        engine = AutoOutreachEngine(tenant_id, campaign_config.get("industry", "general"))
        leads = campaign_config.get("leads", [])
        result = await engine.launch_campaign(
            leads=leads,
            campaign_type=campaign_config.get("type", "cold_outreach"),
            channel=campaign_config.get("channel", "whatsapp"),
            sequence_length=campaign_config.get("sequence_length", 5),
        )
        return result

    result = run_async(_run())

    return {
        "task": "run_outreach_campaign",
        "tenant_id": tenant_id,
        "campaign_name": campaign_config.get("name", ""),
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@shared_task(name="app.workers.ai_agent_tasks.process_incoming_message")
def process_incoming_message(tenant_id: str, message: str, lead_data: dict, industry: str = "general"):
    """
    Background task: Process incoming WhatsApp message with AI.
    Generates smart reply and sends it automatically.
    """
    from app.services.auto_outreach import AutoOutreachEngine

    async def _process():
        engine = AutoOutreachEngine(tenant_id, industry)
        result = await engine.smart_reply(
            incoming_message=message,
            lead_data=lead_data,
        )
        return result

    result = run_async(_process())

    return {
        "task": "process_incoming_message",
        "tenant_id": tenant_id,
        "lead_name": lead_data.get("name", ""),
        "response_sent": result.get("sent", False),
        "should_escalate": result.get("should_escalate", False),
        "sentiment": result.get("sentiment", ""),
        "intent": result.get("intent", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@shared_task(name="app.workers.ai_agent_tasks.daily_ai_report")
def daily_ai_report(tenant_id: str):
    """
    Background task: Generate daily AI performance report.
    Summarizes all AI agent activities for the day.
    """
    from app.services.ai_brain import ai_brain

    async def _report():
        summary = await ai_brain.think(
            system_prompt="أنت محلل بيانات مبيعات. اكتب تقرير يومي موجز.",
            user_message=f"""اكتب تقرير يومي لنظام Dealix AI يتضمن:
- عدد الرسائل المرسلة اليوم
- عدد العملاء المكتشفين
- عدد المحادثات النشطة
- أهم الإنجازات
- توصيات للتحسين

التاريخ: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
""",
            temperature=0.5,
            max_tokens=500,
        )
        return summary

    report = run_async(_report())

    return {
        "task": "daily_ai_report",
        "tenant_id": tenant_id,
        "report": report,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
