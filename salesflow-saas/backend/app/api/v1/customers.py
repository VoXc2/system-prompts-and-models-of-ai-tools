"""Customer management API — converted leads become customers."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.api.v1.deps import get_current_user, get_db
from app.models.customer import Customer

router = APIRouter()


class CustomerCreate(BaseModel):
    full_name: str
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    industry: Optional[str] = None
    notes: Optional[str] = None
    lead_id: Optional[UUID] = None


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    industry: Optional[str] = None
    notes: Optional[str] = None


@router.get("")
async def list_customers(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
    query = select(Customer).where(Customer.tenant_id == tenant_id)

    if search:
        query = query.where(
            Customer.full_name.ilike(f"%{search}%")
            | Customer.company.ilike(f"%{search}%")
            | Customer.phone.ilike(f"%{search}%")
        )

    total_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_q)).scalar() or 0

    query = query.order_by(Customer.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return {"items": [_serialize(c) for c in items], "total": total}


@router.post("", status_code=201)
async def create_customer(
    data: CustomerCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    customer = Customer(
        tenant_id=current_user["tenant_id"],
        full_name=data.full_name,
        company=data.company,
        email=data.email,
        phone=data.phone,
    )
    for field in ("city", "industry", "notes", "lead_id"):
        val = getattr(data, field, None)
        if val is not None and hasattr(customer, field):
            setattr(customer, field, val)
    db.add(customer)
    await db.flush()
    return _serialize(customer)


@router.get("/{customer_id}")
async def get_customer(
    customer_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    customer = await _get_or_404(db, current_user["tenant_id"], customer_id)
    return _serialize(customer)


@router.put("/{customer_id}")
async def update_customer(
    customer_id: UUID,
    data: CustomerUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    customer = await _get_or_404(db, current_user["tenant_id"], customer_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(customer, field, value)
    await db.flush()
    return _serialize(customer)


async def _get_or_404(db, tenant_id, customer_id):
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id, Customer.tenant_id == tenant_id)
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="العميل غير موجود")
    return customer


def _serialize(c):
    return {
        "id": str(c.id),
        "full_name": c.full_name,
        "company": getattr(c, "company", None),
        "email": getattr(c, "email", None),
        "phone": getattr(c, "phone", None),
        "city": getattr(c, "city", None),
        "industry": getattr(c, "industry", None),
        "notes": getattr(c, "notes", None),
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
