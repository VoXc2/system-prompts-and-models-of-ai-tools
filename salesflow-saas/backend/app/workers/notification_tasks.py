"""Celery tasks for notifications and reports."""
import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func

from app.workers.celery_app import celery_app
from app.database import async_session
from app.models.notification import Notification
from app.models.tenant import Tenant
from app.models.lead import Lead
from app.models.deal import Deal

logger = logging.getLogger(__name__)


async def _send_daily_report():
    """Generate and send daily sales report to all active tenants."""
    today = datetime.now(timezone.utc).date()

    async with async_session() as db:
        # Get all active tenants
        result = await db.execute(
            select(Tenant).where(Tenant.is_active == True)
        )
        tenants = result.scalars().all()

        for tenant in tenants:
            try:
                # Count today's leads
                lead_count = await db.execute(
                    select(func.count(Lead.id)).where(
                        Lead.tenant_id == tenant.id,
                        func.date(Lead.created_at) == today,
                    )
                )
                new_leads = lead_count.scalar() or 0

                # Count today's deals
                deal_count = await db.execute(
                    select(func.count(Deal.id)).where(
                        Deal.tenant_id == tenant.id,
                        func.date(Deal.created_at) == today,
                    )
                )
                new_deals = deal_count.scalar() or 0

                # Create notification for tenant owner
                from app.models.user import User
                owner_result = await db.execute(
                    select(User).where(
                        User.tenant_id == tenant.id,
                        User.role == "admin",
                    ).limit(1)
                )
                owner = owner_result.scalar_one_or_none()

                if owner:
                    notification = Notification(
                        tenant_id=tenant.id,
                        user_id=owner.id,
                        type="daily_report",
                        title="التقرير اليومي",
                        body=(
                            f"عملاء محتملون جدد: {new_leads}\n"
                            f"صفقات جديدة: {new_deals}\n"
                            f"تاريخ: {today.isoformat()}"
                        ),
                    )
                    db.add(notification)
                    logger.info("Daily report created for tenant %s: %d leads, %d deals",
                              tenant.name, new_leads, new_deals)
            except Exception as e:
                logger.error("Failed daily report for tenant %s: %s", tenant.id, e)

        await db.commit()


async def _notify_user(user_id: str, title: str, body: str, notification_type: str):
    """Create an in-app notification for a user."""
    async with async_session() as db:
        from app.models.user import User
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            logger.warning("Cannot notify user %s: not found", user_id)
            return

        notification = Notification(
            tenant_id=user.tenant_id,
            user_id=user.id,
            type=notification_type,
            title=title,
            body=body,
        )
        db.add(notification)
        await db.commit()
        logger.info("Notification created for user %s: %s", user_id, title)


@celery_app.task(name="app.workers.notification_tasks.send_daily_report")
def send_daily_report():
    """Generate and send daily sales report to all active tenants."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_send_daily_report())
    finally:
        loop.close()
    return {"status": "ok"}


@celery_app.task(name="app.workers.notification_tasks.notify_user")
def notify_user(user_id: str, title: str, body: str, notification_type: str = "info"):
    """Create an in-app notification for a user."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_notify_user(user_id, title, body, notification_type))
    finally:
        loop.close()
    return {"status": "ok"}
