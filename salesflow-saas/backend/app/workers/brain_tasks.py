"""Celery tasks — Brain OS dispatch + daily learning (parallel workers, queue scaling)."""

from __future__ import annotations

import asyncio
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def brain_dispatch_agent_chain(
    self,
    tenant_id: str,
    event_type: str,
    payload: dict,
    lead_id: str | None = None,
    conversation_id: str | None = None,
):
    """Delegates to existing agent event executor — no duplicate LLM stack."""
    from app.workers.agent_tasks import execute_event_sync

    try:
        return execute_event_sync(
            event_type,
            payload,
            tenant_id=tenant_id,
            lead_id=lead_id,
            conversation_id=conversation_id,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("brain_dispatch_agent_chain failed")
        raise self.retry(exc=exc)


@shared_task
def brain_daily_learning() -> dict:
    """Per-tenant learning snapshot + suggestion row; scales with tenant count (batch DB)."""

    async def run() -> dict:
        from sqlalchemy import select

        from app.database import async_session
        from app.brain.learning_loop import connect_self_improvement_signals, run_daily_learning_snapshot
        from app.models.tenant import Tenant

        processed = 0
        first_tid: str | None = None
        async with async_session() as db:
            q = await db.execute(select(Tenant).where(Tenant.is_active.is_(True)).limit(100))
            tenants = q.scalars().all()
            for t in tenants:
                if first_tid is None:
                    first_tid = str(t.id)
                await run_daily_learning_snapshot(db, t.id)
                processed += 1
            await db.commit()
        if first_tid:
            try:
                connect_self_improvement_signals(first_tid, bottlenecks=[])
            except Exception:  # noqa: BLE001
                logger.exception("self_improvement_signals")
        return {"status": "ok", "tenants_processed": processed}

    return asyncio.run(run())
