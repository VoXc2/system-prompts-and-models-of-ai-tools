"""Full OS API — unified deal lifecycle orchestration.

Single endpoint processes any event (inbound message, reply, booking,
payment) and returns: next stage, actions to take, response message,
and whether human approval is needed.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/os", tags=["Full OS"])


class ProcessEventRequest(BaseModel):
    lead_id: str = ""
    phone: str = ""
    email: str = ""
    company: str = ""
    sector: str = ""
    source: str = "whatsapp_inbound"
    message: str = ""
    current_stage: str = "new_lead"
    event_type: str = "inbound_message"


class BulkProcessRequest(BaseModel):
    events: List[ProcessEventRequest]


@router.post("/process")
async def process_event(req: ProcessEventRequest) -> Dict[str, Any]:
    """Process a single event through the deal lifecycle state machine.

    Returns: new_stage, actions, response_message_ar, human_approval_required.
    If auto_send_allowed=True, the response can be sent automatically.
    If human_approval_required=True, create a draft for Sami to review.
    """
    from app.services.full_os_orchestrator import orchestrator, OrchestratorEvent

    event = OrchestratorEvent(
        lead_id=req.lead_id,
        phone=req.phone,
        email=req.email,
        company=req.company,
        sector=req.sector,
        source=req.source,
        message=req.message,
        current_stage=req.current_stage,
        event_type=req.event_type,
    )
    return orchestrator.process_event(event)


@router.post("/process-and-act")
async def process_and_act(req: ProcessEventRequest) -> Dict[str, Any]:
    """Process event AND execute the first safe action.

    If auto_send_allowed: sends WhatsApp response via Ultramsg.
    If human_approval_required: creates a draft for review.
    Always logs the activity.
    """
    from app.services.full_os_orchestrator import orchestrator, OrchestratorEvent

    event = OrchestratorEvent(
        lead_id=req.lead_id,
        phone=req.phone,
        email=req.email,
        company=req.company,
        sector=req.sector,
        source=req.source,
        message=req.message,
        current_stage=req.current_stage,
        event_type=req.event_type,
    )
    result = orchestrator.process_event(event)

    execution = {"action_taken": "none", "send_result": None, "draft_created": False}

    if result.get("auto_send_allowed") and result.get("response_message_ar") and req.phone:
        if "send_whatsapp" in result.get("actions", []):
            try:
                from app.services.whatsapp_multi_provider import send_whatsapp_smart
                send_result = await send_whatsapp_smart(req.phone, result["response_message_ar"])
                execution = {
                    "action_taken": "whatsapp_sent",
                    "send_result": send_result,
                    "draft_created": False,
                }
            except Exception as exc:
                execution = {
                    "action_taken": "whatsapp_failed",
                    "error": str(exc)[:200],
                    "draft_created": False,
                }

    elif result.get("human_approval_required") and result.get("response_message_ar"):
        try:
            from app.models.outreach_draft import OutreachDraft
            from app.database import async_session
            async with async_session() as session:
                draft = OutreachDraft(
                    batch_id=f"os_{result['lead_id']}",
                    company=req.company,
                    contact_phone=req.phone,
                    contact_email=req.email,
                    channel="whatsapp" if req.phone else "email",
                    subject=f"[{result['new_stage']}] {req.company}",
                    body=result["response_message_ar"],
                    sector=req.sector,
                    status="draft",
                    approval_required=True,
                    source="full_os_orchestrator",
                )
                session.add(draft)
                await session.commit()
                execution = {
                    "action_taken": "draft_created",
                    "draft_id": str(draft.id),
                    "draft_created": True,
                }
        except Exception:
            execution = {"action_taken": "draft_failed", "draft_created": False}

    return {**result, "execution": execution}


@router.post("/bulk-process")
async def bulk_process(req: BulkProcessRequest) -> Dict[str, Any]:
    """Process multiple events at once (for batch imports)."""
    from app.services.full_os_orchestrator import orchestrator, OrchestratorEvent

    results = []
    for event_req in req.events:
        event = OrchestratorEvent(
            lead_id=event_req.lead_id,
            phone=event_req.phone,
            email=event_req.email,
            company=event_req.company,
            sector=event_req.sector,
            source=event_req.source,
            message=event_req.message,
            current_stage=event_req.current_stage,
            event_type=event_req.event_type,
        )
        results.append(orchestrator.process_event(event))

    return {
        "processed": len(results),
        "results": results,
    }


@router.get("/whatsapp-providers")
async def whatsapp_provider_status() -> Dict[str, Any]:
    """Check which WhatsApp providers are configured."""
    from app.services.whatsapp_multi_provider import check_providers
    return await check_providers()


@router.post("/test-send")
async def test_whatsapp_send(phone: str, message: str = "اختبار Dealix — النظام شغّال 🚀") -> Dict[str, Any]:
    """Test WhatsApp send via all configured providers."""
    from app.services.whatsapp_multi_provider import send_whatsapp_smart
    return await send_whatsapp_smart(phone, message)


@router.get("/stages")
async def list_stages() -> Dict[str, Any]:
    """List all deal lifecycle stages with their possible transitions."""
    from app.services.full_os_orchestrator import STAGE_TRANSITIONS, STAGE_AUTO_ACTIONS, STAGE_MESSAGES_AR

    stages = {}
    for stage, transitions in STAGE_TRANSITIONS.items():
        stages[stage.value] = {
            "transitions": {k: v.value for k, v in transitions.items()},
            "auto_actions": [a.value for a in STAGE_AUTO_ACTIONS.get(stage, [])],
            "message_template": STAGE_MESSAGES_AR.get(stage, ""),
        }
    return {"stages": stages, "total": len(stages)}
