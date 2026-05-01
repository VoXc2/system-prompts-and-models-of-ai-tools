"""Short-term growth memory stub — replace with decision_memory / DB later."""

from __future__ import annotations

from typing import Any

_MEMORY: list[dict[str, Any]] = []


def record_highlight(entry: dict[str, Any]) -> dict[str, Any]:
    _MEMORY.append(dict(entry))
    return {"stored": True, "size": len(_MEMORY), "demo": True}


def recent_highlights(limit: int = 10) -> dict[str, Any]:
    return {"highlights": list(_MEMORY[-limit:]), "demo": True}
