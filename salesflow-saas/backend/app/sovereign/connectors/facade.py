"""Connector facade: registry, policy-governed outbound calls, audit, and telemetry."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any

import httpx
from pydantic import BaseModel, Field

from app.sovereign.schemas import ActionClass, ConnectorContract, ConnectorHealthStatus

logger = logging.getLogger(__name__)


class ConnectorCallResult(BaseModel):
    success: bool
    status_code: int
    response_data: dict[str, Any] = Field(default_factory=dict)
    latency_ms: float
    retries_used: int
    idempotency_key: str
    audit_id: str


class ConnectorFacade:
    """Single entry for outbound integrations; agents depend on contracts, not vendors."""

    def __init__(self) -> None:
        self._registry: dict[str, ConnectorContract] = {}
        self._idempotency_cache: dict[tuple[str, str], ConnectorCallResult] = {}
        self._connector_execution_approved: dict[str, bool] = {}

    def set_execution_approved(self, connector_id: str, granted: bool) -> None:
        """Policy hook: APPROVAL_REQUIRED connectors need an explicit grant before calls."""
        self._connector_execution_approved[connector_id] = granted

    def register_connector(self, contract: ConnectorContract) -> None:
        self._registry[contract.connector_id] = contract

    def get_connector(self, connector_id: str) -> ConnectorContract:
        if connector_id not in self._registry:
            msg = f"Unknown connector_id: {connector_id}"
            raise KeyError(msg)
        return self._registry[connector_id]

    def list_connectors(self) -> list[ConnectorContract]:
        return list(self._registry.values())

    def _check_approval(self, contract: ConnectorContract) -> bool:
        if contract.approval_policy is ActionClass.FULLY_AUTOMATED:
            return True
        if contract.approval_policy is ActionClass.FORBIDDEN:
            return False
        return self._connector_execution_approved.get(contract.connector_id, False)

    async def execute_connector_call(
        self,
        connector_id: str,
        method: str,
        path: str,
        payload: dict[str, Any],
        idempotency_key: str,
    ) -> ConnectorCallResult:
        contract = self.get_connector(connector_id)
        cache_key = (connector_id, idempotency_key)
        if cache_key in self._idempotency_cache:
            cached = self._idempotency_cache[cache_key]
            logger.info(
                "connector.idempotent_replay",
                extra={
                    "connector_id": connector_id,
                    "idempotency_key": idempotency_key,
                    "audit_id": cached.audit_id,
                },
            )
            return cached

        audit_id = str(uuid.uuid4())
        if not self._check_approval(contract):
            result = ConnectorCallResult(
                success=False,
                status_code=403,
                response_data={"error": "approval_required", "connector_id": connector_id},
                latency_ms=0.0,
                retries_used=0,
                idempotency_key=idempotency_key,
                audit_id=audit_id,
            )
            logger.warning(
                "connector.audit",
                extra={
                    "event": "connector_call_denied",
                    "audit_id": audit_id,
                    "connector_id": connector_id,
                    "method": method,
                    "path": path,
                    "approval_policy": contract.approval_policy.value,
                },
            )
            self._idempotency_cache[cache_key] = result
            return result

        url = path if path.startswith("http") else f"{contract.base_url.rstrip('/')}/{path.lstrip('/')}"
        timeout = httpx.Timeout(contract.timeout_ms / 1000.0)
        headers: dict[str, str] = {contract.idempotency_key_header: idempotency_key}
        retries_used = 0
        started = time.perf_counter()
        last_status = 0
        last_body: dict[str, Any] = {}

        logger.info(
            "connector.audit",
            extra={
                "event": "connector_call_start",
                "audit_id": audit_id,
                "connector_id": connector_id,
                "method": method,
                "path": path,
            },
        )

        max_attempts = contract.retry_policy.max_retries + 1
        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(1, max_attempts + 1):
                try:
                    response = await client.request(method.upper(), url, json=payload, headers=headers)
                    last_status = response.status_code
                    try:
                        last_body = response.json() if response.content else {}
                    except Exception:
                        last_body = {"raw": response.text[:2048]}

                    if last_status in contract.retry_policy.retry_on_status_codes and attempt < max_attempts:
                        retries_used += 1
                        delay = min(
                            contract.retry_policy.backoff_base_seconds * (2 ** (attempt - 1)),
                            contract.retry_policy.backoff_max_seconds,
                        )
                        await asyncio.sleep(delay)
                        continue

                    latency_ms = (time.perf_counter() - started) * 1000.0
                    success = 200 <= last_status < 300
                    result = ConnectorCallResult(
                        success=success,
                        status_code=last_status,
                        response_data=last_body,
                        latency_ms=latency_ms,
                        retries_used=retries_used,
                        idempotency_key=idempotency_key,
                        audit_id=audit_id,
                    )
                    logger.info(
                        "connector.audit",
                        extra={
                            "event": "connector_call_complete",
                            "audit_id": audit_id,
                            "connector_id": connector_id,
                            "status_code": last_status,
                            "retries_used": retries_used,
                            "latency_ms": latency_ms,
                        },
                    )
                    if contract.telemetry_enabled:
                        logger.info(
                            "connector.telemetry",
                            extra={
                                "metric": "connector_call",
                                "connector_id": connector_id,
                                "success": success,
                                "latency_ms": latency_ms,
                                "retries": retries_used,
                            },
                        )
                    self._idempotency_cache[cache_key] = result
                    return result
                except httpx.RequestError as exc:
                    last_status = 0
                    last_body = {"error": type(exc).__name__, "message": str(exc)[:500]}
                    if attempt < max_attempts:
                        retries_used += 1
                        delay = min(
                            contract.retry_policy.backoff_base_seconds * (2 ** (attempt - 1)),
                            contract.retry_policy.backoff_max_seconds,
                        )
                        await asyncio.sleep(delay)
                        continue
                    latency_ms = (time.perf_counter() - started) * 1000.0
                    result = ConnectorCallResult(
                        success=False,
                        status_code=0,
                        response_data=last_body,
                        latency_ms=latency_ms,
                        retries_used=retries_used,
                        idempotency_key=idempotency_key,
                        audit_id=audit_id,
                    )
                    logger.exception(
                        "connector.audit",
                        extra={
                            "event": "connector_call_failed",
                            "audit_id": audit_id,
                            "connector_id": connector_id,
                        },
                    )
                    self._idempotency_cache[cache_key] = result
                    return result

        latency_ms = (time.perf_counter() - started) * 1000.0
        result = ConnectorCallResult(
            success=False,
            status_code=last_status,
            response_data=last_body,
            latency_ms=latency_ms,
            retries_used=retries_used,
            idempotency_key=idempotency_key,
            audit_id=audit_id,
        )
        self._idempotency_cache[cache_key] = result
        return result

    async def get_health_status(self, connector_id: str) -> ConnectorHealthStatus:
        contract = self.get_connector(connector_id)
        url = f"{contract.base_url.rstrip('/')}/"
        started = time.perf_counter()
        try:
            timeout = httpx.Timeout(min(5.0, contract.timeout_ms / 1000.0))
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.head(url, follow_redirects=True)
                latency = (time.perf_counter() - started) * 1000.0
                healthy = response.status_code < 500
                return ConnectorHealthStatus(
                    connector_id=connector_id,
                    healthy=healthy,
                    latency_ms=latency,
                    detail_en=f"HEAD {url} -> {response.status_code}",
                    detail_ar=f"HEAD {url} -> {response.status_code}",
                )
        except Exception as exc:
            return ConnectorHealthStatus(
                connector_id=connector_id,
                healthy=False,
                latency_ms=(time.perf_counter() - started) * 1000.0,
                detail_en=str(exc)[:500],
                detail_ar=str(exc)[:500],
            )

    async def get_all_health(self) -> list[ConnectorHealthStatus]:
        results: list[ConnectorHealthStatus] = []
        for cid in self._registry:
            results.append(await self.get_health_status(cid))
        return results
