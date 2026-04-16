"""Route LLM workloads across sovereign lanes with cost/latency/Arabic constraints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.sovereign.schemas import ModelRoutingDecision, SovereignRoutingLane


class RoutingDashboard(BaseModel):
    lanes: dict[str, dict[str, Any]]
    total_requests: int
    avg_latency_ms: float
    avg_cost_usd: float
    schema_adherence_rate: float
    arabic_quality_avg: float


_DEFAULT_LANE_MODELS: dict[SovereignRoutingLane, list[str]] = {
    SovereignRoutingLane.CODING: ["deepseek-coder-v2", "deepseek-chat"],
    SovereignRoutingLane.EXECUTIVE_REASONING: ["claude-3-5-sonnet", "gpt-4o"],
    SovereignRoutingLane.THROUGHPUT_DRAFTING: ["llama-3.1-70b-groq", "mixtral-8x7b-groq"],
    SovereignRoutingLane.ARABIC_NLP: ["gpt-4o-arabic", "llama-3.1-70b-arabic"],
    SovereignRoutingLane.FALLBACK: ["gpt-4o-mini"],
}

_DEFAULT_PROVIDERS: dict[SovereignRoutingLane, str] = {
    SovereignRoutingLane.CODING: "deepseek",
    SovereignRoutingLane.EXECUTIVE_REASONING: "anthropic_openai",
    SovereignRoutingLane.THROUGHPUT_DRAFTING: "groq",
    SovereignRoutingLane.ARABIC_NLP: "openai_groq",
    SovereignRoutingLane.FALLBACK: "openai",
}


class SovereignRoutingFabric:
    def __init__(self) -> None:
        self._lane_models: dict[SovereignRoutingLane, list[str]] = {
            lane: list(models) for lane, models in _DEFAULT_LANE_MODELS.items()
        }
        self._lane_extra: dict[SovereignRoutingLane, dict[str, Any]] = {
            lane: {
                "latency_budget_ms": {SovereignRoutingLane.CODING: 45_000}.get(lane, 120_000),
                "cost_ceiling_usd": 2.5 if lane == SovereignRoutingLane.EXECUTIVE_REASONING else 0.35,
            }
            for lane in SovereignRoutingLane
        }
        self._total_requests = 0
        self._latency_sum = 0.0
        self._cost_sum = 0.0
        self._schema_sum = 0.0
        self._arabic_sum = 0.0
        self._metrics_samples = 0

    def register_lane(self, lane: SovereignRoutingLane, models: list[str]) -> None:
        self._lane_models[lane] = list(models)

    def get_lane_config(self, lane: SovereignRoutingLane) -> dict[str, Any]:
        extra = dict(self._lane_extra.get(lane, {}))
        return {
            "lane": lane.value,
            "models": list(self._lane_models.get(lane, [])),
            **extra,
        }

    def route(self, task_type: str, context: dict[str, Any]) -> ModelRoutingDecision:
        arabic_required = bool(context.get("arabic_quality_required") or context.get("language") == "ar")
        lane = _pick_lane(task_type, context)
        models = self._lane_models.get(lane, _DEFAULT_LANE_MODELS[SovereignRoutingLane.FALLBACK])
        model_id = models[0]
        extra = self._lane_extra.get(lane, {})
        if arabic_required and lane is not SovereignRoutingLane.ARABIC_NLP:
            lane = SovereignRoutingLane.ARABIC_NLP
            models = self._lane_models.get(lane, _DEFAULT_LANE_MODELS[SovereignRoutingLane.ARABIC_NLP])
            model_id = models[0]
            extra = self._lane_extra.get(lane, {})
        self._total_requests += 1
        return ModelRoutingDecision(
            lane=lane,
            model_id=model_id,
            provider=_DEFAULT_PROVIDERS[lane],
            latency_budget_ms=int(extra.get("latency_budget_ms", 120_000)),
            cost_ceiling_usd=float(extra.get("cost_ceiling_usd", 0.5)),
            arabic_quality_required=arabic_required,
        )

    def record_routing_metrics(
        self,
        decision: ModelRoutingDecision,
        actual_latency_ms: float,
        schema_adherence: float,
        contradiction_rate: float,
        arabic_quality_score: float,
        cost_usd: float,
    ) -> None:
        self._latency_sum += actual_latency_ms
        self._cost_sum += cost_usd
        self._schema_sum += schema_adherence
        self._arabic_sum += arabic_quality_score
        self._metrics_samples += 1
        _ = contradiction_rate

    def get_routing_dashboard(self) -> RoutingDashboard:
        m = self._metrics_samples or 1
        lanes_out: dict[str, dict[str, Any]] = {}
        for lane in SovereignRoutingLane:
            lanes_out[lane.value] = self.get_lane_config(lane)
        return RoutingDashboard(
            lanes=lanes_out,
            total_requests=self._total_requests,
            avg_latency_ms=self._latency_sum / m,
            avg_cost_usd=self._cost_sum / m,
            schema_adherence_rate=self._schema_sum / m,
            arabic_quality_avg=self._arabic_sum / m,
        )


def _pick_lane(task_type: str, context: dict[str, Any]) -> SovereignRoutingLane:
    tt = task_type.upper()
    if context.get("arabic_quality_required") or context.get("language") == "ar":
        return SovereignRoutingLane.ARABIC_NLP
    if "ARABIC" in tt:
        return SovereignRoutingLane.ARABIC_NLP
    if any(x in tt for x in ("CODE", "REFACTOR", "BUG", "DEV")):
        return SovereignRoutingLane.CODING
    if any(x in tt for x in ("BOARD", "STRATEGY", "EXEC", "MEMO", "MA", "PMI")):
        return SovereignRoutingLane.EXECUTIVE_REASONING
    if any(x in tt for x in ("DRAFT", "BULK", "SEQUENCE", "OUTREACH")):
        return SovereignRoutingLane.THROUGHPUT_DRAFTING
    return SovereignRoutingLane.FALLBACK
