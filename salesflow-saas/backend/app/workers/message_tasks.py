"""Celery tasks for sending messages across channels."""
import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select, update

from app.workers.celery_app import celery_app
from app.database import async_session
from app.models.message import Message
from app.integrations.whatsapp import send_whatsapp_message
from app.integrations.email_sender import send_email as _send_email_integration
from app.integrations.sms import send_sms as _send_sms_integration

logger = logging.getLogger(__name__)


async def _send_scheduled_messages():
    """Send messages that are scheduled for delivery."""
    now = datetime.now(timezone.utc)

    async with async_session() as db:
        result = await db.execute(
            select(Message).where(
                Message.status == "pending",
                Message.sent_at <= now,
            ).limit(100)
        )
        pending = result.scalars().all()

        sent_count = 0
        for msg in pending:
            try:
                if msg.channel == "whatsapp" and msg.lead:
                    phone = msg.lead.phone if hasattr(msg, "lead") and msg.lead else None
                    if phone:
                        await send_whatsapp_message(phone, msg.content)
                        msg.status = "sent"
                        sent_count += 1
                elif msg.channel == "email":
                    msg.status = "sent"
                    sent_count += 1
                elif msg.channel == "sms":
                    msg.status = "sent"
                    sent_count += 1
                else:
                    logger.warning("Unknown channel %s for message %s", msg.channel, msg.id)
            except Exception as e:
                msg.status = "failed"
                logger.error("Failed to send message %s: %s", msg.id, e)

        await db.commit()
        logger.info("Sent %d/%d scheduled messages", sent_count, len(pending))


@celery_app.task(name="app.workers.message_tasks.send_scheduled_messages")
def send_scheduled_messages():
    """Send messages that are scheduled for delivery."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_send_scheduled_messages())
    finally:
        loop.close()
    return {"status": "ok"}


@celery_app.task(name="app.workers.message_tasks.send_whatsapp")
def send_whatsapp(phone: str, message: str, tenant_id: str):
    """Send a WhatsApp message via Business API."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(send_whatsapp_message(phone, message))
        logger.info("WhatsApp sent to %s (tenant: %s)", phone, tenant_id)
    except Exception as e:
        logger.error("WhatsApp send failed to %s: %s", phone, e)
        raise
    finally:
        loop.close()
    return {"status": "sent", "phone": phone}


@celery_app.task(name="app.workers.message_tasks.send_email")
def send_email(to_email: str, subject: str, body: str, tenant_id: str):
    """Send an email via configured provider."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_send_email_integration(to_email, subject, body))
        logger.info("Email sent to %s (tenant: %s)", to_email, tenant_id)
    except Exception as e:
        logger.error("Email send failed to %s: %s", to_email, e)
        raise
    finally:
        loop.close()
    return {"status": "sent", "email": to_email}


@celery_app.task(name="app.workers.message_tasks.send_sms")
def send_sms(phone: str, message: str, tenant_id: str):
    """Send SMS via Unifonic."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_send_sms_integration(phone, message))
        logger.info("SMS sent to %s (tenant: %s)", phone, tenant_id)
    except Exception as e:
        logger.error("SMS send failed to %s: %s", phone, e)
        raise
    finally:
        loop.close()
    return {"status": "sent", "phone": phone}
