"""Unit tests for the new auto_client_acquisition.model_router."""

from __future__ import annotations

from auto_client_acquisition.model_router import (
    ALL_PROVIDERS,
    ALL_TASK_TYPES,
    build_fallback_chain,
    build_usage_demo,
    classify_cost,
    get_provider,
    route_task,
)


def test_every_task_type_has_at_least_one_provider():
    for tt in ALL_TASK_TYPES:
        chain = build_fallback_chain(tt)
        assert chain, f"no provider for task: {tt}"


def test_provider_registry_contains_essentials():
    keys = {p.key for p in ALL_PROVIDERS}
    for required in ("claude_sonnet", "claude_haiku", "gpt_4_class",
                     "gemini_pro", "azure_oai_ksa"):
        assert required in keys


def test_get_provider_unknown():
    assert get_provider("bogus_key") is None


def test_classify_cost_bulk_is_low():
    assert classify_cost(task_type="low_cost_bulk", bulk=True) == "low"


def test_classify_cost_strategic_is_mid():
    assert classify_cost(task_type="strategic_reasoning") == "mid"


def test_classify_cost_huge_output_is_high():
    assert classify_cost(task_type="summarization",
                         expected_output_tokens=2000) == "high"


def test_high_sensitivity_prefers_ksa_or_local():
    chain = build_fallback_chain(
        "compliance_guardrail", sensitivity="high", requires_arabic=True,
    )
    top_provider = get_provider(chain[0])
    assert top_provider is not None
    assert top_provider.privacy_tier in ("ksa_region", "self_hosted")


def test_route_task_unknown_returns_no_provider():
    d = route_task("totally_made_up")
    assert d.primary_provider is None
    assert d.fallback_chain == []


def test_route_task_arabic_copywriting():
    d = route_task("arabic_copywriting", requires_arabic=True)
    assert d.primary_provider is not None
    assert d.cost_class in ("low", "mid", "high")


def test_route_task_with_primary_override():
    d = route_task("strategic_reasoning", primary_provider="gpt_4_class")
    assert d.fallback_chain[0] == "gpt_4_class"


def test_usage_demo_covers_all_task_types():
    demo = build_usage_demo()
    assert demo["task_types_total"] == len(ALL_TASK_TYPES)
    assert len(demo["routes"]) == len(ALL_TASK_TYPES)
    assert demo["cost_counts"]
