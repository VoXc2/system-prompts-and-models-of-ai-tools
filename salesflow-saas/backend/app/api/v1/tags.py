"""Tags and segments API for leads, deals, and contacts."""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Any

from app.api.v1.deps import get_current_user, get_db
from app.models.tag import Tag, Segment

router = APIRouter()


# --------------- Schemas ---------------

class TagCreate(BaseModel):
    name: str
    color: str = "#6366F1"
    entity_type: str  # lead | deal | contact


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    entity_type: Optional[str] = None


class TagResponse(BaseModel):
    id: str
    name: str
    color: str
    entity_type: str
    tenant_id: str
    created_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, obj: Tag) -> "TagResponse":
        return cls(
            id=str(obj.id),
            name=obj.name,
            color=obj.color or "#6B7280",
            entity_type=obj.entity_type or "",
            tenant_id=str(obj.tenant_id),
            created_at=obj.created_at.isoformat() if obj.created_at else "",
        )


class SegmentCreate(BaseModel):
    name: str
    filters: dict[str, Any]
    description: Optional[str] = None


class SegmentResponse(BaseModel):
    id: str
    name: str
    filters: dict[str, Any]
    description: Optional[str]
    tenant_id: str
    member_count: int
    created_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, obj: Segment) -> "SegmentResponse":
        return cls(
            id=str(obj.id),
            name=obj.name,
            filters=obj.filters or {},
            description=obj.description,
            tenant_id=str(obj.tenant_id),
            member_count=obj.member_count or 0,
            created_at=obj.created_at.isoformat() if obj.created_at else "",
        )


# --------------- Tag Endpoints ---------------

@router.post("/tags", response_model=TagResponse, status_code=201)
async def create_tag(
    data: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new tag."""
    tenant_id = current_user["tenant_id"]

    if data.entity_type not in ("lead", "deal", "contact"):
        raise HTTPException(status_code=400, detail="entity_type يجب أن يكون lead أو deal أو contact")

    tag = Tag(
        tenant_id=tenant_id,
        name=data.name,
        color=data.color,
        entity_type=data.entity_type,
    )
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return TagResponse.from_orm_model(tag)


@router.get("/tags", response_model=list[TagResponse])
async def list_tags(
    entity_type: Optional[str] = Query(None, description="Filter by entity type: lead, deal, contact"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all tags, optionally filtered by entity_type."""
    tenant_id = current_user["tenant_id"]
    stmt = select(Tag).where(Tag.tenant_id == tenant_id)
    if entity_type:
        stmt = stmt.where(Tag.entity_type == entity_type)
    result = await db.execute(stmt)
    tags = result.scalars().all()
    return [TagResponse.from_orm_model(t) for t in tags]


@router.put("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: str,
    data: TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update an existing tag."""
    tenant_id = current_user["tenant_id"]
    result = await db.execute(
        select(Tag).where(Tag.id == UUID(tag_id), Tag.tenant_id == tenant_id)
    )
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="التاق غير موجود")

    updates = data.model_dump(exclude_none=True)
    if "entity_type" in updates and updates["entity_type"] not in ("lead", "deal", "contact"):
        raise HTTPException(status_code=400, detail="entity_type يجب أن يكون lead أو deal أو contact")

    for field, value in updates.items():
        setattr(tag, field, value)

    await db.commit()
    await db.refresh(tag)
    return TagResponse.from_orm_model(tag)


@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a tag."""
    tenant_id = current_user["tenant_id"]
    result = await db.execute(
        select(Tag).where(Tag.id == UUID(tag_id), Tag.tenant_id == tenant_id)
    )
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="التاق غير موجود")

    await db.delete(tag)
    await db.commit()


# --------------- Segment Endpoints ---------------

@router.post("/segments", response_model=SegmentResponse, status_code=201)
async def create_segment(
    data: SegmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new segment with filter criteria."""
    tenant_id = current_user["tenant_id"]

    segment = Segment(
        tenant_id=tenant_id,
        name=data.name,
        filters=data.filters,
        description=data.description,
        member_count=0,
    )
    db.add(segment)
    await db.commit()
    await db.refresh(segment)
    return SegmentResponse.from_orm_model(segment)


@router.get("/segments", response_model=list[SegmentResponse])
async def list_segments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all segments for the tenant."""
    tenant_id = current_user["tenant_id"]
    result = await db.execute(
        select(Segment).where(Segment.tenant_id == tenant_id)
    )
    segments = result.scalars().all()
    return [SegmentResponse.from_orm_model(s) for s in segments]


@router.get("/segments/{segment_id}", response_model=SegmentResponse)
async def get_segment(
    segment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a single segment by ID."""
    tenant_id = current_user["tenant_id"]
    result = await db.execute(
        select(Segment).where(Segment.id == UUID(segment_id), Segment.tenant_id == tenant_id)
    )
    segment = result.scalar_one_or_none()
    if not segment:
        raise HTTPException(status_code=404, detail="الشريحة غير موجودة")
    return SegmentResponse.from_orm_model(segment)
