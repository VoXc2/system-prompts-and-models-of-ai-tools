"""Unified conversation inbox API."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ConversationReply(BaseModel):
    message: str
    channel: Optional[str] = "whatsapp"


class ConversationCreate(BaseModel):
    contact_name: str
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    channel: str = "whatsapp"
    subject: Optional[str] = None
    initial_message: Optional[str] = None


@router.get("/")
async def list_conversations(
    status: Optional[str] = None,
    channel: Optional[str] = None,
    assigned_to: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    """List all conversations with filters."""
    return {
        "conversations": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "filters": {"status": status, "channel": channel, "assigned_to": assigned_to},
    }


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a conversation with its messages."""
    return {
        "conversation": {"id": conversation_id, "status": "open"},
        "messages": [],
    }


@router.post("/")
async def create_conversation(req: ConversationCreate):
    """Create a new conversation."""
    return {
        "status": "created",
        "conversation": {
            "contact_name": req.contact_name,
            "contact_phone": req.contact_phone,
            "channel": req.channel,
            "status": "open",
        },
    }


@router.post("/{conversation_id}/reply")
async def reply_to_conversation(conversation_id: str, req: ConversationReply):
    """Send a reply in a conversation (auto-routes to correct channel)."""
    return {
        "status": "sent",
        "conversation_id": conversation_id,
        "channel": req.channel,
        "message": req.message,
    }


@router.post("/{conversation_id}/assign")
async def assign_conversation(conversation_id: str, user_id: str):
    """Assign conversation to a team member."""
    return {
        "status": "assigned",
        "conversation_id": conversation_id,
        "assigned_to": user_id,
    }


@router.post("/{conversation_id}/close")
async def close_conversation(conversation_id: str):
    """Close/resolve a conversation."""
    return {
        "status": "closed",
        "conversation_id": conversation_id,
    }
