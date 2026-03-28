"""
Dealix Appointment Service — Booking, reminders, availability checking.
Core feature for salons, clinics, and service businesses.
"""
import logging
from datetime import datetime, timedelta, timezone, time as dt_time
from typing import Optional
from uuid import uuid4

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.appointment import Appointment

logger = logging.getLogger(__name__)
settings = get_settings()

# Default business hours (Saudi Arabia)
DEFAULT_BUSINESS_HOURS = {
    "start": dt_time(9, 0),   # 9 AM
    "end": dt_time(22, 0),    # 10 PM
    "slot_minutes": 30,
    "break_start": dt_time(12, 0),   # Prayer/lunch break
    "break_end": dt_time(13, 0),
}

# Service durations per type (minutes)
SERVICE_DURATIONS = {
    # Salons
    "haircut": 30,
    "hair_color": 90,
    "hair_treatment": 60,
    "facial": 45,
    "makeup": 60,
    "manicure": 30,
    "pedicure": 45,
    "bridal": 180,
    # Clinics
    "consultation": 30,
    "checkup": 45,
    "followup": 20,
    "procedure": 60,
    "dental_cleaning": 30,
    "dental_filling": 45,
    # General
    "demo": 30,
    "meeting": 60,
    "callback": 15,
    "other": 30,
}


class AppointmentService:
    """Manages appointment booking, availability, and reminders."""

    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    async def book(
        self,
        start_time: datetime,
        service_type: str = "other",
        title: Optional[str] = None,
        lead_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
        contact_name: Optional[str] = None,
        contact_phone: Optional[str] = None,
        contact_email: Optional[str] = None,
        location: Optional[str] = None,
        notes: Optional[str] = None,
        booked_via: str = "manual",
        duration_minutes: Optional[int] = None,
    ) -> Appointment:
        """Book a new appointment with conflict checking."""

        duration = duration_minutes or SERVICE_DURATIONS.get(service_type, 30)
        end_time = start_time + timedelta(minutes=duration)

        # Check for conflicts
        conflict = await self._check_conflict(start_time, end_time, assigned_to)
        if conflict:
            raise ValueError(
                f"يوجد موعد متعارض في هذا الوقت: {conflict.title or conflict.service_type} "
                f"({conflict.start_time.strftime('%H:%M')} - {conflict.end_time.strftime('%H:%M')})"
            )

        if not title:
            title = self._generate_title(service_type, contact_name)

        appointment = Appointment(
            tenant_id=self.tenant_id,
            lead_id=lead_id,
            customer_id=customer_id,
            assigned_to=assigned_to,
            title=title,
            service_type=service_type,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration,
            status="pending",
            booked_via=booked_via,
            contact_name=contact_name,
            contact_phone=contact_phone,
            contact_email=contact_email,
            location=location,
            notes=notes,
        )
        self.db.add(appointment)
        await self.db.commit()
        await self.db.refresh(appointment)

        logger.info(
            "Appointment booked: %s at %s via %s",
            service_type, start_time.isoformat(), booked_via,
        )
        return appointment

    async def confirm(self, appointment_id: str) -> Appointment:
        """Confirm a pending appointment."""
        apt = await self._get(appointment_id)
        if apt.status != "pending":
            raise ValueError(f"لا يمكن تأكيد موعد بحالة: {apt.status}")
        apt.status = "confirmed"
        await self.db.commit()
        await self.db.refresh(apt)
        return apt

    async def cancel(self, appointment_id: str, reason: Optional[str] = None) -> Appointment:
        """Cancel an appointment."""
        apt = await self._get(appointment_id)
        if apt.status in ("completed", "cancelled"):
            raise ValueError(f"لا يمكن إلغاء موعد بحالة: {apt.status}")
        apt.status = "cancelled"
        if reason:
            apt.notes = f"{apt.notes or ''}\nسبب الإلغاء: {reason}".strip()
        await self.db.commit()
        await self.db.refresh(apt)
        return apt

    async def complete(self, appointment_id: str) -> Appointment:
        """Mark appointment as completed."""
        apt = await self._get(appointment_id)
        apt.status = "completed"
        await self.db.commit()
        await self.db.refresh(apt)
        return apt

    async def mark_no_show(self, appointment_id: str) -> Appointment:
        """Mark appointment as no-show."""
        apt = await self._get(appointment_id)
        apt.status = "no_show"
        await self.db.commit()
        await self.db.refresh(apt)
        return apt

    async def reschedule(
        self,
        appointment_id: str,
        new_start_time: datetime,
        duration_minutes: Optional[int] = None,
    ) -> Appointment:
        """Reschedule an appointment."""
        apt = await self._get(appointment_id)
        duration = duration_minutes or apt.duration_minutes or 30
        new_end = new_start_time + timedelta(minutes=duration)

        conflict = await self._check_conflict(new_start_time, new_end, apt.assigned_to, exclude_id=appointment_id)
        if conflict:
            raise ValueError("يوجد موعد متعارض في الوقت الجديد")

        apt.start_time = new_start_time
        apt.end_time = new_end
        apt.duration_minutes = duration
        apt.reminder_sent = False
        apt.reminder_24h_sent = False
        apt.reminder_1h_sent = False
        await self.db.commit()
        await self.db.refresh(apt)
        return apt

    async def get_availability(
        self,
        date: datetime,
        assigned_to: Optional[str] = None,
        service_type: str = "other",
    ) -> list[dict]:
        """Get available time slots for a given date."""
        duration = SERVICE_DURATIONS.get(service_type, 30)
        hours = DEFAULT_BUSINESS_HOURS

        # Get existing appointments for the date
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        query = select(Appointment).where(
            Appointment.tenant_id == self.tenant_id,
            Appointment.start_time >= day_start,
            Appointment.start_time < day_end,
            Appointment.status.in_(["pending", "confirmed"]),
        )
        if assigned_to:
            query = query.where(Appointment.assigned_to == assigned_to)

        result = await self.db.execute(query.order_by(Appointment.start_time))
        existing = result.scalars().all()

        # Build busy intervals
        busy = [(a.start_time, a.end_time or a.start_time + timedelta(minutes=a.duration_minutes or 30)) for a in existing]

        # Add break time
        break_start = date.replace(hour=hours["break_start"].hour, minute=hours["break_start"].minute)
        break_end = date.replace(hour=hours["break_end"].hour, minute=hours["break_end"].minute)
        busy.append((break_start, break_end))

        # Generate available slots
        slots = []
        current = date.replace(hour=hours["start"].hour, minute=hours["start"].minute, second=0, microsecond=0)
        end_of_day = date.replace(hour=hours["end"].hour, minute=hours["end"].minute)

        while current + timedelta(minutes=duration) <= end_of_day:
            slot_end = current + timedelta(minutes=duration)
            is_available = not any(
                (current < b_end and slot_end > b_start) for b_start, b_end in busy
            )
            if is_available:
                slots.append({
                    "start": current.isoformat(),
                    "end": slot_end.isoformat(),
                    "duration_minutes": duration,
                    "available": True,
                })
            current += timedelta(minutes=hours["slot_minutes"])

        return slots

    async def get_today(self, assigned_to: Optional[str] = None) -> list[Appointment]:
        """Get today's appointments."""
        now = datetime.now(timezone.utc)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        query = select(Appointment).where(
            Appointment.tenant_id == self.tenant_id,
            Appointment.start_time >= day_start,
            Appointment.start_time < day_end,
        )
        if assigned_to:
            query = query.where(Appointment.assigned_to == assigned_to)

        result = await self.db.execute(query.order_by(Appointment.start_time))
        return list(result.scalars().all())

    async def get_due_reminders(self) -> list[Appointment]:
        """Get appointments that need reminders sent."""
        now = datetime.now(timezone.utc)
        reminder_24h = now + timedelta(hours=24)
        reminder_1h = now + timedelta(hours=1)

        # 24h reminders
        query_24h = select(Appointment).where(
            Appointment.tenant_id == self.tenant_id,
            Appointment.status.in_(["pending", "confirmed"]),
            Appointment.reminder_24h_sent == False,
            Appointment.start_time <= reminder_24h,
            Appointment.start_time > now,
        )
        result_24h = await self.db.execute(query_24h)
        due_24h = list(result_24h.scalars().all())

        # 1h reminders
        query_1h = select(Appointment).where(
            Appointment.tenant_id == self.tenant_id,
            Appointment.status.in_(["pending", "confirmed"]),
            Appointment.reminder_1h_sent == False,
            Appointment.start_time <= reminder_1h,
            Appointment.start_time > now,
        )
        result_1h = await self.db.execute(query_1h)
        due_1h = list(result_1h.scalars().all())

        return due_24h + due_1h

    async def get_stats(self) -> dict:
        """Get appointment statistics for the tenant."""
        now = datetime.now(timezone.utc)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_today = (await self.db.execute(
            select(func.count()).where(
                Appointment.tenant_id == self.tenant_id,
                Appointment.start_time >= day_start,
                Appointment.start_time < day_start + timedelta(days=1),
            )
        )).scalar() or 0

        total_month = (await self.db.execute(
            select(func.count()).where(
                Appointment.tenant_id == self.tenant_id,
                Appointment.start_time >= month_start,
            )
        )).scalar() or 0

        completed_month = (await self.db.execute(
            select(func.count()).where(
                Appointment.tenant_id == self.tenant_id,
                Appointment.status == "completed",
                Appointment.start_time >= month_start,
            )
        )).scalar() or 0

        no_show_month = (await self.db.execute(
            select(func.count()).where(
                Appointment.tenant_id == self.tenant_id,
                Appointment.status == "no_show",
                Appointment.start_time >= month_start,
            )
        )).scalar() or 0

        no_show_rate = (no_show_month / total_month * 100) if total_month > 0 else 0

        return {
            "today": total_today,
            "this_month": total_month,
            "completed_this_month": completed_month,
            "no_show_this_month": no_show_month,
            "no_show_rate": round(no_show_rate, 1),
        }

    # ─── Private Methods ───

    async def _get(self, appointment_id: str) -> Appointment:
        result = await self.db.execute(
            select(Appointment).where(
                Appointment.id == appointment_id,
                Appointment.tenant_id == self.tenant_id,
            )
        )
        apt = result.scalar_one_or_none()
        if not apt:
            raise ValueError("الموعد غير موجود")
        return apt

    async def _check_conflict(
        self,
        start: datetime,
        end: datetime,
        assigned_to: Optional[str],
        exclude_id: Optional[str] = None,
    ) -> Optional[Appointment]:
        """Check if a time slot conflicts with existing appointments."""
        query = select(Appointment).where(
            Appointment.tenant_id == self.tenant_id,
            Appointment.status.in_(["pending", "confirmed"]),
            Appointment.start_time < end,
            Appointment.end_time > start,
        )
        if assigned_to:
            query = query.where(Appointment.assigned_to == assigned_to)
        if exclude_id:
            query = query.where(Appointment.id != exclude_id)

        result = await self.db.execute(query.limit(1))
        return result.scalar_one_or_none()

    @staticmethod
    def _generate_title(service_type: str, contact_name: Optional[str]) -> str:
        """Generate a human-readable Arabic title."""
        type_labels = {
            "haircut": "قص شعر",
            "hair_color": "صبغة شعر",
            "hair_treatment": "علاج شعر",
            "facial": "عناية بالبشرة",
            "makeup": "مكياج",
            "manicure": "مانيكير",
            "pedicure": "باديكير",
            "bridal": "تجهيز عروس",
            "consultation": "استشارة",
            "checkup": "فحص",
            "followup": "متابعة",
            "procedure": "إجراء طبي",
            "dental_cleaning": "تنظيف أسنان",
            "dental_filling": "حشوة أسنان",
            "demo": "عرض تجريبي",
            "meeting": "اجتماع",
            "callback": "اتصال",
            "other": "موعد",
        }
        label = type_labels.get(service_type, "موعد")
        if contact_name:
            return f"{label} - {contact_name}"
        return label
