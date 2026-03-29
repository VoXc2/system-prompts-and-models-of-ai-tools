from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel as Schema
from decimal import Decimal
from typing import Optional
from datetime import datetime
from app.api.v1.deps import get_current_user, get_db
from app.models.playbook import Playbook
from app.services.audit import log_action

router = APIRouter()


class PlaybookCreate(Schema):
    name: str
    name_ar: Optional[str] = None
    industry: str
    product_type: str
    tier: str = "A"
    description: Optional[str] = None
    description_ar: Optional[str] = None
    setup_fee: Decimal = Decimal("0")
    monthly_fee: Decimal = Decimal("0")
    performance_percentage: Decimal = Decimal("0")
    currency: str = "SAR"
    target_persona: Optional[dict] = None
    outreach_sequence: Optional[list] = None
    qualification_criteria: Optional[dict] = None
    content_templates: Optional[list] = None
    kpi_targets: Optional[dict] = None
    sales_cycle_days: int = 30
    custom_stages: Optional[list] = None


class PlaybookUpdate(Schema):
    name: Optional[str] = None
    name_ar: Optional[str] = None
    industry: Optional[str] = None
    product_type: Optional[str] = None
    tier: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    setup_fee: Optional[Decimal] = None
    monthly_fee: Optional[Decimal] = None
    performance_percentage: Optional[Decimal] = None
    target_persona: Optional[dict] = None
    outreach_sequence: Optional[list] = None
    qualification_criteria: Optional[dict] = None
    content_templates: Optional[list] = None
    kpi_targets: Optional[dict] = None
    sales_cycle_days: Optional[int] = None
    custom_stages: Optional[list] = None
    is_active: Optional[bool] = None


class PlaybookResponse(Schema):
    id: UUID
    tenant_id: UUID
    name: str
    name_ar: Optional[str]
    industry: str
    product_type: str
    tier: str
    description: Optional[str]
    description_ar: Optional[str]
    setup_fee: Optional[Decimal]
    monthly_fee: Optional[Decimal]
    performance_percentage: Optional[Decimal]
    currency: str
    target_persona: Optional[dict]
    outreach_sequence: Optional[list]
    qualification_criteria: Optional[dict]
    content_templates: Optional[list]
    kpi_targets: Optional[dict]
    sales_cycle_days: Optional[int]
    custom_stages: Optional[list]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


@router.get("", response_model=list[PlaybookResponse])
async def list_playbooks(
    industry: str = Query(None),
    product_type: str = Query(None),
    is_active: bool = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Playbook).where(Playbook.tenant_id == current_user["tenant_id"])
    if industry:
        query = query.where(Playbook.industry == industry)
    if product_type:
        query = query.where(Playbook.product_type == product_type)
    if is_active is not None:
        query = query.where(Playbook.is_active == is_active)

    query = query.order_by(Playbook.industry, Playbook.product_type)
    result = await db.execute(query)
    return [PlaybookResponse.model_validate(p) for p in result.scalars().all()]


@router.post("", response_model=PlaybookResponse, status_code=201)
async def create_playbook(
    data: PlaybookCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user["role"] not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Only admins can manage playbooks")

    playbook = Playbook(tenant_id=current_user["tenant_id"], **data.model_dump(exclude_none=True))
    db.add(playbook)
    await db.flush()
    await db.refresh(playbook)
    await log_action(db, current_user["tenant_id"], current_user["user_id"], "create", "playbook", str(playbook.id))
    return PlaybookResponse.model_validate(playbook)


@router.get("/{playbook_id}", response_model=PlaybookResponse)
async def get_playbook(
    playbook_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Playbook).where(Playbook.id == playbook_id, Playbook.tenant_id == current_user["tenant_id"])
    )
    playbook = result.scalar_one_or_none()
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    return PlaybookResponse.model_validate(playbook)


@router.put("/{playbook_id}", response_model=PlaybookResponse)
async def update_playbook(
    playbook_id: UUID,
    data: PlaybookUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user["role"] not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Only admins can manage playbooks")

    result = await db.execute(
        select(Playbook).where(Playbook.id == playbook_id, Playbook.tenant_id == current_user["tenant_id"])
    )
    playbook = result.scalar_one_or_none()
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")

    changes = data.model_dump(exclude_none=True)
    for field, value in changes.items():
        setattr(playbook, field, value)

    await db.flush()
    await db.refresh(playbook)
    await log_action(db, current_user["tenant_id"], current_user["user_id"], "update", "playbook", str(playbook.id), changes=changes)
    return PlaybookResponse.model_validate(playbook)


@router.delete("/{playbook_id}", status_code=204)
async def delete_playbook(
    playbook_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user["role"] not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Only admins can manage playbooks")

    result = await db.execute(
        select(Playbook).where(Playbook.id == playbook_id, Playbook.tenant_id == current_user["tenant_id"])
    )
    playbook = result.scalar_one_or_none()
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")

    await db.delete(playbook)
    await db.flush()
    await log_action(db, current_user["tenant_id"], current_user["user_id"], "delete", "playbook", str(playbook_id))
