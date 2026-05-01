"""Security Curator router — secret redaction + diff inspection."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.security_curator import (
    inspect_diff,
    redact_trace,
    sanitize_tool_output,
    scan_payload,
)

router = APIRouter(prefix="/api/v1/security-curator", tags=["security-curator"])


@router.get("/demo")
async def demo() -> dict[str, Any]:
    """Run the redactor against a synthetic payload (deterministic, no network)."""
    sample = {
        "user_id": "user_42",
        "phone": "+966500000123",
        "email": "ali@example.sa",
        "api_key": "ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1234",
        "openai_key": "sk-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1234",
        "notes": "العميل أحمد رقمه +966599999999 وإيميله ali@example.com",
    }
    scan = scan_payload(sample)
    trace = redact_trace(sample)
    return {
        "scan": scan,
        "trace": trace,
    }


@router.post("/redact")
async def redact(payload: Any = Body(...)) -> dict[str, Any]:
    """Redact secrets + PII from arbitrary JSON payload."""
    return redact_trace(payload)


@router.post("/inspect-diff")
async def inspect_diff_endpoint(
    diff: str = Body(..., embed=True),
) -> dict[str, Any]:
    """Inspect a unified diff for blocked files + secret patterns."""
    return inspect_diff(diff).to_dict()


@router.post("/sanitize-output")
async def sanitize_output(payload: Any = Body(...)) -> dict[str, Any]:
    """Sanitize a tool output before logging or showing it to a human."""
    return sanitize_tool_output(payload)
