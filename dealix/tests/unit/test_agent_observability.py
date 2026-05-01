"""Unit tests for Agent Observability."""

from __future__ import annotations

from auto_client_acquisition.agent_observability import (
    CostTracker,
    build_trace_event,
    run_eval_pack,
    safety_eval,
    saudi_tone_eval,
)


# ── Trace events ─────────────────────────────────────────────
def test_trace_event_hashes_user_id():
    e = build_trace_event(
        workflow_name="first_10", agent_name="scout",
        user_id="user_real_42", company_id="acme",
    )
    assert e["user_id_hash"] != "user_real_42"
    assert e["company_id_hash"] != "acme"
    assert len(str(e["user_id_hash"])) == 16


def test_trace_event_redacts_payload_secrets():
    e = build_trace_event(
        workflow_name="x", agent_name="y",
        payload={"token": "ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1234"},
    )
    assert "ghp_AAAA" not in str(e.get("payload"))


# ── Safety eval ──────────────────────────────────────────────
def test_safety_blocks_guarantee():
    out = safety_eval("ضمان 100% نتائج مضمونة")
    assert out["verdict"] in ("blocked", "needs_review")


def test_safety_safe_for_clean_text():
    out = safety_eval("هلا أحمد، لاحظت توسعكم. يناسبك أعرض لك Pilot؟")
    assert out["verdict"] == "safe"
    assert out["score"] >= 70


def test_safety_blocks_medical_claim():
    """Medical claims should at minimum require human review (and ideally block)."""
    out = safety_eval("هذا المنتج يعالج السكر ويشفي الضغط بدون أدوية.")
    assert out["verdict"] in ("blocked", "needs_review")
    assert any(v["category"] == "medical_claim" for v in out["violations"])


# ── Saudi tone eval ──────────────────────────────────────────
def test_tone_natural_for_friendly_arabic():
    text = ("هلا أحمد، لاحظت توسعكم في فريق المبيعات. "
            "يناسبك أعرض لك Pilot 7 أيام؟")
    out = saudi_tone_eval(text)
    assert out["verdict"] in ("natural", "decent")
    assert out["arabic_ratio"] > 0.5


def test_tone_off_for_too_corporate():
    text = "تحية طيبة وبعد، ندعوكم لاكتشاف synergy و best-in-class."
    out = saudi_tone_eval(text)
    assert out["verdict"] == "off"


def test_tone_off_for_empty():
    out = saudi_tone_eval("")
    assert out["verdict"] == "off"


# ── Eval pack ────────────────────────────────────────────────
def test_eval_pack_runs_all_cases():
    out = run_eval_pack()
    assert out["total"] >= 5
    assert "pass_rate" in out


def test_eval_pack_has_some_passing():
    out = run_eval_pack()
    assert out["passed"] >= 1


# ── Cost tracker ────────────────────────────────────────────
def test_cost_tracker_aggregates():
    t = CostTracker()
    t.record(workflow_name="first_10", provider_key="claude_sonnet",
             task_type="strategic_reasoning", cost_estimate=0.025)
    t.record(workflow_name="first_10", provider_key="claude_haiku",
             task_type="classification", cost_estimate=0.001)
    s = t.summary()
    assert s["runs"] == 2
    assert round(s["total"], 4) == 0.026
    assert s["by_workflow"]["first_10"] > 0
