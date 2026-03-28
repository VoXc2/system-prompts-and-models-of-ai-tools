"""Voice AI API endpoints."""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.services.voice_ai import VoiceAIService
from app.services.appointment_service import AppointmentService

logger = logging.getLogger(__name__)
router = APIRouter()


class OutboundCallRequest(BaseModel):
    phone_number: str
    assistant_id: Optional[str] = None
    voice_profile: str = "khalid"


class AssistantCreateRequest(BaseModel):
    name: str = "Dealix Voice Agent"
    industry: str = "general"
    voice_profile: str = "khalid"


# ─── Voice Profiles ───

@router.get("/profiles")
async def list_voice_profiles():
    """List available Saudi voice profiles (Khalid, Noura)."""
    service = VoiceAIService(tenant_id="default")
    profiles = service.get_voice_profiles()
    return {"profiles": profiles}


@router.get("/profiles/{profile_id}")
async def get_voice_profile(profile_id: str):
    """Get details for a specific voice profile."""
    service = VoiceAIService(tenant_id="default")
    profiles = service.get_voice_profiles()
    for p in profiles:
        if p["id"] == profile_id:
            return {"profile": p}
    return {"status": "error", "detail": f"الملف الصوتي '{profile_id}' غير موجود"}


# ─── Assistants ───

@router.post("/assistants")
async def create_voice_assistant(
    req: AssistantCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a new Voice AI assistant with a Saudi voice profile."""
    service = VoiceAIService(tenant_id=current_user["tenant_id"])
    result = await service.create_assistant(req.name, req.industry, voice_profile=req.voice_profile)
    return {"status": "created", "assistant": result}


@router.post("/call")
async def make_outbound_call(
    req: OutboundCallRequest,
    current_user: dict = Depends(get_current_user),
):
    """Initiate an outbound Voice AI call with selected Saudi voice profile."""
    service = VoiceAIService(tenant_id=current_user["tenant_id"])
    result = await service.make_outbound_call(
        req.phone_number, req.assistant_id, voice_profile=req.voice_profile
    )
    return {"status": "initiated", "call": result}


@router.post("/webhook")
async def voice_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Process incoming Voice AI webhook events (Vapi/Retell).

    If the webhook returns a book_appointment action, persist it to DB.
    """
    body = await request.json()

    # Extract tenant_id from webhook metadata or default
    tenant_id = body.get("message", {}).get("metadata", {}).get("tenant_id", "default")
    service = VoiceAIService(tenant_id=tenant_id)
    result = await service.process_call_webhook(body)

    # If voice agent requested a booking, persist to appointments table
    if isinstance(result, dict) and result.get("action") == "book_appointment":
        try:
            apt_svc = AppointmentService(db, tenant_id)
            preferred_time = result.get("preferred_time")

            # Parse time or default to next business hour
            if preferred_time:
                try:
                    start_time = datetime.fromisoformat(preferred_time)
                except (ValueError, TypeError):
                    start_time = datetime.now(timezone.utc)
            else:
                start_time = datetime.now(timezone.utc)

            appointment = await apt_svc.book(
                start_time=start_time,
                service_type=result.get("service_type", "demo"),
                contact_name=result.get("customer_name"),
                contact_phone=result.get("phone"),
                notes=result.get("notes"),
                booked_via="voice_ai",
            )
            result["appointment_id"] = str(appointment.id)
            result["appointment_status"] = appointment.status
            logger.info("Voice AI booking persisted: appointment %s", appointment.id)
        except Exception as e:
            logger.error("Failed to persist voice booking: %s", e)
            result["booking_error"] = str(e)

    return result


@router.get("/calls")
async def list_calls(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
):
    """List recent Voice AI calls."""
    service = VoiceAIService(tenant_id=current_user["tenant_id"])
    calls = await service.get_call_history(limit)
    return {"calls": calls, "total": len(calls)}


@router.get("/calls/{call_id}")
async def get_call(
    call_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get call details with transcript."""
    return {"call": {"id": call_id}, "transcript": None}


@router.post("/calls/{call_id}/summarize")
async def summarize_call(
    call_id: str,
    transcript: str,
    current_user: dict = Depends(get_current_user),
):
    """AI-generate a summary for a call."""
    service = VoiceAIService(tenant_id=current_user["tenant_id"])
    summary = await service.generate_call_summary(transcript)
    return {"call_id": call_id, "summary": summary}
