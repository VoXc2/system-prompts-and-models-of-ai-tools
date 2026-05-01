"""
Base Agent — shared foundation for all agents.
الفئة الأساسية لكل الوكلاء.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from core.errors import AgentError
from core.llm import get_router
from core.logging import get_logger
from core.utils import generate_id, utcnow

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents.
    Provides: unique id, logging, LLM access, JSON-safe LLM parsing.
    """

    name: str = "base_agent"

    def __init__(self, agent_id: str | None = None) -> None:
        self.agent_id = agent_id or generate_id(self.name)
        self.created_at: datetime = utcnow()
        self.router = get_router()
        self.log = logger.bind(agent=self.name, agent_id=self.agent_id)

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the agent's core work."""
        ...

    # ── Utilities ───────────────────────────────────────────────
    @staticmethod
    def parse_json_response(text: str) -> dict[str, Any]:
        """
        Safely parse JSON from an LLM response that may have prose around it.
        يستخرج JSON بأمان حتى لو كان فيه نص حوله.
        """
        if not text:
            return {}

        # 1. Try raw parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. Try extracting fenced block ```json ... ```
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fenced:
            try:
                return json.loads(fenced.group(1))
            except json.JSONDecodeError:
                pass

        # 3. Try largest {...} block
        largest = re.search(r"\{[\s\S]*\}", text)
        if largest:
            try:
                return json.loads(largest.group(0))
            except json.JSONDecodeError:
                pass

        raise AgentError(f"Could not parse JSON from LLM response: {text[:300]}")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.agent_id}>"
