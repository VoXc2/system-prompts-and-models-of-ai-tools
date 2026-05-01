"""
n8n webhook client — send events to n8n workflows for automation orchestration.
عميل ويبهوك n8n.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.config.settings import get_settings
from core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class N8NResult:
    success: bool
    status_code: int | None = None
    response_data: dict[str, Any] | None = None
    error: str | None = None


class N8NClient:
    """Posts events to an n8n webhook URL."""

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def configured(self) -> bool:
        return bool(self.settings.n8n_webhook_url)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def send_event(self, event_type: str, data: dict[str, Any]) -> N8NResult:
        """POST an event to the configured n8n webhook."""
        if not self.configured:
            return N8NResult(success=False, error="N8N_WEBHOOK_URL not configured")

        url = self.settings.n8n_webhook_url or ""
        payload = {"event": event_type, "data": data}

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                try:
                    data_json = response.json()
                except ValueError:
                    data_json = None

            logger.info("n8n_event_sent", event=event_type, status=response.status_code)
            return N8NResult(
                success=True, status_code=response.status_code, response_data=data_json
            )
        except Exception as e:
            logger.exception("n8n_event_failed", error=str(e))
            return N8NResult(success=False, error=str(e))
