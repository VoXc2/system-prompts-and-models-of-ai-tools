"""
Base LLM abstraction — unified interface across all providers.
واجهة موحدة لجميع مزودي النماذج اللغوية.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["system", "user", "assistant"]


@dataclass
class Message:
    """A conversation message | رسالة محادثة."""

    role: Role
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class LLMResponse:
    """Standardized LLM response | رد موحد من النموذج."""

    content: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    finish_reason: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class LLMClient(ABC):
    """Abstract LLM client | عميل نموذج لغوي مجرد."""

    provider_name: str = "base"

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str | None = None,
        timeout: int = 60,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        *,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send a chat completion request | أرسل طلب محادثة."""
        ...

    async def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """Convenience wrapper — returns just the string content."""
        messages = [Message(role="user", content=prompt)]
        response = await self.chat(
            messages, max_tokens=max_tokens, temperature=temperature, system=system
        )
        return response.content
