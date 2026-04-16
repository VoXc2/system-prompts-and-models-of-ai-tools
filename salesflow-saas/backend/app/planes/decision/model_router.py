"""Model Routing Fabric — benchmark-driven model selection."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ModelProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    model_id: str
    provider: str  # "openai", "anthropic", "groq", "deepseek", "google"
    display_name: str
    tier: str  # "implementation", "architecture", "strategic", "operational", "lightweight"
    capabilities: list[str] = Field(default_factory=list)
    avg_latency_ms: float = 0.0
    success_rate: float = 1.0
    schema_adherence: float = 1.0
    tool_call_reliability: float = 1.0
    contradiction_rate: float = 0.0
    arabic_memo_quality: float = 0.0
    cost_per_1k_tokens: float = 0.0


class BenchmarkResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_id: str
    task_type: str
    latency_ms: float
    success: bool
    schema_adherent: bool
    tool_calls_correct: bool
    arabic_quality_score: float = 0.0
    cost: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelRoutingFabric:
    """Routes tasks to optimal models based on internal benchmarks."""
    
    DEFAULT_PROFILES: list[ModelProfile] = [
        ModelProfile(
            model_id="codex-5.3-high-fast",
            provider="openai",
            display_name="Codex 5.3 High Fast",
            tier="implementation",
            capabilities=["code_generation", "refactoring", "test_writing", "repo_work"],
        ),
        ModelProfile(
            model_id="gpt-5.4-high",
            provider="openai",
            display_name="GPT-5.4 High",
            tier="architecture",
            capabilities=["system_design", "typed_outputs", "executive_memos", "tool_workflows", "structured_outputs"],
        ),
        ModelProfile(
            model_id="opus-4.6-high",
            provider="anthropic",
            display_name="Opus 4.6 High",
            tier="strategic",
            capabilities=["strategic_analysis", "board_synthesis", "comparative_analysis", "complex_reasoning"],
        ),
        ModelProfile(
            model_id="sonnet-4.6-high",
            provider="anthropic",
            display_name="Sonnet 4.6 High",
            tier="operational",
            capabilities=["drafting", "structured_content", "high_throughput", "operational_work"],
        ),
        ModelProfile(
            model_id="groq-llama-3.1-70b",
            provider="groq",
            display_name="Groq Llama 3.1 70B",
            tier="lightweight",
            capabilities=["fast_classification", "arabic_nlp", "intent_detection"],
        ),
    ]
    
    TASK_TIER_MAP: dict[str, str] = {
        "code_generation": "implementation",
        "refactoring": "implementation",
        "test_writing": "implementation",
        "system_design": "architecture",
        "executive_memo": "architecture",
        "structured_output": "architecture",
        "board_pack": "strategic",
        "strategic_comparison": "strategic",
        "ma_valuation": "strategic",
        "drafting": "operational",
        "operational_content": "operational",
        "fast_classification": "lightweight",
        "arabic_nlp": "lightweight",
        "intent_detection": "lightweight",
        "scoring": "lightweight",
    }
    
    def __init__(self):
        self._profiles: dict[str, ModelProfile] = {p.model_id: p for p in self.DEFAULT_PROFILES}
        self._benchmarks: list[BenchmarkResult] = []
    
    def select_model(self, task_type: str) -> ModelProfile:
        tier = self.TASK_TIER_MAP.get(task_type, "operational")
        candidates = [p for p in self._profiles.values() if p.tier == tier]
        if not candidates:
            candidates = [p for p in self._profiles.values() if p.tier == "operational"]
        candidates.sort(key=lambda p: (-p.success_rate, p.avg_latency_ms, p.cost_per_1k_tokens))
        return candidates[0]
    
    def record_benchmark(self, result: BenchmarkResult) -> None:
        self._benchmarks.append(result)
        profile = self._profiles.get(result.model_id)
        if profile:
            recent = [b for b in self._benchmarks if b.model_id == result.model_id][-100:]
            profile.success_rate = sum(1 for b in recent if b.success) / len(recent)
            profile.avg_latency_ms = sum(b.latency_ms for b in recent) / len(recent)
            profile.schema_adherence = sum(1 for b in recent if b.schema_adherent) / len(recent)
            profile.tool_call_reliability = sum(1 for b in recent if b.tool_calls_correct) / len(recent)
            arabic_scores = [b.arabic_quality_score for b in recent if b.arabic_quality_score > 0]
            if arabic_scores:
                profile.arabic_memo_quality = sum(arabic_scores) / len(arabic_scores)
    
    def get_dashboard_data(self) -> dict[str, Any]:
        return {
            "models": [p.model_dump() for p in self._profiles.values()],
            "total_benchmarks": len(self._benchmarks),
            "benchmarks_by_model": {
                mid: len([b for b in self._benchmarks if b.model_id == mid])
                for mid in self._profiles
            },
        }


model_routing_fabric = ModelRoutingFabric()
