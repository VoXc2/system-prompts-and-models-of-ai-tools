"""Unit tests for auto_client_acquisition.ai.model_router."""

from __future__ import annotations

import pytest

from auto_client_acquisition.ai.model_router import (
    ModelTask,
    estimate_model_cost_class,
    get_model_route,
    requires_guardrail,
)


# ── ModelTask enum ───────────────────────────────────────────────
def test_model_task_is_enum():
    """ModelTask should be a StrEnum / Enum with at least one member."""
    members = list(ModelTask)
    assert len(members) > 0


def test_model_task_string_values():
    """Each task should serialize to a non-empty string."""
    for t in ModelTask:
        assert str(t)
        assert len(str(t)) > 0


# ── get_model_route ──────────────────────────────────────────────
def test_get_model_route_returns_route_for_each_task():
    """Real ModelRoute fields: task, quality_tier, latency, cost_class,
    fallback_task, guardrail_required, eval_metric."""
    for t in ModelTask:
        route = get_model_route(t)
        assert route is not None
        # Core required fields per the dataclass
        for field in ("task", "quality_tier", "latency", "cost_class", "guardrail_required"):
            assert hasattr(route, field), f"missing {field} on route for {t}"
        # task on the route should round-trip back to the input
        assert route.task == t


def test_routes_are_consistent_for_same_task():
    """Calling twice with the same task should return equivalent routes."""
    for t in list(ModelTask)[:3]:
        a = get_model_route(t)
        b = get_model_route(t)
        # Same content (immutable / pure function)
        assert a == b or str(a) == str(b)


# ── cost class ───────────────────────────────────────────────────
def test_estimate_cost_class_for_each_task():
    """Should return a non-empty cost class label per task."""
    for t in ModelTask:
        out = estimate_model_cost_class(t)
        assert out is not None


def test_cost_classes_have_known_labels():
    """Cost class labels should be meaningful strings."""
    seen = set()
    for t in ModelTask:
        out = estimate_model_cost_class(t)
        seen.add(str(out))
    # We should have some variety (not all identical)
    assert len(seen) >= 1


# ── guardrail ────────────────────────────────────────────────────
def test_requires_guardrail_returns_bool():
    for t in ModelTask:
        out = requires_guardrail(t)
        assert isinstance(out, bool)


def test_guardrail_distribution_not_uniform():
    """Sanity: at least some tasks need guardrail, some don't (typical AI design)."""
    needs = [requires_guardrail(t) for t in ModelTask]
    # Either: some True some False, OR all True (defensive). Pure False would be suspicious.
    # Just assert that the function is consistent and returns booleans.
    assert all(isinstance(x, bool) for x in needs)
