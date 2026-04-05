"""Scheduled lead re-score — opt-in."""

from __future__ import annotations

import asyncio
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def lead_engine_daily_rescore() -> dict:
    from app.config import get_settings

    if not get_settings().DEALIX_LEAD_ENGINE_ENABLED or not get_settings().DEALIX_LEAD_ENGINE_SCHEDULE_ENABLED:
        return {"status": "disabled"}

    async def run() -> dict:
        from sqlalchemy import select

        from app.database import async_session
        from app.models.lead import Lead
        from app.models.tenant import Tenant
        from app.services.lead_engine.orchestrator import recompute_lead

        n = 0
        async with async_session() as db:
            tq = await db.execute(select(Tenant).where(Tenant.is_active.is_(True)).limit(20))
            tenants = tq.scalars().all()
            for t in tenants:
                lq = await db.execute(
                    select(Lead).where(Lead.tenant_id == t.id).order_by(Lead.updated_at.desc()).limit(50)
                )
                for lead in lq.scalars().all():
                    try:
                        await recompute_lead(db, tenant_id=t.id, lead=lead, emit_events=False)
                        n += 1
                    except Exception:  # noqa: BLE001
                        logger.exception("lead_engine rescore lead=%s", lead.id)
            await db.commit()
        return {"status": "ok", "leads_processed": n}

    return asyncio.run(run())
