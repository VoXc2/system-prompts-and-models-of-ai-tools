"""Static provider labels for routing display."""

from __future__ import annotations

from typing import Any

_PROVIDERS: list[dict[str, Any]] = [
    {"id": "anthropic", "label": "Anthropic", "tasks_default": ["strategic_reasoning", "arabic_copywriting"]},
    {"id": "openai", "label": "OpenAI", "tasks_default": ["classification", "summarization"]},
    {"id": "google", "label": "Google Gemini", "tasks_default": ["vision_analysis", "meeting_analysis"]},
    {"id": "groq", "label": "Groq", "tasks_default": ["low_cost_bulk", "extraction"]},
]


def list_providers() -> dict[str, Any]:
    return {"providers": list(_PROVIDERS), "demo": True}
