"""Appointment booking endpoints for Dealix CRM."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.api.v1.deps import get_current_user, get_db
from app.models.appointment import Appointment
from app.services.appointment_service import AppointmentService

router = APIRouter()


# ─── Schemas ───

class AppointmentCreate(BaseModel):
    title: Optional[str] = None
    service_type: str = "other"
    start_time: datetime
    duration_minutes: Optional[int] = None
    lead_id: Optional[str] = None
    customer_id: Optional[str] = None
    assigned_to: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    booked_via: str = "manual"


class AppointmentUpdate(BaseModel):
    title: Optional[str] = None
    service_type: Optional[str] = None
    start_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    assigned_to: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class AvailabilityQuery(BaseModel):
    date: datetime
    service_type: str = "other"
    assigned_to: Optional[str] = None


def _serialize(a: Appointment) -> dict:
    return {
        "id": str(a.id),
        "tenant_id": str(a.tenant_id),
        "title": a.title,
        "service_type": a.service_type,
        "start_time": a.start_time.isoformat() if a.start_time else None,
        "end_time": a.end_time.isoformat() if a.end_time else None,
        "duration_minutes": a.duration_minutes,
        "status": a.status,
        "booked_via": a.booked_via,
        "contact_name": a.contact_name,
        "contact_phone": a.contact_phone,
        "contact_email": a.contact_email,
        "location": a.location,
        "notes": a.notes,
        "lead_id": str(a.lead_id) if a.lead_id else None,
        "customer_id": str(a.customer_id) if a.customer_id else None,
        "assigned_to": str(a.assigned_to) if a.assigned_to else None,
        "reminder_sent": a.reminder_sent,
        "is_recurring": a.is_recurring,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


# ─── Endpoints ───

@router.post("", status_code=201)
async def create_appointment(
    req: AppointmentCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """حجز موعد جديد مع التحقق من عدم التعارض."""
    svc = AppointmentService(db, current_user["tenant_id"])
    try:
        apt = await svc.book(
            start_time=req.start_time,
            service_type=req.service_type,
            title=req.title,
            lead_id=req.lead_id,
            customer_id=req.customer_id,
            assigned_to=req.assigned_to,
            contact_name=req.contact_name,
            contact_phone=req.contact_phone,
            contact_email=req.contact_email,
            location=req.location,
            notes=req.notes,
            booked_via=req.booked_via,
            duration_minutes=req.duration_minutes,
        )
        return {"status": "success", "message": "تم حجز الموعد بنجاح", "data": _serialize(apt)}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("")
async def list_appointments(
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """عرض قائمة المواعيد مع الفلاتر."""
    tenant_id = current_user["tenant_id"]
    query = select(Appointment).where(Appointment.tenant_id == tenant_id)

    if status:
        query = query.where(Appointment.status == status)
    if assigned_to:
        query = query.where(Appointment.assigned_to == assigned_to)
    if date_from:
        query = query.where(Appointment.start_time >= datetime.fromisoformat(date_from))
    if date_to:
        query = query.where(Appointment.start_time <= datetime.fromisoformat(date_to))

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    offset = (page - 1) * per_page
    query = query.order_by(Appointment.start_time.desc()).offset(offset).limit(per_page)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "status": "success",
        "data": {
            "items": [_serialize(a) for a in items],
            "total": total,
            "page": page,
            "per_page": per_page,
        },
    }


@router.get("/today")
async def today_appointments(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """عرض مواعيد اليوم."""
    svc = AppointmentService(db, current_user["tenant_id"])
    appointments = await svc.get_today()
    return {
        "status": "success",
        "data": [_serialize(a) for a in appointments],
        "total": len(appointments),
    }


@router.get("/availability")
async def check_availability(
    date: str = Query(..., description="التاريخ بصيغة YYYY-MM-DD"),
    service_type: str = Query("other"),
    assigned_to: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """فحص الأوقات المتاحة لتاريخ محدد."""
    svc = AppointmentService(db, current_user["tenant_id"])
    dt = datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
    slots = await svc.get_availability(dt, assigned_to, service_type)
    return {
        "status": "success",
        "date": date,
        "service_type": service_type,
        "available_slots": slots,
        "total_available": len(slots),
    }


@router.get("/stats")
async def appointment_stats(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """إحصائيات المواعيد."""
    svc = AppointmentService(db, current_user["tenant_id"])
    stats = await svc.get_stats()
    return {"status": "success", "data": stats}


@router.get("/{appointment_id}")
async def get_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """جلب بيانات موعد محدد."""
    tenant_id = current_user["tenant_id"]
    result = await db.execute(
        select(Appointment).where(
            Appointment.id == appointment_id,
            Appointment.tenant_id == tenant_id,
        )
    )
    apt = result.scalar_one_or_none()
    if not apt:
        raise HTTPException(status_code=404, detail="الموعد غير موجود")
    return {"status": "success", "data": _serialize(apt)}


@router.put("/{appointment_id}")
async def update_appointment(
    appointment_id: str,
    req: AppointmentUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """تعديل موعد (إعادة جدولة)."""
    svc = AppointmentService(db, current_user["tenant_id"])
    try:
        if req.start_time:
            apt = await svc.reschedule(appointment_id, req.start_time, req.duration_minutes)
        else:
            apt = await svc._get(appointment_id)

        # Update other fields
        for field in ["title", "service_type", "assigned_to", "contact_name", "contact_phone", "location", "notes"]:
            val = getattr(req, field, None)
            if val is not None:
                setattr(apt, field, val)
        await db.commit()
        await db.refresh(apt)

        return {"status": "success", "message": "تم تعديل الموعد", "data": _serialize(apt)}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/{appointment_id}/confirm")
async def confirm_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """تأكيد موعد."""
    svc = AppointmentService(db, current_user["tenant_id"])
    try:
        apt = await svc.confirm(appointment_id)
        return {"status": "success", "message": "تم تأكيد الموعد", "data": _serialize(apt)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{appointment_id}/complete")
async def complete_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """تحديد الموعد كمكتمل."""
    svc = AppointmentService(db, current_user["tenant_id"])
    try:
        apt = await svc.complete(appointment_id)
        return {"status": "success", "message": "تم إكمال الموعد", "data": _serialize(apt)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{appointment_id}/no-show")
async def no_show_appointment(
    appointment_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """تحديد الموعد كعدم حضور."""
    svc = AppointmentService(db, current_user["tenant_id"])
    try:
        apt = await svc.mark_no_show(appointment_id)
        return {"status": "success", "message": "تم تسجيل عدم الحضور", "data": _serialize(apt)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{appointment_id}")
async def cancel_appointment(
    appointment_id: str,
    reason: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """إلغاء موعد."""
    svc = AppointmentService(db, current_user["tenant_id"])
    try:
        apt = await svc.cancel(appointment_id, reason)
        return {"status": "success", "message": "تم إلغاء الموعد", "data": _serialize(apt)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
