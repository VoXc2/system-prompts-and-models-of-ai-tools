"""
Model Router — intelligently routes tasks to LLM providers with fallback.
مُوجّه النماذج — يرسل كل مهمة لأفضل مزود مع احتياط عند الفشل.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from core.config.models import (
    FALLBACK_CHAIN,
    TASK_ROUTING,
    Provider,
    Task,
)
from core.config.settings import Settings, get_settings
from core.llm.anthropic_client import AnthropicClient
from core.llm.base import LLMClient, LLMResponse, Message
from core.llm.gemini_client import GeminiClient
from core.llm.glm_client import GLMClient
from core.llm.openai_compat import DeepSeekClient, GroqClient, OpenAIClient

logger = logging.getLogger(__name__)


@dataclass
class UsageRecord:
    """Tracks calls/tokens per provider | يتتبع الاستدعاءات والرموز لكل مزود."""

    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    errors: int = 0
    fallbacks_triggered: int = 0


class ModelRouter:
    """
    Routes a Task to the appropriate LLM client with fallback chain.
    يوجّه المهمة إلى عميل النموذج المناسب مع سلسلة احتياط.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._clients: dict[Provider, LLMClient | None] = {}
        self.usage: dict[Provider, UsageRecord] = {p: UsageRecord() for p in Provider}
        self._build_clients()

    # ── Client construction ─────────────────────────────────────
    def _build_clients(self) -> None:
        """Instantiate clients only for providers that have API keys set."""
        s = self.settings

        if s.anthropic_api_key:
            self._clients[Provider.ANTHROPIC] = AnthropicClient(
                api_key=s.anthropic_api_key.get_secret_value(),
                model=s.anthropic_model,
                timeout=s.anthropic_timeout,
            )

        if s.deepseek_api_key:
            self._clients[Provider.DEEPSEEK] = DeepSeekClient(
                api_key=s.deepseek_api_key.get_secret_value(),
                model=s.deepseek_model,
                base_url=s.deepseek_base_url,
            )

        if s.glm_api_key:
            self._clients[Provider.GLM] = GLMClient(
                api_key=s.glm_api_key.get_secret_value(),
                model=s.glm_model,
                base_url=s.glm_base_url,
            )

        if s.google_api_key:
            self._clients[Provider.GEMINI] = GeminiClient(
                api_key=s.google_api_key.get_secret_value(),
                model=s.gemini_model,
            )

        if s.groq_api_key:
            self._clients[Provider.GROQ] = GroqClient(
                api_key=s.groq_api_key.get_secret_value(),
                model=s.groq_model,
                base_url=s.groq_base_url,
            )

        if s.openai_api_key:
            self._clients[Provider.OPENAI] = OpenAIClient(
                api_key=s.openai_api_key.get_secret_value(),
                model=s.openai_model,
                base_url=s.openai_base_url,
            )

        configured = [p.value for p in self._clients]
        logger.info("ModelRouter initialized with providers: %s", configured)

    # ── Public API ──────────────────────────────────────────────
    def available_providers(self) -> list[Provider]:
        """List providers that are actually configured."""
        return list(self._clients.keys())

    def get_client(self, provider: Provider) -> LLMClient | None:
        return self._clients.get(provider)

    async def run(
        self,
        task: Task,
        messages: list[Message] | str,
        *,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        preferred_provider: Provider | None = None,
    ) -> LLMResponse:
        """
        Execute a task through the routing + fallback chain.
        نفّذ المهمة عبر سلسلة التوجيه والاحتياط.
        """
        # Normalize input
        if isinstance(messages, str):
            messages = [Message(role="user", content=messages)]

        primary = preferred_provider or TASK_ROUTING.get(task, Provider.ANTHROPIC)
        chain = [primary] + [p for p in FALLBACK_CHAIN.get(primary, []) if p != primary]

        last_error: Exception | None = None
        for idx, provider in enumerate(chain):
            client = self._clients.get(provider)
            if client is None:
                logger.debug("Skipping unconfigured provider: %s", provider)
                continue

            usage = self.usage[provider]
            try:
                usage.calls += 1
                if idx > 0:
                    self.usage[primary].fallbacks_triggered += 1
                    logger.warning(
                        "Task=%s fallback to provider=%s (primary=%s)",
                        task.value,
                        provider.value,
                        primary.value,
                    )

                response = await client.chat(
                    messages=messages,
                    system=system,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                usage.input_tokens += response.input_tokens
                usage.output_tokens += response.output_tokens
                return response

            except Exception as e:
                usage.errors += 1
                last_error = e
                logger.exception(
                    "Provider=%s failed for task=%s: %s", provider.value, task.value, e
                )
                continue

        raise RuntimeError(f"All providers failed for task {task.value}. Last error: {last_error}")

    def usage_summary(self) -> dict[str, Any]:
        """Human-readable usage summary."""
        return {
            provider.value: {
                "calls": record.calls,
                "input_tokens": record.input_tokens,
                "output_tokens": record.output_tokens,
                "total_tokens": record.input_tokens + record.output_tokens,
                "errors": record.errors,
                "fallbacks_triggered": record.fallbacks_triggered,
            }
            for provider, record in self.usage.items()
        }


# ── Singleton ───────────────────────────────────────────────────
_router_instance: ModelRouter | None = None


def get_router() -> ModelRouter:
    """Global router singleton."""
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter()
    return _router_instance
