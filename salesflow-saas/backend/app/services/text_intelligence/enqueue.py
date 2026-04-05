"""Queue hooks — optional Celery; never raises into API handlers."""

from __future__ import annotations

import logging

logger = logging.getLogger("dealix.text_intelligence.enqueue")


def enqueue_lead_text_intel(lead_id: str, tenant_id: str) -> None:
    from app.config import get_settings

    s = get_settings()
    if not getattr(s, "DEALIX_TEXT_INTELLIGENCE_ENABLED", True):
        return
    if not getattr(s, "DEALIX_TEXT_INTEL_ASYNC_DEFAULT", True):
        return
    try:
        from app.workers.text_intel_tasks import process_lead_text_intel

        process_lead_text_intel.delay(lead_id, tenant_id)
    except Exception as e:  # noqa: BLE001 — queue optional in dev
        logger.debug("enqueue_lead_text_intel skipped: %s", e)
