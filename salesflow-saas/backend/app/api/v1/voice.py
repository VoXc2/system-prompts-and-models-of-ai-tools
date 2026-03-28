"""Voice AI API endpoints."""
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from app.services.voice_ai import VoiceAIService

router = APIRouter()


class OutboundCallRequest(BaseModel):
    phone_number: str
    assistant_id: Optional[str] = None


class AssistantCreateRequest(BaseModel):
    name: str = "Dealix Voice Agent"
    industry: str = "general"


@router.post("/assistants")
async def create_voice_assistant(req: AssistantCreateRequest):
    """Create a new Voice AI assistant."""
    service = VoiceAIService(tenant_id="default")
    result = await service.create_assistant(req.name, req.industry)
    return {"status": "created", "assistant": result}


@router.post("/call")
async def make_outbound_call(req: OutboundCallRequest):
    """Initiate an outbound Voice AI call."""
    service = VoiceAIService(tenant_id="default")
    result = await service.make_outbound_call(req.phone_number, req.assistant_id)
    return {"status": "initiated", "call": result}


@router.post("/webhook")
async def voice_webhook(request: Request):
    """Process incoming Voice AI webhook events (Vapi/Retell)."""
    body = await request.json()
    service = VoiceAIService(tenant_id="default")
    result = await service.process_call_webhook(body)
    return result


@router.get("/calls")
async def list_calls(limit: int = 50):
    """List recent Voice AI calls."""
    service = VoiceAIService(tenant_id="default")
    calls = await service.get_call_history(limit)
    return {"calls": calls, "total": len(calls)}


@router.get("/calls/{call_id}")
async def get_call(call_id: str):
    """Get call details with transcript."""
    return {"call": {"id": call_id}, "transcript": None}


@router.post("/calls/{call_id}/summarize")
async def summarize_call(call_id: str, transcript: str):
    """AI-generate a summary for a call."""
    service = VoiceAIService(tenant_id="default")
    summary = await service.generate_call_summary(transcript)
    return {"call_id": call_id, "summary": summary}
