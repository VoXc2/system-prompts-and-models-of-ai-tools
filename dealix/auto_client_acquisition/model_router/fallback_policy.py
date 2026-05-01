"""Build a deterministic fallback chain for any task type."""

from __future__ import annotations

from .provider_registry import ALL_PROVIDERS, Provider


def _supports(p: Provider, task_type: str, *, requires_arabic: bool, requires_vision: bool) -> bool:
    if task_type not in p.capabilities:
        return False
    if requires_arabic and not p.supports_arabic:
        return False
    if requires_vision and not p.supports_vision:
        return False
    return True


def build_fallback_chain(
    task_type: str,
    *,
    requires_arabic: bool = False,
    requires_vision: bool = False,
    sensitivity: str = "low",
    primary_key: str | None = None,
) -> list[str]:
    """
    Return an ordered list of provider keys to try for a task.

    Rules:
      - if `primary_key` is supplied and supports the task, it goes first.
      - high-sensitivity workloads prefer KSA-region or self-hosted.
      - among the rest, lower cost_class is preferred.
    """
    candidates = [
        p for p in ALL_PROVIDERS
        if _supports(p, task_type,
                     requires_arabic=requires_arabic,
                     requires_vision=requires_vision)
    ]

    cost_order = {"low": 0, "mid": 1, "high": 2}
    privacy_order = {"self_hosted": 0, "ksa_region": 1, "vendor_cloud": 2}

    if sensitivity == "high":
        candidates.sort(key=lambda p: (
            privacy_order.get(p.privacy_tier, 9),
            cost_order.get(p.cost_class, 9),
        ))
    else:
        candidates.sort(key=lambda p: (
            cost_order.get(p.cost_class, 9),
            privacy_order.get(p.privacy_tier, 9),
        ))

    chain = [p.key for p in candidates]
    if primary_key:
        if primary_key in chain:
            chain.remove(primary_key)
            chain.insert(0, primary_key)
    return chain
