"""Unified conversation inbox API."""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, ConversationMessage


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ConversationCreate(BaseModel):
    contact_name: str
    contact_phone: str | None = None
    contact_email: str | None = None
    channel: str = "whatsapp"
    subject: str | None = None
    initial_message: str | None = None
    lead_id: UUID | None = None
    customer_id: UUID | None = None


class ConversationReply(BaseModel):
    message: str
    channel: str | None = None
    content_type: str = "text"
    sender_type: str = "user"
    direction: str = "outbound"


class AssignRequest(BaseModel):
    user_id: UUID


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_type: str
    sender_id: UUID | None
    channel: str | None
    direction: str
    content_type: str | None
    content: str | None
    status: str | None
    external_id: str | None
    extra_data: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    lead_id: UUID | None
    customer_id: UUID | None
    assigned_to: UUID | None
    channel: str
    status: str | None
    subject: str | None
    contact_name: str | None
    contact_phone: str | None
    contact_email: str | None
    messages_count: int | None
    unread_count: int | None
    last_message_at: datetime | None
    last_message_preview: str | None
    sentiment: str | None
    ai_summary: str | None
    tags: list | None
    is_ai_managed: bool | None
    extra_data: dict | None
    updated_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetailResponse(BaseModel):
    conversation: ConversationResponse
    messages: list[MessageResponse]


class ConversationListResponse(BaseModel):
    items: list[ConversationResponse]
    total: int
    page: int
    per_page: int


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter()


async def _get_conversation_or_404(
    db: AsyncSession, conversation_id: UUID, tenant_id: UUID,
) -> Conversation:
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    status: str | None = Query(None),
    channel: str | None = Query(None),
    assigned_to: UUID | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all conversations with optional filters, ordered by last_message_at desc."""
    query = select(Conversation).where(Conversation.tenant_id == current_user.tenant_id)

    if status:
        query = query.where(Conversation.status == status)
    if channel:
        query = query.where(Conversation.channel == channel)
    if assigned_to:
        query = query.where(Conversation.assigned_to == assigned_to)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = (
        query
        .order_by(Conversation.last_message_at.desc().nullslast())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(query)
    conversations = result.scalars().all()

    return ConversationListResponse(
        items=[ConversationResponse.model_validate(c) for c in conversations],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a conversation with its messages (eager loaded)."""
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == current_user.tenant_id,
        )
        .options(selectinload(Conversation.messages))
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationDetailResponse(
        conversation=ConversationResponse.model_validate(conv),
        messages=[MessageResponse.model_validate(m) for m in conv.messages],
    )


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    req: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new conversation, optionally with an initial message."""
    now = datetime.now(timezone.utc)

    conv = Conversation(
        tenant_id=current_user.tenant_id,
        contact_name=req.contact_name,
        contact_phone=req.contact_phone,
        contact_email=req.contact_email,
        channel=req.channel,
        subject=req.subject,
        lead_id=req.lead_id,
        customer_id=req.customer_id,
        status="open",
        messages_count=0,
        unread_count=0,
        last_message_at=now if req.initial_message else None,
        last_message_preview=req.initial_message[:500] if req.initial_message else None,
        updated_at=now,
    )
    db.add(conv)
    await db.flush()

    if req.initial_message:
        msg = ConversationMessage(
            tenant_id=current_user.tenant_id,
            conversation_id=conv.id,
            sender_type="user",
            sender_id=current_user.id,
            channel=req.channel,
            direction="outbound",
            content_type="text",
            content=req.initial_message,
            status="sent",
        )
        db.add(msg)
        conv.messages_count = 1
        await db.flush()

    await db.refresh(conv)
    return ConversationResponse.model_validate(conv)


@router.post("/{conversation_id}/reply", response_model=MessageResponse)
async def reply_to_conversation(
    conversation_id: UUID,
    req: ConversationReply,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a reply in a conversation. Updates conversation metadata."""
    conv = await _get_conversation_or_404(db, conversation_id, current_user.tenant_id)
    now = datetime.now(timezone.utc)

    msg = ConversationMessage(
        tenant_id=current_user.tenant_id,
        conversation_id=conv.id,
        sender_type=req.sender_type,
        sender_id=current_user.id,
        channel=req.channel or conv.channel,
        direction=req.direction,
        content_type=req.content_type,
        content=req.message,
        status="sent",
    )
    db.add(msg)

    conv.messages_count = (conv.messages_count or 0) + 1
    conv.last_message_at = now
    conv.last_message_preview = req.message[:500] if req.message else None
    conv.updated_at = now

    await db.flush()
    await db.refresh(msg)
    return MessageResponse.model_validate(msg)


@router.post("/{conversation_id}/assign", response_model=ConversationResponse)
async def assign_conversation(
    conversation_id: UUID,
    req: AssignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Assign conversation to a team member."""
    conv = await _get_conversation_or_404(db, conversation_id, current_user.tenant_id)

    conv.assigned_to = req.user_id
    conv.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(conv)
    return ConversationResponse.model_validate(conv)


@router.post("/{conversation_id}/close", response_model=ConversationResponse)
async def close_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Close/resolve a conversation."""
    conv = await _get_conversation_or_404(db, conversation_id, current_user.tenant_id)

    conv.status = "closed"
    conv.updated_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(conv)
    return ConversationResponse.model_validate(conv)
