"""Proposal / pitch deck management API - إدارة العروض التقديمية."""
from datetime import datetime, date, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.proposal import Proposal
from app.models.deal import Deal
from app.models.lead import Lead

router = APIRouter()


# ---------------------------------------------------------------------------
# Enums & labels
# ---------------------------------------------------------------------------

class ProposalStatus(str, Enum):
    draft = "draft"
    sent = "sent"
    viewed = "viewed"
    accepted = "accepted"
    rejected = "rejected"


STATUS_LABELS = {
    "draft": "مسودة",
    "sent": "مرسل",
    "viewed": "تم الاطلاع",
    "accepted": "مقبول",
    "rejected": "مرفوض",
}

VALID_STATUSES = set(STATUS_LABELS.keys())


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ProposalCreate(BaseModel):
    deal_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    title: str = Field(..., min_length=1, max_length=255)
    content: dict = Field(default_factory=dict)
    total_amount: Optional[float] = None
    currency: str = "SAR"
    valid_until: Optional[date] = None
    auto_generate: bool = False
    industry: Optional[str] = None
    services_list: Optional[list[str]] = None


class ProposalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[dict] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    valid_until: Optional[date] = None


class ProposalGenerateRequest(BaseModel):
    deal_id: Optional[UUID] = None
    lead_id: Optional[UUID] = None
    industry: str = "general"
    services_list: list[str] = Field(default_factory=list)
    custom_instructions: Optional[str] = None


class ProposalResponse(BaseModel):
    id: str
    tenant_id: str
    deal_id: Optional[str] = None
    lead_id: Optional[str] = None
    title: str
    content: dict
    total_amount: Optional[float] = None
    currency: str = "SAR"
    status: str
    status_label: str = ""
    valid_until: Optional[str] = None
    sent_at: Optional[str] = None
    viewed_at: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, obj: Proposal) -> "ProposalResponse":
        return cls(
            id=str(obj.id),
            tenant_id=str(obj.tenant_id),
            deal_id=str(obj.deal_id) if obj.deal_id else None,
            lead_id=str(obj.lead_id) if obj.lead_id else None,
            title=obj.title or "",
            content=obj.content or {},
            total_amount=float(obj.total_amount) if obj.total_amount is not None else None,
            currency=obj.currency or "SAR",
            status=obj.status or "draft",
            status_label=STATUS_LABELS.get(obj.status or "draft", obj.status or ""),
            valid_until=obj.valid_until.isoformat() if obj.valid_until else None,
            sent_at=obj.sent_at.isoformat() if obj.sent_at else None,
            viewed_at=obj.viewed_at.isoformat() if obj.viewed_at else None,
            created_at=obj.created_at.isoformat() if obj.created_at else "",
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_proposal_or_404(
    db: AsyncSession, proposal_id: UUID, tenant_id: str,
) -> Proposal:
    result = await db.execute(
        select(Proposal).where(
            Proposal.id == proposal_id,
            Proposal.tenant_id == tenant_id,
        )
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=404, detail="العرض غير موجود")
    return proposal


async def _get_lead_data(db: AsyncSession, lead_id: UUID, tenant_id: str) -> dict:
    """Fetch lead data as a dict for AI generation."""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        return {}
    return {
        "name": lead.name,
        "phone": lead.phone,
        "email": lead.email,
        "source": lead.source,
        "status": lead.status,
        "notes": lead.notes,
        "extra_data": lead.extra_data or {},
    }


async def _get_deal_data(db: AsyncSession, deal_id: UUID, tenant_id: str) -> dict:
    """Fetch deal data as a dict for AI generation."""
    result = await db.execute(
        select(Deal).where(Deal.id == deal_id, Deal.tenant_id == tenant_id)
    )
    deal = result.scalar_one_or_none()
    if not deal:
        return {}
    return {
        "title": getattr(deal, "title", None) or getattr(deal, "name", ""),
        "value": float(deal.value) if deal.value else None,
        "stage": deal.stage,
        "notes": getattr(deal, "notes", None) or "",
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", status_code=201)
async def create_proposal(
    data: ProposalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """إنشاء عرض جديد — Create a new proposal, optionally AI-generated."""
    tenant_id = current_user["tenant_id"]
    content = data.content

    # Optionally generate content with AI
    if data.auto_generate:
        from app.services.proposal_generator import ProposalGenerator

        generator = ProposalGenerator()
        lead_data = {}
        deal_data = {}

        if data.lead_id:
            lead_data = await _get_lead_data(db, data.lead_id, tenant_id)
        if data.deal_id:
            deal_data = await _get_deal_data(db, data.deal_id, tenant_id)

        content = await generator.generate_proposal_content(
            lead_data=lead_data,
            deal_data=deal_data,
            industry=data.industry or "general",
            services_list=data.services_list or [],
        )

    proposal = Proposal(
        tenant_id=tenant_id,
        deal_id=data.deal_id,
        lead_id=data.lead_id,
        title=data.title,
        content=content,
        total_amount=data.total_amount,
        currency=data.currency,
        status="draft",
        valid_until=data.valid_until,
    )
    db.add(proposal)
    await db.commit()
    await db.refresh(proposal)

    return {
        "status": "created",
        "message": "تم إنشاء العرض بنجاح",
        "proposal": ProposalResponse.from_orm_model(proposal),
    }


@router.post("/generate")
async def generate_proposal(
    data: ProposalGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """توليد محتوى عرض بالذكاء الاصطناعي — AI-generate proposal content."""
    from app.services.proposal_generator import ProposalGenerator

    tenant_id = current_user["tenant_id"]
    generator = ProposalGenerator()

    lead_data = {}
    deal_data = {}

    if data.lead_id:
        lead_data = await _get_lead_data(db, data.lead_id, tenant_id)
        if not lead_data:
            raise HTTPException(status_code=404, detail="العميل المحتمل غير موجود")
    if data.deal_id:
        deal_data = await _get_deal_data(db, data.deal_id, tenant_id)
        if not deal_data:
            raise HTTPException(status_code=404, detail="الصفقة غير موجودة")

    try:
        content = await generator.generate_proposal_content(
            lead_data=lead_data,
            deal_data=deal_data,
            industry=data.industry,
            services_list=data.services_list,
            custom_instructions=data.custom_instructions,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"فشل في توليد المحتوى بالذكاء الاصطناعي: {str(exc)}",
        )

    return {
        "status": "generated",
        "message": "تم توليد محتوى العرض بنجاح",
        "content": content,
    }


@router.get("")
async def list_proposals(
    status: Optional[ProposalStatus] = Query(None, description="تصفية حسب الحالة"),
    lead_id: Optional[UUID] = Query(None, description="تصفية حسب العميل المحتمل"),
    deal_id: Optional[UUID] = Query(None, description="تصفية حسب الصفقة"),
    page: int = Query(1, ge=1, description="رقم الصفحة"),
    page_size: int = Query(20, ge=1, le=100, description="حجم الصفحة"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """عرض جميع العروض — List proposals with filters and pagination."""
    tenant_id = current_user["tenant_id"]

    base = select(Proposal).where(Proposal.tenant_id == tenant_id)
    if status:
        base = base.where(Proposal.status == status.value)
    if lead_id:
        base = base.where(Proposal.lead_id == lead_id)
    if deal_id:
        base = base.where(Proposal.deal_id == deal_id)

    # Total count
    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # Paginated results
    offset = (page - 1) * page_size
    stmt = base.order_by(Proposal.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    proposals = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "label": "العروض",
        "proposals": [ProposalResponse.from_orm_model(p) for p in proposals],
    }


@router.get("/{proposal_id}")
async def get_proposal(
    proposal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """عرض تفاصيل العرض — Get a single proposal."""
    tenant_id = current_user["tenant_id"]
    proposal = await _get_proposal_or_404(db, proposal_id, tenant_id)
    return {"proposal": ProposalResponse.from_orm_model(proposal)}


@router.put("/{proposal_id}")
async def update_proposal(
    proposal_id: UUID,
    data: ProposalUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """تعديل العرض — Update an existing proposal (only drafts can be edited)."""
    tenant_id = current_user["tenant_id"]
    proposal = await _get_proposal_or_404(db, proposal_id, tenant_id)

    if proposal.status not in ("draft",):
        raise HTTPException(
            status_code=400,
            detail="لا يمكن تعديل عرض تم إرساله بالفعل",
        )

    updated_fields = data.model_dump(exclude_none=True)
    if not updated_fields:
        raise HTTPException(status_code=400, detail="لا توجد حقول للتحديث")

    for field, value in updated_fields.items():
        setattr(proposal, field, value)

    await db.commit()
    await db.refresh(proposal)

    return {
        "status": "updated",
        "message": "تم تحديث العرض بنجاح",
        "updated_fields": list(updated_fields.keys()),
        "proposal": ProposalResponse.from_orm_model(proposal),
    }


@router.post("/{proposal_id}/send")
async def send_proposal(
    proposal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """إرسال العرض — Mark proposal as sent and record timestamp."""
    tenant_id = current_user["tenant_id"]
    proposal = await _get_proposal_or_404(db, proposal_id, tenant_id)

    if proposal.status not in ("draft",):
        raise HTTPException(
            status_code=400,
            detail="العرض تم إرساله مسبقاً أو في حالة لا تسمح بالإرسال",
        )

    view_token = uuid4().hex[:16]
    view_url = f"https://app.dealix.sa/proposals/view/{view_token}"

    proposal.status = "sent"
    proposal.sent_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(proposal)

    return {
        "status": "sent",
        "message": "تم إرسال العرض بنجاح",
        "view_url": view_url,
        "proposal": ProposalResponse.from_orm_model(proposal),
    }


@router.get("/{proposal_id}/view")
async def view_proposal_public(
    proposal_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """رابط عرض عام — Public view link (no auth). Updates viewed_at on first view."""
    result = await db.execute(
        select(Proposal).where(Proposal.id == proposal_id)
    )
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=404, detail="العرض غير موجود")

    if proposal.status == "draft":
        raise HTTPException(status_code=403, detail="العرض لم يتم إرساله بعد")

    # Record first view
    if proposal.viewed_at is None:
        proposal.viewed_at = datetime.now(timezone.utc)
        if proposal.status == "sent":
            proposal.status = "viewed"
        await db.commit()
        await db.refresh(proposal)

    return {
        "proposal": {
            "id": str(proposal.id),
            "title": proposal.title or "",
            "content": proposal.content or {},
            "total_amount": float(proposal.total_amount) if proposal.total_amount is not None else None,
            "currency": proposal.currency or "SAR",
            "status": proposal.status,
            "status_label": STATUS_LABELS.get(proposal.status, ""),
            "valid_until": proposal.valid_until.isoformat() if proposal.valid_until else None,
        },
    }


@router.post("/{proposal_id}/accept")
async def accept_proposal(
    proposal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """قبول العرض — Mark proposal as accepted."""
    tenant_id = current_user["tenant_id"]
    proposal = await _get_proposal_or_404(db, proposal_id, tenant_id)

    if proposal.status in ("accepted", "rejected"):
        raise HTTPException(
            status_code=400,
            detail=f"العرض في حالة '{STATUS_LABELS.get(proposal.status, proposal.status)}' ولا يمكن تغييره",
        )

    proposal.status = "accepted"
    await db.commit()
    await db.refresh(proposal)

    return {
        "status": "accepted",
        "message": "تم قبول العرض بنجاح",
        "proposal": ProposalResponse.from_orm_model(proposal),
    }


@router.post("/{proposal_id}/reject")
async def reject_proposal(
    proposal_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """رفض العرض — Mark proposal as rejected."""
    tenant_id = current_user["tenant_id"]
    proposal = await _get_proposal_or_404(db, proposal_id, tenant_id)

    if proposal.status in ("accepted", "rejected"):
        raise HTTPException(
            status_code=400,
            detail=f"العرض في حالة '{STATUS_LABELS.get(proposal.status, proposal.status)}' ولا يمكن تغييره",
        )

    proposal.status = "rejected"
    await db.commit()
    await db.refresh(proposal)

    return {
        "status": "rejected",
        "message": "تم رفض العرض",
        "proposal": ProposalResponse.from_orm_model(proposal),
    }
