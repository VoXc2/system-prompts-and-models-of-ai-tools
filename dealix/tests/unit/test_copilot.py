"""Smoke tests for the Copilot (intent router + answer engine + safe actions)."""

from __future__ import annotations

from auto_client_acquisition.copilot import ask
from auto_client_acquisition.copilot.answer_engine import answer, explain_metric
from auto_client_acquisition.copilot.intent_router import (
    INTENTS,
    classify_intent,
    list_intents,
)
from auto_client_acquisition.copilot.safe_actions import (
    SAFE_ACTIONS,
    get_action,
    propose_actions,
)


# ── Intent router ────────────────────────────────────────────────
def test_classify_what_to_do_today():
    intent = classify_intent("وش أسوي اليوم؟")
    assert intent.intent_id == "what_to_do_today"
    assert intent.confidence > 0.5


def test_classify_revenue_leaks():
    intent = classify_intent("أين المال يتسرب؟")
    assert intent.intent_id == "show_revenue_leaks"


def test_classify_forecast():
    intent = classify_intent("كم متوقع pipeline لـ 30 يوم؟")
    assert intent.intent_id == "forecast_revenue"


def test_classify_compliance():
    intent = classify_intent("لماذا حُظر هذا التواصل بسبب PDPL؟")
    assert intent.intent_id == "explain_compliance_block"


def test_classify_at_risk():
    intent = classify_intent("أعرض الصفقات المعرضة للخطر")
    assert intent.intent_id == "show_at_risk_deals"


def test_classify_stop():
    intent = classify_intent("أوقف autopilot")
    assert intent.intent_id == "stop_or_disable"


def test_classify_unknown_falls_back_to_general():
    intent = classify_intent("xkcdq")
    assert intent.intent_id == "general_help"
    assert intent.confidence < 0.5


def test_classify_empty_string():
    intent = classify_intent("")
    assert intent.intent_id == "general_help"


def test_intent_taxonomy_no_dupes():
    assert len(INTENTS) == len(set(INTENTS))


def test_list_intents_has_all():
    listed = list_intents()
    assert len(listed) == len(INTENTS)


# ── Answer engine ────────────────────────────────────────────────
def test_answer_what_to_do_today_includes_decisions():
    intent = classify_intent("وش أسوي اليوم؟")
    a = answer(intent=intent, question_ar="وش أسوي؟", customer_id="c1",
               context={"n_high_priority_leads": 8, "n_active_leaks": 3})
    assert "أهم 3 قرارات" in a.answer_ar or "قرارات" in a.answer_ar
    assert a.confidence > 0.7
    assert a.citations


def test_answer_revenue_leaks_cites_leak_detector():
    intent = classify_intent("أين المال؟")
    a = answer(intent=intent, question_ar="?", customer_id="c1", context={})
    assert any(c.reference.startswith("leak_detector") for c in a.citations)


def test_answer_explain_metric():
    a = explain_metric(metric_name="reply_rate", value=0.082, benchmark_p50=0.07, customer_id="c1")
    assert "reply_rate" in a.answer_ar
    assert "8.2" in a.answer_ar
    assert a.confidence > 0.5


def test_answer_general_help_for_unknown():
    intent = classify_intent("hello")
    a = answer(intent=intent, question_ar="hello", customer_id="c1", context={})
    # Should give general help text
    assert len(a.answer_ar) > 50


# ── Safe actions ─────────────────────────────────────────────────
def test_propose_actions_for_what_to_do():
    intent = classify_intent("وش أسوي اليوم؟")
    actions = propose_actions(intent=intent, customer_id="c1", context={})
    assert len(actions) >= 1
    assert any(a.action_id == "run_daily_growth" for a in actions)


def test_propose_actions_for_compliance():
    intent = classify_intent("لماذا حُظر؟ PDPL")
    actions = propose_actions(intent=intent, customer_id="c1", context={})
    assert any(a.action_id == "explain_block" for a in actions)


def test_propose_actions_general_falls_back():
    intent = classify_intent("xyz")
    actions = propose_actions(intent=intent, customer_id="c1", context={})
    assert len(actions) >= 1


def test_get_action_by_id():
    a = get_action("run_daily_growth")
    assert a is not None
    assert a.workflow_id == "daily_growth_run"


def test_get_action_unknown_returns_none():
    assert get_action("nonexistent") is None


def test_safety_classes_known():
    valid = {"read_only", "draft_only", "write_with_approval", "autonomous"}
    for a in SAFE_ACTIONS:
        assert a.safety_class in valid


# ── End-to-end ask() ─────────────────────────────────────────────
def test_ask_e2e_returns_full_response():
    out = ask(question_ar="وش أسوي اليوم؟", customer_id="c1",
              context={"n_high_priority_leads": 8, "n_active_leaks": 3})
    assert out["intent"] == "what_to_do_today"
    assert out["answer_ar"]
    assert out["confidence"] > 0
    assert isinstance(out["proposed_actions"], list)
    assert len(out["proposed_actions"]) >= 1


def test_ask_e2e_compliance_question():
    out = ask(question_ar="لماذا حُظر هذا الإيميل بسبب PDPL؟", customer_id="c1",
              context={"block_reason": "no_consent", "n_blocked": 5})
    assert out["intent"] == "explain_compliance_block"
    assert "PDPL" in out["answer_ar"] or "حُظ" in out["answer_ar"]
