"""In-memory decision snippets for demos — replace with DB in production."""

from __future__ import annotations

from typing import Any

_STORE: list[dict[str, Any]] = []


def record_decision(entry: dict[str, Any]) -> dict[str, Any]:
    e = {
        "id": f"dec_{len(_STORE)+1}",
        **entry,
    }
    _STORE.append(e)
    return {"ok": True, "entry": e, "demo": True}


def list_decisions(*, limit: int = 20) -> dict[str, Any]:
    return {"decisions": list(reversed(_STORE[-limit:])), "count": len(_STORE), "demo": True}


def reset_demo_memory() -> None:
    _STORE.clear()
