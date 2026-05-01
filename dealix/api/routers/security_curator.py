"""Security curator API — redact and inspect diffs."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.security_curator.patch_firewall import inspect_diff
from auto_client_acquisition.security_curator.secret_redactor import redact_secrets, scan_payload
from auto_client_acquisition.security_curator.trace_redactor import redact_trace_payload

router = APIRouter(prefix="/api/v1/security-curator", tags=["security_curator"])


@router.get("/demo")
async def demo() -> dict[str, Any]:
    return {"ok": True, "message_ar": "طبقة أمان للوكلاء — redaction وفحص فرق قبل التطبيق.", "demo": True}


@router.post("/redact")
async def redact(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    text = str(payload.get("text") or "")
    return {"redacted": redact_secrets(text), "findings": scan_payload(payload)}


@router.post("/inspect-diff")
async def inspect_diff_route(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    diff = str(payload.get("diff_text") or "")
    return inspect_diff(diff)


@router.post("/trace/sanitize")
async def trace_sanitize(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    """Redact nested trace/span metadata before export to observability backends."""
    body = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    return {"sanitized": redact_trace_payload(body or {}), "demo": True}
