"""Personal operator in-memory store."""

from __future__ import annotations

from auto_client_acquisition.personal_operator.memory import (
    MemoryType,
    PersonalOperatorMemory,
    add_memory,
    looks_like_secret,
    search_memories,
    summarize_memory,
)


def test_add_and_search_memory():
    store = PersonalOperatorMemory()
    add_memory(store, memory_type=MemoryType.GOAL, title="هدف", body="إطلاق Dealix")
    hits = search_memories(store, "Dealix")
    assert hits


def test_summarize_memory():
    store = PersonalOperatorMemory()
    add_memory(store, memory_type=MemoryType.GOAL, title="a", body="b")
    s = summarize_memory(store)
    assert s["total"] >= 1


def test_secret_blocked():
    store = PersonalOperatorMemory()
    out = add_memory(store, memory_type=MemoryType.GOAL, title="x", body="token sk-123456789012345678901234567890")
    assert out["ok"] is False


def test_looks_like_secret():
    assert looks_like_secret("Bearer abcdefghijklmnopqrstuvwxyz0123456789") is True
    assert looks_like_secret("hello world") is False
