"""Task-based model routing — provider-agnostic, deterministic."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

CostClass = Literal["low", "medium", "high"]


class ModelTask(StrEnum):
    STRATEGIC_REASONING = "strategic_reasoning"
    ARABIC_WRITING = "arabic_writing"
    CLASSIFICATION = "classification"
    COMPLIANCE_GUARDRAIL = "compliance_guardrail"
    PROJECT_CODE_UNDERSTANDING = "project_code_understanding"
    SUMMARIZATION = "summarization"
    EXTRACTION = "extraction"
    FORECASTING = "forecasting"
    CUSTOMER_SUPPORT = "customer_support"
    BULK_ENRICHMENT = "bulk_enrichment"


@dataclass(frozen=True)
class ModelRoute:
    task: ModelTask
    quality_tier: Literal["standard", "high"]
    latency: Literal["low", "medium", "high"]
    cost_class: CostClass
    fallback_task: ModelTask | None
    guardrail_required: bool
    eval_metric: str


def get_model_route(task: ModelTask) -> ModelRoute:
    """Return routing guidance without binding to a vendor model name."""
    table: dict[ModelTask, ModelRoute] = {
        ModelTask.STRATEGIC_REASONING: ModelRoute(
            task, "high", "medium", "high", ModelTask.SUMMARIZATION, True, "decision_accuracy",
        ),
        ModelTask.ARABIC_WRITING: ModelRoute(
            task, "high", "medium", "medium", ModelTask.SUMMARIZATION, True, "arabic_tone_and_grounding",
        ),
        ModelTask.CLASSIFICATION: ModelRoute(
            task, "standard", "low", "low", None, True, "precision_recall",
        ),
        ModelTask.COMPLIANCE_GUARDRAIL: ModelRoute(
            task, "high", "low", "medium", ModelTask.CLASSIFICATION, True, "block_rate_vs_false_positives",
        ),
        ModelTask.PROJECT_CODE_UNDERSTANDING: ModelRoute(
            task, "high", "medium", "high", ModelTask.SUMMARIZATION, True, "grounded_citations",
        ),
        ModelTask.SUMMARIZATION: ModelRoute(
            task, "standard", "low", "low", None, False, "faithfulness",
        ),
        ModelTask.EXTRACTION: ModelRoute(
            task, "standard", "medium", "medium", ModelTask.CLASSIFICATION, True, "field_f1",
        ),
        ModelTask.FORECASTING: ModelRoute(
            task, "high", "high", "high", ModelTask.SUMMARIZATION, True, "forecast_error",
        ),
        ModelTask.CUSTOMER_SUPPORT: ModelRoute(
            task, "standard", "low", "medium", ModelTask.SUMMARIZATION, True, "resolution_rate",
        ),
        ModelTask.BULK_ENRICHMENT: ModelRoute(
            task, "standard", "high", "low", None, False, "cost_per_row",
        ),
    }
    return table.get(task, table[ModelTask.SUMMARIZATION])


def estimate_model_cost_class(task: ModelTask) -> CostClass:
    return get_model_route(task).cost_class


def requires_guardrail(task: ModelTask) -> bool:
    return get_model_route(task).guardrail_required
