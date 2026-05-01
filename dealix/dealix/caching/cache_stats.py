"""
Global cache-stats singleton — lets any module pull hit-rate into /health or
the /admin/costs endpoint without threading a cache object through every call.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from typing import Any

_lock = threading.Lock()
_registry: dict[str, Any] = defaultdict(lambda: None)


def register(name: str, cache: Any) -> None:
    """Register a SemanticCache-like object so stats can be inspected globally."""
    with _lock:
        _registry[name] = cache


def unregister(name: str) -> None:
    with _lock:
        _registry.pop(name, None)


def get_global_stats() -> dict[str, dict[str, float]]:
    """Alias for snapshot() — returns all registered cache stats."""
    return snapshot()


def snapshot() -> dict[str, dict[str, float]]:
    """Return `{cache_name: stats_dict}` for every registered cache."""
    with _lock:
        out: dict[str, dict[str, float]] = {}
        for name, cache in _registry.items():
            stats = getattr(cache, "stats", None)
            if stats is not None and hasattr(stats, "to_dict"):
                out[name] = stats.to_dict()
        return out
