"""Celery tasks for automated lead follow-up."""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.workers.celery_app import celery_app
from app.database import async_session
from app.models.activity import Activity
from app.models.lead import Lead
from app.integrations.whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)


async def _process_pending_followups():
    """Find leads needing follow-up and trigger automated messages."""
    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(hours=48)

    async with async_session() as db:
        # Find leads with status 'contacted' but no activity in 48 hours
        result = await db.execute(
            select(Lead).where(
                Lead.status.in_(["contacted", "qualified"]),
                Lead.updated_at < stale_cutoff,
                Lead.phone != None,
            ).limit(50)
        )
        stale_leads = result.scalars().all()

        for lead in stale_leads:
            try:
                msg = (
                    f"مرحبًا {lead.name or 'عزيزي العميل'}!\n"
                    f"نتابع معك بخصوص استفسارك السابق.\n"
                    f"هل تحتاج أي مساعدة إضافية؟ نحن هنا لخدمتك 🙏"
                )
                await send_whatsapp_message(lead.phone, msg)

                # Log the follow-up activity
                activity = Activity(
                    tenant_id=lead.tenant_id,
                    lead_id=lead.id,
                    type="follow_up",
                    subject="متابعة تلقائية",
                    description="تم إرسال رسالة متابعة تلقائية عبر واتساب",
                    is_automated=True,
                    completed_at=now,
                )
                db.add(activity)
                logger.info("Follow-up sent to lead %s (%s)", lead.id, lead.name)
            except Exception as e:
                logger.error("Failed follow-up for lead %s: %s", lead.id, e)

        await db.commit()
        logger.info("Processed %d pending follow-ups", len(stale_leads))


async def _execute_workflow(workflow_id: str, lead_id: str):
    """Execute a specific automation workflow for a lead."""
    async with async_session() as db:
        result = await db.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()
        if not lead:
            logger.warning("Workflow %s: lead %s not found", workflow_id, lead_id)
            return

        logger.info("Executing workflow %s for lead %s", workflow_id, lead.name)
        # Workflow execution is extensible — future workflows will be loaded
        # from a workflow definitions table and executed step by step


@celery_app.task(name="app.workers.follow_up_tasks.process_pending_followups")
def process_pending_followups():
    """Check for leads that need follow-up and trigger automated messages."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_process_pending_followups())
    finally:
        loop.close()
    return {"status": "ok"}


@celery_app.task(name="app.workers.follow_up_tasks.execute_workflow")
def execute_workflow(workflow_id: str, lead_id: str):
    """Execute a specific automation workflow for a lead."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_execute_workflow(workflow_id, lead_id))
    finally:
        loop.close()
    return {"status": "ok"}
