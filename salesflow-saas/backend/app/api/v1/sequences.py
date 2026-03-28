"""Sales sequences - automated multi-step follow-up workflows for Dealix CRM."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.sequence import Sequence, SequenceStep, SequenceEnrollment

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class SequenceStepCreate(BaseModel):
    step_order: int
    step_type: str  # send_whatsapp | send_email | create_task | update_status | wait | ai_reply
    delay_days: int = 0
    delay_hours: int = 0
    channel: Optional[str] = None  # whatsapp, email, sms
    template_name: Optional[str] = None
    message_content: Optional[str] = None
    ai_generated: bool = False
    settings: Optional[dict] = None


class SequenceStepResponse(BaseModel):
    id: str
    sequence_id: str
    step_order: int
    step_type: str
    delay_days: int
    delay_hours: int
    channel: Optional[str] = None
    template_name: Optional[str] = None
    message_content: Optional[str] = None
    ai_generated: bool
    settings: Optional[dict] = None
    created_at: str


class SequenceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    channel: str = "whatsapp"
    steps: Optional[list[SequenceStepCreate]] = None


class SequenceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    channel: Optional[str] = None
    status: Optional[str] = None  # draft | active | paused | archived


class SequenceResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    channel: str
    status: str
    status_ar: str  # Arabic status label
    total_steps: int
    total_enrolled: int
    total_completed: int
    total_converted: int
    steps: Optional[list[SequenceStepResponse]] = None
    created_at: str
    updated_at: Optional[str] = None


class EnrollRequest(BaseModel):
    lead_id: str


class EnrollmentResponse(BaseModel):
    id: str
    sequence_id: str
    lead_id: str
    current_step: int
    status: str
    status_ar: str
    enrolled_at: str
    next_step_at: Optional[str] = None
    completed_at: Optional[str] = None
    reply_received: bool


class PauseResponse(BaseModel):
    enrollment_id: str
    status: str
    status_ar: str
    message: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

STATUS_AR = {
    "draft": "مسودة",
    "active": "نشط",
    "paused": "متوقف مؤقتاً",
    "archived": "مؤرشف",
    "completed": "مكتمل",
    "replied": "تم الرد",
    "converted": "تم التحويل",
    "bounced": "مرتجع",
}

STEP_TYPE_AR = {
    "send_whatsapp": "إرسال واتساب",
    "send_email": "إرسال بريد إلكتروني",
    "create_task": "إنشاء مهمة",
    "update_status": "تحديث الحالة",
    "wait": "انتظار",
    "ai_reply": "رد ذكاء اصطناعي",
}

VALID_STEP_TYPES = set(STEP_TYPE_AR.keys())


def _serialize_dt(dt: Optional[datetime]) -> Optional[str]:
    """Convert a datetime to ISO string, or return None."""
    return dt.isoformat() if dt else None


def _step_to_response(step: SequenceStep) -> SequenceStepResponse:
    return SequenceStepResponse(
        id=str(step.id),
        sequence_id=str(step.sequence_id),
        step_order=step.step_order,
        step_type=step.step_type,
        delay_days=step.delay_days or 0,
        delay_hours=step.delay_hours or 0,
        channel=step.channel,
        template_name=step.template_name,
        message_content=step.message_content,
        ai_generated=step.ai_generated or False,
        settings=step.settings,
        created_at=_serialize_dt(step.created_at) or "",
    )


def _sequence_to_response(
    seq: Sequence,
    steps: Optional[list[SequenceStep]] = None,
) -> SequenceResponse:
    steps_out = [_step_to_response(s) for s in steps] if steps is not None else None
    return SequenceResponse(
        id=str(seq.id),
        tenant_id=str(seq.tenant_id),
        name=seq.name,
        industry=seq.industry,
        channel=seq.channel or "whatsapp",
        status=seq.status or "draft",
        status_ar=STATUS_AR.get(seq.status or "draft", seq.status or "draft"),
        total_steps=seq.total_steps or 0,
        total_enrolled=seq.total_enrolled or 0,
        total_completed=seq.total_completed or 0,
        total_converted=seq.total_converted or 0,
        steps=steps_out,
        created_at=_serialize_dt(seq.created_at) or "",
        updated_at=None,
    )


def _enrollment_to_response(enrollment: SequenceEnrollment) -> EnrollmentResponse:
    return EnrollmentResponse(
        id=str(enrollment.id),
        sequence_id=str(enrollment.sequence_id),
        lead_id=str(enrollment.lead_id),
        current_step=enrollment.current_step or 0,
        status=enrollment.status or "active",
        status_ar=STATUS_AR.get(enrollment.status or "active", enrollment.status or "active"),
        enrolled_at=_serialize_dt(enrollment.enrolled_at) or "",
        next_step_at=_serialize_dt(enrollment.next_step_at),
        completed_at=_serialize_dt(enrollment.completed_at),
        reply_received=enrollment.reply_received or False,
    )


async def _get_sequence_or_404(
    db: AsyncSession,
    sequence_id: str,
    tenant_id: str,
) -> Sequence:
    """Fetch a sequence by id and tenant, or raise 404."""
    result = await db.execute(
        select(Sequence).where(
            Sequence.id == sequence_id,
            Sequence.tenant_id == tenant_id,
        )
    )
    seq = result.scalars().first()
    if not seq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="التسلسل غير موجود",
        )
    return seq


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_sequence(
    req: SequenceCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new sales sequence with optional initial steps.

    إنشاء تسلسل مبيعات جديد مع خطوات اختيارية.
    """
    if req.steps:
        for step in req.steps:
            if step.step_type not in VALID_STEP_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"نوع الخطوة غير صالح: {step.step_type}. الأنواع المتاحة: {', '.join(VALID_STEP_TYPES)}",
                )

    tenant_id = current_user["tenant_id"]

    seq = Sequence(
        tenant_id=tenant_id,
        name=req.name,
        industry=req.industry,
        channel=req.channel,
        status="draft",
        total_steps=len(req.steps) if req.steps else 0,
        total_enrolled=0,
        total_completed=0,
        total_converted=0,
        settings={},
    )
    db.add(seq)
    await db.flush()  # get seq.id before creating steps

    created_steps: list[SequenceStep] = []
    if req.steps:
        for step_data in req.steps:
            step = SequenceStep(
                tenant_id=tenant_id,
                sequence_id=seq.id,
                step_order=step_data.step_order,
                step_type=step_data.step_type,
                delay_days=step_data.delay_days,
                delay_hours=step_data.delay_hours,
                channel=step_data.channel,
                template_name=step_data.template_name,
                message_content=step_data.message_content,
                ai_generated=step_data.ai_generated,
                settings=step_data.settings or {},
            )
            db.add(step)
            created_steps.append(step)

    await db.commit()
    await db.refresh(seq)
    for s in created_steps:
        await db.refresh(s)

    return {
        "status": "created",
        "الحالة": "تم الإنشاء",
        "sequence": _sequence_to_response(seq, created_steps).model_dump(),
    }


@router.get("/")
async def list_sequences(
    status_filter: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all sequences for the current tenant.

    عرض جميع التسلسلات للمستأجر الحالي.
    """
    tenant_id = current_user["tenant_id"]

    query = select(Sequence).where(Sequence.tenant_id == tenant_id)

    if status_filter:
        query = query.where(Sequence.status == status_filter)
    if industry:
        query = query.where(Sequence.industry == industry)

    # Total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginated results
    query = query.order_by(Sequence.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    sequences = result.scalars().all()

    return {
        "sequences": [_sequence_to_response(s).model_dump() for s in sequences],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{sequence_id}")
async def get_sequence(
    sequence_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get sequence details including all steps.

    عرض تفاصيل التسلسل مع جميع الخطوات.
    """
    tenant_id = current_user["tenant_id"]
    seq = await _get_sequence_or_404(db, sequence_id, tenant_id)

    # Fetch steps ordered by step_order
    steps_result = await db.execute(
        select(SequenceStep)
        .where(
            SequenceStep.sequence_id == seq.id,
            SequenceStep.tenant_id == tenant_id,
        )
        .order_by(SequenceStep.step_order)
    )
    steps = steps_result.scalars().all()

    return {"sequence": _sequence_to_response(seq, steps).model_dump()}


@router.put("/{sequence_id}")
async def update_sequence(
    sequence_id: str,
    req: SequenceUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a sales sequence.

    تحديث تسلسل مبيعات.
    """
    updated_fields = req.model_dump(exclude_none=True)
    if not updated_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا توجد حقول للتحديث",
        )

    if req.status and req.status not in STATUS_AR:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"حالة غير صالحة: {req.status}",
        )

    tenant_id = current_user["tenant_id"]
    seq = await _get_sequence_or_404(db, sequence_id, tenant_id)

    for field, value in updated_fields.items():
        setattr(seq, field, value)

    await db.commit()
    await db.refresh(seq)

    resp = _sequence_to_response(seq)
    return {"status": "updated", "الحالة": "تم التحديث", "sequence": resp.model_dump()}


@router.delete("/{sequence_id}")
async def delete_sequence(
    sequence_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a sequence by setting status to archived.

    حذف تسلسل (حذف ناعم).
    """
    tenant_id = current_user["tenant_id"]
    seq = await _get_sequence_or_404(db, sequence_id, tenant_id)

    seq.status = "archived"
    await db.commit()
    await db.refresh(seq)

    return {
        "status": "deleted",
        "الحالة": "تم الحذف",
        "sequence_id": str(seq.id),
        "message": "تم حذف التسلسل بنجاح (حذف ناعم)",
    }


# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------


@router.post("/{sequence_id}/steps", status_code=status.HTTP_201_CREATED)
async def add_step(
    sequence_id: str,
    req: SequenceStepCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a step to an existing sequence.

    إضافة خطوة إلى تسلسل موجود.
    """
    if req.step_type not in VALID_STEP_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"نوع الخطوة غير صالح: {req.step_type}. الأنواع المتاحة: {', '.join(VALID_STEP_TYPES)}",
        )

    tenant_id = current_user["tenant_id"]
    seq = await _get_sequence_or_404(db, sequence_id, tenant_id)

    step = SequenceStep(
        tenant_id=tenant_id,
        sequence_id=seq.id,
        step_order=req.step_order,
        step_type=req.step_type,
        delay_days=req.delay_days,
        delay_hours=req.delay_hours,
        channel=req.channel,
        template_name=req.template_name,
        message_content=req.message_content,
        ai_generated=req.ai_generated,
        settings=req.settings or {},
    )
    db.add(step)

    seq.total_steps = (seq.total_steps or 0) + 1

    await db.commit()
    await db.refresh(step)
    await db.refresh(seq)

    return {
        "status": "created",
        "الحالة": "تم الإنشاء",
        "step": _step_to_response(step).model_dump(),
        "step_type_ar": STEP_TYPE_AR.get(req.step_type, req.step_type),
    }


# ---------------------------------------------------------------------------
# Enrollments
# ---------------------------------------------------------------------------


@router.post("/{sequence_id}/enroll", status_code=status.HTTP_201_CREATED)
async def enroll_lead(
    sequence_id: str,
    req: EnrollRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enroll a lead in a sales sequence.

    تسجيل عميل محتمل في تسلسل مبيعات.
    """
    tenant_id = current_user["tenant_id"]
    seq = await _get_sequence_or_404(db, sequence_id, tenant_id)

    now = datetime.now(timezone.utc)

    enrollment = SequenceEnrollment(
        tenant_id=tenant_id,
        sequence_id=seq.id,
        lead_id=req.lead_id,
        current_step=0,
        status="active",
        enrolled_at=now,
        next_step_at=now,
        reply_received=False,
        extra_data={},
    )
    db.add(enrollment)

    seq.total_enrolled = (seq.total_enrolled or 0) + 1

    await db.commit()
    await db.refresh(enrollment)
    await db.refresh(seq)

    return {
        "status": "enrolled",
        "الحالة": "تم التسجيل",
        "enrollment": _enrollment_to_response(enrollment).model_dump(),
    }


@router.post("/{sequence_id}/pause/{enrollment_id}")
async def pause_enrollment(
    sequence_id: str,
    enrollment_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pause a lead's enrollment in a sequence.

    إيقاف تسجيل عميل محتمل مؤقتاً في تسلسل.
    """
    tenant_id = current_user["tenant_id"]

    result = await db.execute(
        select(SequenceEnrollment).where(
            SequenceEnrollment.id == enrollment_id,
            SequenceEnrollment.sequence_id == sequence_id,
            SequenceEnrollment.tenant_id == tenant_id,
        )
    )
    enrollment = result.scalars().first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="التسجيل غير موجود",
        )

    enrollment.status = "paused"
    enrollment.next_step_at = None

    await db.commit()
    await db.refresh(enrollment)

    return PauseResponse(
        enrollment_id=str(enrollment.id),
        status="paused",
        status_ar=STATUS_AR["paused"],
        message="تم إيقاف التسجيل مؤقتاً بنجاح",
    ).model_dump()


@router.get("/{sequence_id}/enrollments")
async def list_enrollments(
    sequence_id: str,
    status_filter: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all enrollments for a sequence.

    عرض جميع التسجيلات في تسلسل.
    """
    tenant_id = current_user["tenant_id"]

    # Verify sequence exists and belongs to tenant
    await _get_sequence_or_404(db, sequence_id, tenant_id)

    query = select(SequenceEnrollment).where(
        SequenceEnrollment.sequence_id == sequence_id,
        SequenceEnrollment.tenant_id == tenant_id,
    )

    if status_filter:
        query = query.where(SequenceEnrollment.status == status_filter)

    # Total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginated results
    query = query.order_by(SequenceEnrollment.enrolled_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    enrollments = result.scalars().all()

    return {
        "sequence_id": sequence_id,
        "enrollments": [_enrollment_to_response(e).model_dump() for e in enrollments],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
