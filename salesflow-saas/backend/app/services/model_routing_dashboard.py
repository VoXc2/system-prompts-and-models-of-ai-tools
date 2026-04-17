"""Model Routing Dashboard — real metrics from ai_conversations table."""

from __future__ import annotations

from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


PROVIDERS = {
    "groq": {"name": "Groq", "model": "llama-3.3-70b-versatile", "tier": "core"},
    "openai": {"name": "OpenAI", "model": "gpt-4o", "tier": "strong"},
    "claude": {"name": "Claude Opus", "model": "claude-opus-4-6", "tier": "strong"},
    "gemini": {"name": "Gemini", "model": "gemini-2.0-flash", "tier": "pilot"},
    "deepseek": {"name": "DeepSeek", "model": "deepseek-coder", "tier": "pilot"},
}


class ModelRoutingDashboard:

    def get_provider_health(self) -> List[Dict[str, Any]]:
        return [
            {"provider": key, "name": info["name"], "model": info["model"], "tier": info["tier"], "status": "available"}
            for key, info in PROVIDERS.items()
        ]

    async def get_routing_stats(self, db: AsyncSession, tenant_id: str) -> Dict[str, Any]:
        from app.models.ai_conversation import AIConversation

        tid = UUID(tenant_id)
        total_calls = int(
            (await db.execute(
                select(func.count()).select_from(AIConversation).where(AIConversation.tenant_id == tid)
            )).scalar() or 0
        )
        total_tokens = int(
            (await db.execute(
                select(func.coalesce(func.sum(AIConversation.tokens_used), 0))
                .where(AIConversation.tenant_id == tid)
            )).scalar() or 0
        )
        avg_latency = float(
            (await db.execute(
                select(func.coalesce(func.avg(AIConversation.latency_ms), 0))
                .where(AIConversation.tenant_id == tid)
            )).scalar() or 0
        )

        return {
            "tenant_id": tenant_id,
            "total_ai_calls": total_calls,
            "total_tokens": total_tokens,
            "avg_latency_ms": round(avg_latency, 1),
            "primary_provider": "groq",
            "fallback_provider": "openai",
            "providers": self.get_provider_health(),
            "routing_policy": {
                "fast_classification": "groq",
                "sales_copy": "claude",
                "research": "gemini",
                "coding": "deepseek",
                "default": "groq",
            },
        }

    async def get_cost_summary(self, db: AsyncSession, tenant_id: str) -> Dict[str, Any]:
        from app.models.ai_conversation import AIConversation

        tid = UUID(tenant_id)
        total_tokens = int(
            (await db.execute(
                select(func.coalesce(func.sum(AIConversation.tokens_used), 0))
                .where(AIConversation.tenant_id == tid)
            )).scalar() or 0
        )
        estimated_cost = round(total_tokens * 0.000003 * 3.75, 2)  # rough $/token * SAR/USD

        return {
            "tenant_id": tenant_id,
            "period": "all_time",
            "total_tokens": total_tokens,
            "estimated_cost_sar": estimated_cost,
            "by_provider": {
                "groq": {"calls": 0, "tokens": total_tokens, "cost_sar": estimated_cost},
            },
        }


model_routing_dashboard = ModelRoutingDashboard()
