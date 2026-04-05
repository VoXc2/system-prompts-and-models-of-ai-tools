"""Celery tasks — text intelligence pipeline (queue + batch; API stays fast)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def process_lead_text_intel(self, lead_id: str, tenant_id: str) -> dict[str, Any]:
    from app.config import get_settings

    if not get_settings().DEALIX_TEXT_INTELLIGENCE_ENABLED:
        return {"status": "disabled"}

    async def run() -> dict[str, Any]:
        from sqlalchemy import desc, select
        from uuid import UUID

        from app.database import IS_SQLITE, async_session
        from app.models.lead import Lead
        from app.models.message import Message
        from app.services.text_intelligence.service import analyze_arabic_text, strip_raw_for_persistence

        lid_u = UUID(str(lead_id))
        tid_u = UUID(str(tenant_id))
        lid_key = str(lid_u) if IS_SQLITE else lid_u
        tid_key = str(tid_u) if IS_SQLITE else tid_u

        async with async_session() as db:
            lead = await db.get(Lead, lid_key)
            if not lead or str(lead.tenant_id) != str(tid_u):
                return {"status": "not_found"}

            parts: list[str] = []
            if lead.notes:
                parts.append(lead.notes)
            mq = await db.execute(
                select(Message)
                .where(Message.lead_id == lid_key, Message.tenant_id == tid_key)
                .where(Message.direction == "inbound")
                .order_by(desc(Message.created_at))
                .limit(25)
            )
            for m in mq.scalars().all():
                if m.content:
                    parts.append(m.content)

            corpus = "\n".join(parts).strip()
            if len(corpus) < 4:
                return {"status": "skipped", "reason": "no_text"}

            intel = analyze_arabic_text(corpus, context="lead_pipeline", input_kind="lead_aggregate")
            stored = strip_raw_for_persistence(intel)
            stored["lead_summary"] = stored.get("summary", "")
            stored["lead_intent"] = stored.get("intent", "")
            stored["lead_urgency"] = stored.get("urgency_level", "")
            stored["lead_signals"] = stored.get("opportunity_signals", [])
            stored["lead_score"] = stored.get("lead_score_estimate", 0)

            lead.text_intelligence = stored
            meta = lead.extra_metadata if isinstance(lead.extra_metadata, dict) else {}
            meta = {**meta, "text_intel": {"intent": stored.get("lead_intent"), "urgency": stored.get("lead_urgency")}}
            lead.extra_metadata = meta

            await db.flush()

            if get_settings().DEALIX_TEXT_INTEL_LEAD_ENGINE_HOOK and get_settings().DEALIX_LEAD_ENGINE_ENABLED:
                try:
                    from app.services.lead_engine.orchestrator import recompute_lead

                    await recompute_lead(
                        db,
                        tenant_id=tid_u,
                        lead=lead,
                        emit_events=True,
                    )
                except Exception:
                    logger.exception("lead_engine recompute after text_intel failed lead=%s", lead_id)

            await db.commit()
            return {"status": "ok", "lead_id": lead_id}

    try:
        return asyncio.run(run())
    except Exception as exc:
        logger.exception("process_lead_text_intel failed")
        raise self.retry(exc=exc) from exc


@shared_task
def process_market_insights_batch(tenant_id: str, scope: str, text_chunks: list[str]) -> dict[str, Any]:
    """Batch market/competitor analysis — chunks should be pre-trimmed; no raw persistence here."""
    from uuid import UUID

    from app.config import get_settings
    from app.database import async_session
    from app.models.text_intelligence import TextIntelligenceMarketInsight
    from app.services.text_intelligence.service import analyze_market_corpus

    if not get_settings().DEALIX_TEXT_INTELLIGENCE_ENABLED:
        return {"status": "disabled"}

    agg = analyze_market_corpus(text_chunks, scope=scope)

    async def persist() -> None:
        async with async_session() as db:
            row = TextIntelligenceMarketInsight(
                tenant_id=UUID(str(tenant_id)),
                scope=scope[:120],
                insights_json=agg,
                source_fingerprint=agg.get("source_fingerprint"),
            )
            db.add(row)
            await db.commit()

    asyncio.run(persist())
    return {"status": "ok", "scope": scope}
