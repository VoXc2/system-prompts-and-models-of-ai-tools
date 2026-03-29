"""
Celery tasks for appointment reminders and no-show management.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery_app import celery_app
from app.database import async_session
from app.models.appointment import Appointment
from app.integrations.whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)


async def _send_reminders():
    """Send WhatsApp reminders for upcoming appointments."""
    now = datetime.now(timezone.utc)

    async with async_session() as db:
        # 24-hour reminders
        cutoff_24h = now + timedelta(hours=24)
        result = await db.execute(
            select(Appointment).where(
                Appointment.status.in_(["pending", "confirmed"]),
                Appointment.reminder_24h_sent == False,
                Appointment.start_time <= cutoff_24h,
                Appointment.start_time > now + timedelta(hours=23),
                Appointment.contact_phone != None,
            )
        )
        due_24h = result.scalars().all()

        for apt in due_24h:
            try:
                time_str = apt.start_time.strftime("%I:%M %p") if apt.start_time else ""
                date_str = apt.start_time.strftime("%Y-%m-%d") if apt.start_time else ""
                msg = (
                    f"هلا {apt.contact_name or 'عزيزي العميل'}! 👋\n"
                    f"تذكير بموعدك بكرة:\n"
                    f"📅 {date_str}\n"
                    f"🕐 {time_str}\n"
                    f"📍 {apt.location or 'الفرع الرئيسي'}\n\n"
                    f"إذا تبي تعدل أو تلغي الموعد رد على هالرسالة"
                )
                await send_whatsapp_message(apt.contact_phone, msg)
                apt.reminder_24h_sent = True
                logger.info("24h reminder sent for appointment %s", apt.id)
            except Exception as e:
                logger.error("Failed to send 24h reminder for %s: %s", apt.id, e)

        # 1-hour reminders
        cutoff_1h = now + timedelta(hours=1)
        result = await db.execute(
            select(Appointment).where(
                Appointment.status.in_(["pending", "confirmed"]),
                Appointment.reminder_1h_sent == False,
                Appointment.start_time <= cutoff_1h,
                Appointment.start_time > now,
                Appointment.contact_phone != None,
            )
        )
        due_1h = result.scalars().all()

        for apt in due_1h:
            try:
                time_str = apt.start_time.strftime("%I:%M %p") if apt.start_time else ""
                msg = (
                    f"{apt.contact_name or 'عزيزي العميل'}\n"
                    f"موعدك بعد ساعة الساعة {time_str} ⏰\n"
                    f"ننتظرك إن شاء الله!"
                )
                await send_whatsapp_message(apt.contact_phone, msg)
                apt.reminder_1h_sent = True
                logger.info("1h reminder sent for appointment %s", apt.id)
            except Exception as e:
                logger.error("Failed to send 1h reminder for %s: %s", apt.id, e)

        await db.commit()


async def _mark_no_shows():
    """Mark overdue confirmed appointments as no-show."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=30)  # 30 min grace period

    async with async_session() as db:
        await db.execute(
            update(Appointment)
            .where(
                Appointment.status == "confirmed",
                Appointment.end_time < cutoff,
            )
            .values(status="no_show")
        )
        await db.commit()


@celery_app.task(name="app.workers.appointment_tasks.send_appointment_reminders")
def send_appointment_reminders():
    """Celery task: Send appointment reminders via WhatsApp."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_send_reminders())
    finally:
        loop.close()
    return {"status": "ok"}


@celery_app.task(name="app.workers.appointment_tasks.mark_no_shows")
def mark_no_shows():
    """Celery task: Mark overdue appointments as no-show."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_mark_no_shows())
    finally:
        loop.close()
    return {"status": "ok"}
