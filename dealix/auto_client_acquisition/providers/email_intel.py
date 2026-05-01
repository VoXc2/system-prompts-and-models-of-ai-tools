"""EmailIntelProvider chain — Hunter → Abstract → Noop. PDPL-safe."""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Protocol, runtime_checkable

import httpx

from auto_client_acquisition.providers.base import ProviderResult

log = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


@runtime_checkable
class EmailIntelProvider(Protocol):
    name: str

    def is_available(self) -> bool: ...

    async def find_domain_emails(self, domain: str, *, limit: int = 10) -> ProviderResult: ...

    async def verify(self, email: str) -> ProviderResult: ...


class HunterProvider:
    name = "hunter"

    def is_available(self) -> bool:
        return bool(os.getenv("HUNTER_API_KEY", "").strip())

    async def find_domain_emails(self, domain: str, *, limit: int = 10) -> ProviderResult:
        api_key = os.getenv("HUNTER_API_KEY", "").strip()
        if not api_key:
            return ProviderResult(provider=self.name, status="no_key")
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                r = await client.get(
                    "https://api.hunter.io/v2/domain-search",
                    params={"domain": domain, "limit": limit, "api_key": api_key},
                )
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(provider=self.name, status="http_error", error=str(exc))
        if r.status_code != 200:
            return ProviderResult(
                provider=self.name, status="http_error",
                error=f"HTTP {r.status_code}: {r.text[:200]}",
            )
        body = r.json() or {}
        data: dict[str, Any] = body.get("data") or {}
        return ProviderResult(
            provider=self.name, status="ok",
            data={
                "domain": domain,
                "organization": data.get("organization"),
                "pattern": data.get("pattern"),
                "emails": data.get("emails") or [],
            },
        )

    async def verify(self, email: str) -> ProviderResult:
        api_key = os.getenv("HUNTER_API_KEY", "").strip()
        if not api_key:
            return ProviderResult(provider=self.name, status="no_key")
        if not EMAIL_RE.match(email):
            return ProviderResult(
                provider=self.name, status="ok",
                data={"email": email, "valid": False, "reason": "format"},
            )
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                r = await client.get(
                    "https://api.hunter.io/v2/email-verifier",
                    params={"email": email, "api_key": api_key},
                )
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(provider=self.name, status="http_error", error=str(exc))
        if r.status_code != 200:
            return ProviderResult(
                provider=self.name, status="http_error",
                error=f"HTTP {r.status_code}: {r.text[:200]}",
            )
        body = r.json() or {}
        data = body.get("data") or {}
        return ProviderResult(
            provider=self.name, status="ok",
            data={
                "email": email,
                "valid": data.get("status") == "valid",
                "score": data.get("score"),
                "result": data.get("result"),
                "smtp_check": data.get("smtp_check"),
            },
        )


class AbstractEmailProvider:
    name = "abstract_email"

    def is_available(self) -> bool:
        return bool(os.getenv("ABSTRACT_API_KEY", "").strip())

    async def find_domain_emails(self, domain: str, *, limit: int = 10) -> ProviderResult:
        return ProviderResult(
            provider=self.name, status="unsupported",
            error="Abstract Email API supports verify only — use Hunter for domain search.",
        )

    async def verify(self, email: str) -> ProviderResult:
        api_key = os.getenv("ABSTRACT_API_KEY", "").strip()
        if not api_key:
            return ProviderResult(provider=self.name, status="no_key")
        if not EMAIL_RE.match(email):
            return ProviderResult(
                provider=self.name, status="ok",
                data={"email": email, "valid": False, "reason": "format"},
            )
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    "https://emailvalidation.abstractapi.com/v1/",
                    params={"api_key": api_key, "email": email},
                )
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(provider=self.name, status="http_error", error=str(exc))
        if r.status_code != 200:
            return ProviderResult(
                provider=self.name, status="http_error",
                error=f"HTTP {r.status_code}: {r.text[:200]}",
            )
        body = r.json() or {}
        return ProviderResult(
            provider=self.name, status="ok",
            data={
                "email": email,
                "valid": body.get("deliverability") == "DELIVERABLE",
                "score": body.get("quality_score"),
                "result": body.get("deliverability"),
                "smtp_check": (body.get("is_smtp_valid") or {}).get("value"),
            },
        )


class NoopEmailIntelProvider:
    name = "noop"

    def is_available(self) -> bool:
        return True

    async def find_domain_emails(self, domain: str, *, limit: int = 10) -> ProviderResult:
        return ProviderResult(
            provider=self.name, status="ok",
            data={
                "domain": domain, "organization": None, "pattern": None, "emails": [],
                "hint": "No EmailIntel provider configured. Set HUNTER_API_KEY or ABSTRACT_API_KEY.",
            },
        )

    async def verify(self, email: str) -> ProviderResult:
        return ProviderResult(
            provider=self.name, status="ok",
            data={
                "email": email,
                "valid": EMAIL_RE.match(email) is not None,
                "score": None, "result": "format_only",
                "hint": "No verifier configured — only regex check applied.",
            },
        )


def get_email_intel_chain() -> list[EmailIntelProvider]:
    return [HunterProvider(), AbstractEmailProvider(), NoopEmailIntelProvider()]


async def find_emails_with_chain(domain: str, *, limit: int = 10) -> ProviderResult:
    last: ProviderResult | None = None
    for p in get_email_intel_chain():
        if not p.is_available():
            continue
        result = await p.find_domain_emails(domain, limit=limit)
        if result.status == "ok":
            return result
        last = result
    return last or ProviderResult(provider="none", status="empty")


async def verify_with_chain(email: str) -> ProviderResult:
    last: ProviderResult | None = None
    for p in get_email_intel_chain():
        if not p.is_available():
            continue
        result = await p.verify(email)
        if result.status == "ok":
            return result
        last = result
    return last or ProviderResult(provider="none", status="empty")
