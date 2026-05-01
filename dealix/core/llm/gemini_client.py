"""
Google Gemini client — research, multimodal, long context.
عميل Gemini — للبحث والتحليل متعدد الوسائط.
"""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.llm.base import LLMClient, LLMResponse, Message


class GeminiClient(LLMClient):
    """Google Gemini client using the generativelanguage REST API."""

    provider_name = "gemini"
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-pro",
        base_url: str | None = None,
        timeout: int = 60,
    ) -> None:
        super().__init__(
            api_key=api_key,
            model=model,
            base_url=base_url or self.BASE_URL,
            timeout=timeout,
        )

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
        """Send messages to Gemini generateContent endpoint."""
        # Convert messages to Gemini format
        contents: list[dict[str, Any]] = []
        for msg in messages:
            role = "user" if msg.role in ("user", "system") else "model"
            contents.append({"role": role, "parts": [{"text": msg.content}]})

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return LLMResponse(content="", provider=self.provider_name, model=self.model, raw=data)

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)

        usage = data.get("usageMetadata", {})
        return LLMResponse(
            content=text,
            provider=self.provider_name,
            model=self.model,
            input_tokens=usage.get("promptTokenCount", 0),
            output_tokens=usage.get("candidatesTokenCount", 0),
            finish_reason=candidates[0].get("finishReason"),
            raw=data,
        )
