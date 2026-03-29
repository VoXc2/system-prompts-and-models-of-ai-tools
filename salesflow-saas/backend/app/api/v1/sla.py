from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from pydantic import BaseModel as Schema
from typing import Optional
from datetime import datetime
from app.api.v1.deps import get_current_user, get_db
from app.models.sla import SLAPolicy, SLABreach
from app.services.audit import log_action

router = APIRouter()


class SLAPolicyCreate(Schema):
    name: str
    name_ar: Optional[str] = None
    entity_type: str
    stage: Optional[str] = None
    priority: str = "normal"
    first_response_minutes: int = 60
    follow_up_minutes: int = 1440
    stage_max_minutes: Optional[int] = None
    resolution_minutes: Optional[int] = None
    escalation_enabled: bool = True
    escalation_to: Optional[UUID] = None
    escalation_notify_channels: Optional[list] = None
    business_hours_only: bool = True
    business_hours: Optional[dict] = None


class SLAPolicyUpdate(Schema):
    name: Optional[str] = None
    name_ar: Optional[str] = None
    stage: Optional[str] = None
    priority: Optional[str] = None
    first_response_minutes: Optional[int] = None
    follow_up_minutes: Optional[int] = None
    stage_max_minutes: Optional[int] = None
    resolution_minutes: Optional[int] = None
    escalation_enabled: Optional[bool] = None
    escalation_to: Optional[UUID] = None
    escalation_notify_channels: Optional[list] = None
    business_hours_only: Optional[bool] = None
    business_hours: Optional[dict] = None
    is_active: Optional[bool] = None


class SLAPolicyResponse(Schema):
    id: UUID
    tenant_id: UUID
    name: str
    name_ar: Optional[str]
    entity_type: str
    stage: Optional[str]
    priority: str
    first_response_minutes: int
    follow_up_minutes: int
    stage_max_minutes: Optional[int]
    resolution_minutes: Optional[int]
    escalation_enabled: bool
    escalation_to: Optional[UUID]
    escalation_notify_channels: Optional[list]
    business_hours_only: bool
    business_hours: Optional[dict]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class SLABreachResponse(Schema):
    id: UUID
    tenant_id: UUID
    policy_id: UUID
    entity_type: str
    entity_id: UUID
    assigned_to: Optional[UUID]
    breach_type: str
    breached_at: datetime
    resolved_at: Optional[datetime]
    exceeded_by_minutes: Optional[int]
    escalated: bool
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class SLAStatsResponse(Schema):
    total_policies: int
    active_breaches: int
    resolved_today: int
    avg_breach_minutes: Optional[float]
    breach_by_type: dict


@router.get("/policies", response_model=list[SLAPolicyResponse])
async def list_sla_policies(
    entity_type: str = Query(None),
    is_active: bool = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(SLAPolicy).where(SLAPolicy.tenant_id == current_user["tenant_id"])
    if entity_type:
        query = query.where(SLAPolicy.entity_type == entity_type)
    if is_active is not None:
        query = query.where(SLAPolicy.is_active == is_active)

    query = query.order_by(SLAPolicy.entity_type, SLAPolicy.priority)
    result = await db.execute(query)
    return [SLAPolicyResponse.model_validate(p) for p in result.scalars().all()]


@router.post("/policies", response_model=SLAPolicyResponse, status_code=201)
async def create_sla_policy(
    data: SLAPolicyCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user["role"] not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Only admins can manage SLA policies")

    policy = SLAPolicy(tenant_id=current_user["tenant_id"], **data.model_dump(exclude_none=True))
    db.add(policy)
    await db.flush()
    await db.refresh(policy)
    await log_action(db, current_user["tenant_id"], current_user["user_id"], "create", "sla_policy", str(policy.id))
    return SLAPolicyResponse.model_validate(policy)


@router.put("/policies/{policy_id}", response_model=SLAPolicyResponse)
async def update_sla_policy(
    policy_id: UUID,
    data: SLAPolicyUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user["role"] not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Only admins can manage SLA policies")

    result = await db.execute(
        select(SLAPolicy).where(SLAPolicy.id == policy_id, SLAPolicy.tenant_id == current_user["tenant_id"])
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="SLA policy not found")

    changes = data.model_dump(exclude_none=True)
    for field, value in changes.items():
        setattr(policy, field, value)

    await db.flush()
    await db.refresh(policy)
    await log_action(db, current_user["tenant_id"], current_user["user_id"], "update", "sla_policy", str(policy.id), changes=changes)
    return SLAPolicyResponse.model_validate(policy)


@router.get("/breaches", response_model=list[SLABreachResponse])
async def list_sla_breaches(
    entity_type: str = Query(None),
    breach_type: str = Query(None),
    resolved: bool = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(SLABreach).where(SLABreach.tenant_id == current_user["tenant_id"])
    if entity_type:
        query = query.where(SLABreach.entity_type == entity_type)
    if breach_type:
        query = query.where(SLABreach.breach_type == breach_type)
    if resolved is not None:
        if resolved:
            query = query.where(SLABreach.resolved_at.isnot(None))
        else:
            query = query.where(SLABreach.resolved_at.is_(None))

    query = query.order_by(SLABreach.breached_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return [SLABreachResponse.model_validate(b) for b in result.scalars().all()]


@router.get("/stats", response_model=SLAStatsResponse)
async def get_sla_stats(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]

    total_policies = (await db.execute(
        select(func.count()).select_from(SLAPolicy).where(SLAPolicy.tenant_id == tenant_id, SLAPolicy.is_active == True)
    )).scalar() or 0

    active_breaches = (await db.execute(
        select(func.count()).select_from(SLABreach).where(
            SLABreach.tenant_id == tenant_id, SLABreach.resolved_at.is_(None)
        )
    )).scalar() or 0

    from datetime import date, timedelta, timezone as tz
    today_start = datetime.now(tz.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_today = (await db.execute(
        select(func.count()).select_from(SLABreach).where(
            SLABreach.tenant_id == tenant_id, SLABreach.resolved_at >= today_start
        )
    )).scalar() or 0

    avg_breach = (await db.execute(
        select(func.avg(SLABreach.exceeded_by_minutes)).where(
            SLABreach.tenant_id == tenant_id, SLABreach.exceeded_by_minutes.isnot(None)
        )
    )).scalar()

    # Breach counts by type
    type_counts = (await db.execute(
        select(SLABreach.breach_type, func.count()).where(
            SLABreach.tenant_id == tenant_id, SLABreach.resolved_at.is_(None)
        ).group_by(SLABreach.breach_type)
    )).all()

    return SLAStatsResponse(
        total_policies=total_policies,
        active_breaches=active_breaches,
        resolved_today=resolved_today,
        avg_breach_minutes=float(avg_breach) if avg_breach else None,
        breach_by_type={t: c for t, c in type_counts},
    )
