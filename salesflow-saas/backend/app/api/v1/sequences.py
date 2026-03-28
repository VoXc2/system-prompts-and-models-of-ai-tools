"""Sales sequences - automated multi-step follow-up workflows for Dealix CRM."""
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.v1.deps import get_current_user, get_db

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


class SequenceStepResponse(SequenceStepCreate):
    id: str
    sequence_id: str
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
    updated_at: str


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

_now_iso = lambda: datetime.now(timezone.utc).isoformat()


def _mock_step(sequence_id: str, step: SequenceStepCreate) -> dict:
    return SequenceStepResponse(
        id=str(uuid4()),
        sequence_id=sequence_id,
        step_order=step.step_order,
        step_type=step.step_type,
        delay_days=step.delay_days,
        delay_hours=step.delay_hours,
        channel=step.channel,
        template_name=step.template_name,
        message_content=step.message_content,
        ai_generated=step.ai_generated,
        settings=step.settings,
        created_at=_now_iso(),
    ).model_dump()


def _mock_sequence(
    tenant_id: str,
    req: SequenceCreate,
    sequence_id: Optional[str] = None,
) -> dict:
    sid = sequence_id or str(uuid4())
    steps_out = [_mock_step(sid, s) for s in (req.steps or [])]
    return SequenceResponse(
        id=sid,
        tenant_id=tenant_id,
        name=req.name,
        description=req.description,
        industry=req.industry,
        channel=req.channel,
        status="draft",
        status_ar=STATUS_AR["draft"],
        total_steps=len(steps_out),
        total_enrolled=0,
        total_completed=0,
        total_converted=0,
        steps=steps_out,
        created_at=_now_iso(),
        updated_at=_now_iso(),
    ).model_dump()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_sequence(
    req: SequenceCreate,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
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

    sequence = _mock_sequence(current_user["tenant_id"], req)
    return {"status": "created", "الحالة": "تم الإنشاء", "sequence": sequence}


@router.get("/")
async def list_sequences(
    status_filter: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """List all sequences for the current tenant.

    عرض جميع التسلسلات للمستأجر الحالي.
    """
    # Mock: return a sample sequence to demonstrate shape
    sample = SequenceResponse(
        id=str(uuid4()),
        tenant_id=current_user["tenant_id"],
        name="متابعة العملاء المحتملين - عقارات",
        description="تسلسل متابعة تلقائي للعملاء المهتمين بالعقارات",
        industry="عقارات",
        channel="whatsapp",
        status="active",
        status_ar=STATUS_AR["active"],
        total_steps=4,
        total_enrolled=23,
        total_completed=8,
        total_converted=3,
        steps=None,
        created_at=_now_iso(),
        updated_at=_now_iso(),
    ).model_dump()

    return {
        "sequences": [sample],
        "total": 1,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{sequence_id}")
async def get_sequence(
    sequence_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """Get sequence details including all steps.

    عرض تفاصيل التسلسل مع جميع الخطوات.
    """
    mock_steps = [
        SequenceStepResponse(
            id=str(uuid4()),
            sequence_id=sequence_id,
            step_order=1,
            step_type="send_whatsapp",
            delay_days=0,
            delay_hours=0,
            channel="whatsapp",
            template_name="ترحيب_عميل_جديد",
            message_content="مرحباً {name}، شكراً لاهتمامك! كيف يمكنني مساعدتك؟",
            ai_generated=False,
            settings=None,
            created_at=_now_iso(),
        ),
        SequenceStepResponse(
            id=str(uuid4()),
            sequence_id=sequence_id,
            step_order=2,
            step_type="wait",
            delay_days=1,
            delay_hours=0,
            channel=None,
            template_name=None,
            message_content=None,
            ai_generated=False,
            settings=None,
            created_at=_now_iso(),
        ),
        SequenceStepResponse(
            id=str(uuid4()),
            sequence_id=sequence_id,
            step_order=3,
            step_type="ai_reply",
            delay_days=0,
            delay_hours=0,
            channel="whatsapp",
            template_name=None,
            message_content=None,
            ai_generated=True,
            settings={"tone": "professional", "language": "ar"},
            created_at=_now_iso(),
        ),
        SequenceStepResponse(
            id=str(uuid4()),
            sequence_id=sequence_id,
            step_order=4,
            step_type="create_task",
            delay_days=3,
            delay_hours=0,
            channel=None,
            template_name=None,
            message_content="اتصال متابعة مع العميل",
            ai_generated=False,
            settings={"task_type": "call", "priority": "high"},
            created_at=_now_iso(),
        ),
    ]

    sequence = SequenceResponse(
        id=sequence_id,
        tenant_id=current_user["tenant_id"],
        name="متابعة العملاء المحتملين - عقارات",
        description="تسلسل متابعة تلقائي للعملاء المهتمين بالعقارات",
        industry="عقارات",
        channel="whatsapp",
        status="active",
        status_ar=STATUS_AR["active"],
        total_steps=len(mock_steps),
        total_enrolled=23,
        total_completed=8,
        total_converted=3,
        steps=[s.model_dump() for s in mock_steps],
        created_at=_now_iso(),
        updated_at=_now_iso(),
    )

    return {"sequence": sequence.model_dump()}


@router.put("/{sequence_id}")
async def update_sequence(
    sequence_id: str,
    req: SequenceUpdate,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
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

    result = {
        "id": sequence_id,
        "tenant_id": current_user["tenant_id"],
        **updated_fields,
        "updated_at": _now_iso(),
    }
    if "status" in result:
        result["status_ar"] = STATUS_AR[result["status"]]

    return {"status": "updated", "الحالة": "تم التحديث", "sequence": result}


@router.delete("/{sequence_id}")
async def delete_sequence(
    sequence_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """Soft-delete a sequence by setting is_active=False.

    حذف تسلسل (حذف ناعم).
    """
    return {
        "status": "deleted",
        "الحالة": "تم الحذف",
        "sequence_id": sequence_id,
        "is_active": False,
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
    db=Depends(get_db),
):
    """Add a step to an existing sequence.

    إضافة خطوة إلى تسلسل موجود.
    """
    if req.step_type not in VALID_STEP_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"نوع الخطوة غير صالح: {req.step_type}. الأنواع المتاحة: {', '.join(VALID_STEP_TYPES)}",
        )

    step = _mock_step(sequence_id, req)
    return {
        "status": "created",
        "الحالة": "تم الإنشاء",
        "step": step,
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
    db=Depends(get_db),
):
    """Enroll a lead in a sales sequence.

    تسجيل عميل محتمل في تسلسل مبيعات.
    """
    enrollment = EnrollmentResponse(
        id=str(uuid4()),
        sequence_id=sequence_id,
        lead_id=req.lead_id,
        current_step=0,
        status="active",
        status_ar=STATUS_AR["active"],
        enrolled_at=_now_iso(),
        next_step_at=_now_iso(),
        completed_at=None,
        reply_received=False,
    )

    return {
        "status": "enrolled",
        "الحالة": "تم التسجيل",
        "enrollment": enrollment.model_dump(),
    }


@router.post("/{sequence_id}/pause/{enrollment_id}")
async def pause_enrollment(
    sequence_id: str,
    enrollment_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """Pause a lead's enrollment in a sequence.

    إيقاف تسجيل عميل محتمل مؤقتاً في تسلسل.
    """
    return PauseResponse(
        enrollment_id=enrollment_id,
        status="paused",
        status_ar=STATUS_AR["paused"],
        message="تم إيقاف التسجيل مؤقتاً بنجاح",
    ).model_dump()


@router.get("/{sequence_id}/enrollments")
async def list_enrollments(
    sequence_id: str,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    """List all enrollments for a sequence.

    عرض جميع التسجيلات في تسلسل.
    """
    sample = EnrollmentResponse(
        id=str(uuid4()),
        sequence_id=sequence_id,
        lead_id=str(uuid4()),
        current_step=2,
        status="active",
        status_ar=STATUS_AR["active"],
        enrolled_at=_now_iso(),
        next_step_at=_now_iso(),
        completed_at=None,
        reply_received=False,
    ).model_dump()

    return {
        "sequence_id": sequence_id,
        "enrollments": [sample],
        "total": 1,
        "limit": limit,
        "offset": offset,
    }
