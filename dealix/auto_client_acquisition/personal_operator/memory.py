"""In-memory Personal Operator store — swappable later with Supabase."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class MemoryType(StrEnum):
    PROFILE = "profile"
    GOAL = "goal"
    PREFERENCE = "preference"
    RELATIONSHIP = "relationship"
    OPPORTUNITY = "opportunity"
    DECISION = "decision"
    MEETING = "meeting"
    FOLLOWUP = "followup"
    LAUNCH_NOTE = "launch_note"
    PROJECT_NOTE = "project_note"


_SECRET_PATTERNS = (
    re.compile(r"sk-[a-zA-Z0-9]{20,}", re.I),
    re.compile(r"AIza[0-9A-Za-z\-_]{20,}"),
    re.compile(r"Bearer\s+[a-zA-Z0-9\-_.]{20,}", re.I),
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
    re.compile(r"xox[baprs]-[a-zA-Z0-9\-]{10,}", re.I),
)


@dataclass
class PersonalMemoryItem:
    id: str
    memory_type: MemoryType
    title: str
    body: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PersonalOperatorMemory:
    items: list[PersonalMemoryItem] = field(default_factory=list)

    def add(self, item: PersonalMemoryItem) -> PersonalMemoryItem:
        self.items.append(item)
        return item


def looks_like_secret(text: str) -> bool:
    """Return True if text resembles API keys or private material."""
    for pattern in _SECRET_PATTERNS:
        if pattern.search(text):
            return True
    return False


def add_memory(
    store: PersonalOperatorMemory,
    *,
    memory_type: MemoryType,
    title: str,
    body: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if looks_like_secret(body) or looks_like_secret(title):
        return {
            "ok": False,
            "error": "secret_like_content_blocked",
            "message": "Do not store API keys or tokens in operator memory.",
        }
    item = PersonalMemoryItem(
        id=f"mem_{uuid4().hex[:12]}",
        memory_type=memory_type,
        title=title.strip(),
        body=body.strip(),
        metadata=dict(metadata or {}),
    )
    store.add(item)
    return {"ok": True, "item": _item_to_dict(item)}


def list_memories(store: PersonalOperatorMemory, *, memory_type: MemoryType | None = None) -> list[dict[str, Any]]:
    items = store.items
    if memory_type is not None:
        items = [i for i in items if i.memory_type == memory_type]
    return [_item_to_dict(i) for i in items]


def search_memories(store: PersonalOperatorMemory, query: str, limit: int = 20) -> list[dict[str, Any]]:
    q = query.lower().strip()
    if not q:
        return []
    hits: list[tuple[int, PersonalMemoryItem]] = []
    for item in store.items:
        hay = f"{item.title}\n{item.body}".lower()
        score = sum(hay.count(term) for term in q.split() if len(term) > 1)
        if score:
            hits.append((score, item))
    hits.sort(key=lambda x: x[0], reverse=True)
    return [_item_to_dict(i) for _, i in hits[:limit]]


def summarize_memory(store: PersonalOperatorMemory) -> dict[str, Any]:
    by_type: dict[str, int] = {}
    for item in store.items:
        k = item.memory_type.value
        by_type[k] = by_type.get(k, 0) + 1
    return {
        "total": len(store.items),
        "by_type": by_type,
        "latest_titles": [i.title for i in store.items[-5:]],
    }


def _item_to_dict(item: PersonalMemoryItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "memory_type": item.memory_type.value,
        "title": item.title,
        "body": item.body,
        "created_at": item.created_at.isoformat(),
        "metadata": item.metadata,
    }
