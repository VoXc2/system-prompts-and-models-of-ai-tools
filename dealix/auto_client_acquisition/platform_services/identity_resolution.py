"""Deterministic identity merge demo — no external graph DB."""

from __future__ import annotations

import hashlib
from typing import Any


def resolve_identity_demo(
    *,
    phone: str | None = None,
    email: str | None = None,
    company_hint: str | None = None,
) -> dict[str, Any]:
    parts = "|".join([p or "" for p in (phone, email, company_hint)])
    hid = hashlib.sha256(parts.encode("utf-8")).hexdigest()[:16]
    return {
        "identity_key": f"id_{hid}",
        "signals": {"phone": phone, "email": email, "company_hint": company_hint},
        "note_ar": "دمج تجريبي — ربط CRM وsocial handles لاحقاً.",
        "demo": True,
    }
