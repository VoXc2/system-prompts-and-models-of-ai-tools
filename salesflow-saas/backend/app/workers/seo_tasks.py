"""Scheduled SEO runs — opt-in via DEALIX_SEO_SCHEDULE_ENABLED."""

from __future__ import annotations

import asyncio
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def seo_scheduled_technical_round() -> dict:
    from app.config import get_settings

    settings = get_settings()
    if not settings.DEALIX_SEO_SCHEDULE_ENABLED or not settings.DEALIX_SEO_ENGINE_ENABLED:
        return {"status": "disabled"}

    async def run() -> dict:
        from sqlalchemy import select

        from app.database import async_session
        from app.models.tenant import Tenant
        from app.services.seo_engine.runner import execute_run

        n = 0
        async with async_session() as db:
            q = await db.execute(select(Tenant).where(Tenant.is_active.is_(True)).limit(15))
            tenants = q.scalars().all()
            for t in tenants:
                try:
                    await execute_run(
                        db,
                        tenant_id=t.id,
                        tenant=t,
                        run_kind="technical_audit",
                        options={"scheduled": True},
                    )
                    n += 1
                except Exception:  # noqa: BLE001
                    logger.exception("seo_scheduled tenant=%s", t.id)
            await db.commit()
        return {"status": "ok", "tenants_processed": n}

    return asyncio.run(run())
