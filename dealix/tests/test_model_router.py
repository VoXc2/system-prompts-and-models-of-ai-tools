"""Model task routing."""

from __future__ import annotations

from auto_client_acquisition.ai.model_router import ModelTask, get_model_route, requires_guardrail


def test_model_routes_exist():
    r = get_model_route(ModelTask.ARABIC_WRITING)
    assert r.task == ModelTask.ARABIC_WRITING
    assert r.eval_metric


def test_high_risk_tasks_require_guardrail():
    assert requires_guardrail(ModelTask.COMPLIANCE_GUARDRAIL) is True
    assert requires_guardrail(ModelTask.STRATEGIC_REASONING) is True


def test_arabic_writing_route():
    r = get_model_route(ModelTask.ARABIC_WRITING)
    assert r.guardrail_required is True


def test_project_understanding_route():
    r = get_model_route(ModelTask.PROJECT_CODE_UNDERSTANDING)
    assert r.quality_tier == "high"
