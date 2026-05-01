"""
OpenAI-compatible API client — used for DeepSeek, Groq, OpenAI.
عميل متوافق مع OpenAI — يُستخدم لـ DeepSeek و Groq و OpenAI.
"""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.llm.base import LLMClient, LLMResponse, Message


class OpenAICompatClient(LLMClient):
    """Base OpenAI-compatible client (chat/completions endpoint)."""

    provider_name = "openai_compat"

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 60,
    ) -> None:
        super().__init__(api_key=api_key, model=model, base_url=base_url, timeout=timeout)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def chat(
        self,
        messages: list[Message],
        *,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send chat completion via OpenAI-compatible endpoint."""
        full_messages: list[dict[str, str]] = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(m.to_dict() for m in messages)

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": full_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/chat/completions"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError(f"No choices returned from {self.provider_name}")

        first_choice = choices[0]
        message = first_choice.get("message", {})
        content = message.get("content", "") or ""

        usage = data.get("usage", {})
        return LLMResponse(
            content=content,
            provider=self.provider_name,
            model=data.get("model", self.model),
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            finish_reason=first_choice.get("finish_reason"),
            raw=data,
        )


class DeepSeekClient(OpenAICompatClient):
    """DeepSeek client (OpenAI-compatible)."""

    provider_name = "deepseek"

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com/v1",
        timeout: int = 60,
    ) -> None:
        super().__init__(api_key=api_key, model=model, base_url=base_url, timeout=timeout)


class GroqClient(OpenAICompatClient):
    """Groq client (OpenAI-compatible) — runs Llama 3.3 70B, ultra-fast."""

    provider_name = "groq"

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
        base_url: str = "https://api.groq.com/openai/v1",
        timeout: int = 60,
    ) -> None:
        super().__init__(api_key=api_key, model=model, base_url=base_url, timeout=timeout)


class OpenAIClient(OpenAICompatClient):
    """OpenAI client (fallback)."""

    provider_name = "openai"

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 60,
    ) -> None:
        super().__init__(api_key=api_key, model=model, base_url=base_url, timeout=timeout)
