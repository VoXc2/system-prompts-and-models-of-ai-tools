"""
Sovereign Routing Fabric — Policy-based model lane selection.

Lanes:
  - coding              → DeepSeek / code-optimized model
  - executive_reasoning → Claude / GPT-4o (high reasoning)
  - throughput_drafting → Groq Llama (fast, high volume)
  - arabic_nlp          → Groq with Arabic context
  - fallback            → GPT-4o-mini

Lane selection is driven by:
  1. ModelRoutingConfig in DB (tenant-specific overrides)
  2. Built-in defaults from AGENTS.md provider preferences
  3. Decision type heuristics
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.sovereign import ModelRoutingConfig


LANE_DEFAULTS: dict[str, dict] = {
    "coding": {
        "primary_model": "deepseek-coder",
        "provider": "deepseek",
        "temperature": 0.1,
        "requires_structured_output": True,
    },
    "executive_reasoning": {
        "primary_model": "claude-3-5-sonnet-20241022",
        "provider": "anthropic",
        "temperature": 0.3,
        "requires_structured_output": True,
    },
    "throughput_drafting": {
        "primary_model": "llama-3.1-70b-versatile",
        "provider": "groq",
        "temperature": 0.7,
        "requires_structured_output": False,
    },
    "arabic_nlp": {
        "primary_model": "llama-3.1-70b-versatile",
        "provider": "groq",
        "temperature": 0.4,
        "requires_structured_output": False,
        "arabic_quality_check": True,
    },
    "fallback": {
        "primary_model": "gpt-4o-mini",
        "provider": "openai",
        "temperature": 0.5,
        "requires_structured_output": False,
    },
}

# Map decision types to preferred lanes
DECISION_TYPE_LANE_MAP: dict[str, str] = {
    # M&A / Executive
    "ma_offer":               "executive_reasoning",
    "term_sheet_send":        "executive_reasoning",
    "ic_memo":                "executive_reasoning",
    "board_pack":             "executive_reasoning",
    "partner_activation":     "executive_reasoning",
    "capital_commitment":     "executive_reasoning",
    # Arabic operations
    "arabic_summary":         "arabic_nlp",
    "arabic_classification":  "arabic_nlp",
    "arabic_memo":            "arabic_nlp",
    "arabic_notification":    "arabic_nlp",
    # Coding / tech
    "code_review":            "coding",
    "migration_plan":         "coding",
    # High-volume drafting
    "memo_draft":             "throughput_drafting",
    "outreach_copy":          "throughput_drafting",
    "enrichment":             "throughput_drafting",
    "evidence_aggregation":   "throughput_drafting",
    "lead_scoring":           "throughput_drafting",
    "workflow_kickoff":       "throughput_drafting",
    "dashboard_refresh":      "throughput_drafting",
}


class SovereignRoutingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def select_lane(
        self,
        decision_type: str,
        arabic_required: bool = False,
    ) -> str:
        if arabic_required:
            return "arabic_nlp"
        return DECISION_TYPE_LANE_MAP.get(decision_type, "executive_reasoning")

    async def get_config_for_lane(self, tenant_id: str, lane: str) -> dict:
        """Return active routing config for this lane (DB override or default)."""
        result = await self.db.execute(
            select(ModelRoutingConfig).where(
                ModelRoutingConfig.tenant_id == tenant_id,
                ModelRoutingConfig.lane == lane,
                ModelRoutingConfig.is_active.is_(True),
            ).limit(1)
        )
        config = result.scalar_one_or_none()
        if config:
            return {
                "lane": config.lane,
                "primary_model": config.primary_model,
                "fallback_model": config.fallback_model,
                "provider": config.provider,
                "max_tokens": config.max_tokens,
                "temperature": float(config.temperature) if config.temperature else 0.5,
                "requires_structured_output": config.requires_structured_output,
                "arabic_quality_check": config.arabic_quality_check,
                "hitl_required": config.hitl_required,
                "approval_class": config.approval_class,
                "avg_latency_ms": config.avg_latency_ms,
                "schema_adherence_pct": float(config.schema_adherence_pct) if config.schema_adherence_pct else None,
                "contradiction_rate_pct": float(config.contradiction_rate_pct) if config.contradiction_rate_pct else None,
            }
        return {**LANE_DEFAULTS.get(lane, LANE_DEFAULTS["fallback"]), "lane": lane}

    async def list_all_configs(self, tenant_id: str) -> list[dict]:
        result = await self.db.execute(
            select(ModelRoutingConfig).where(
                ModelRoutingConfig.tenant_id == tenant_id,
            ).order_by(ModelRoutingConfig.lane)
        )
        rows = result.scalars().all()
        configs = []
        for r in rows:
            configs.append({
                "id": str(r.id),
                "lane": r.lane,
                "primary_model": r.primary_model,
                "fallback_model": r.fallback_model,
                "provider": r.provider,
                "is_active": r.is_active,
                "avg_latency_ms": r.avg_latency_ms,
                "schema_adherence_pct": float(r.schema_adherence_pct) if r.schema_adherence_pct else None,
                "contradiction_rate_pct": float(r.contradiction_rate_pct) if r.contradiction_rate_pct else None,
                "arabic_quality_score": float(r.arabic_quality_score) if r.arabic_quality_score else None,
                "cost_per_task_sar": float(r.cost_per_task_sar) if r.cost_per_task_sar else None,
            })
        # Fill missing lanes with defaults
        configured_lanes = {c["lane"] for c in configs}
        for lane, defaults in LANE_DEFAULTS.items():
            if lane not in configured_lanes:
                configs.append({"lane": lane, **defaults, "id": None, "is_active": True, "source": "default"})
        return configs
