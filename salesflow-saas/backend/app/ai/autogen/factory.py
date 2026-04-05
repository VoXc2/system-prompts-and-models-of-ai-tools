"""
مصنع AutoGen — عميل OpenAI-متوافق (OpenAI أو Groq) + وكيل مساعد جاهز للتوسّع إلى فرق متعددة.

مرجع: https://microsoft.github.io/autogen/stable/
"""

from __future__ import annotations

from typing import Any

from app.config import Settings, get_settings


def is_autogen_available() -> bool:
    try:
        import autogen_agentchat  # noqa: F401
        import autogen_ext  # noqa: F401

        return True
    except ImportError:
        return False


def dealix_autogen_openai_client(settings: Settings | None = None) -> Any | None:
    """
    يعيد OpenAIChatCompletionClient لـ AutoGen.
    - إن وُجد OPENAI_API_KEY → واجهة OpenAI الرسمية.
    - وإلا إن وُجد GROQ_API_KEY → Groq عبر base_url المتوافق مع OpenAI.
    """
    if not is_autogen_available():
        return None
    from autogen_ext.models.openai import OpenAIChatCompletionClient

    s = settings or get_settings()
    if (s.OPENAI_API_KEY or "").strip():
        return OpenAIChatCompletionClient(
            model=s.OPENAI_MODEL,
            api_key=s.OPENAI_API_KEY.strip(),
        )
    if (s.GROQ_API_KEY or "").strip():
        return OpenAIChatCompletionClient(
            model=s.GROQ_MODEL,
            api_key=s.GROQ_API_KEY.strip(),
            base_url="https://api.groq.com/openai/v1",
        )
    return None


def dealix_assistant_agent(
    name: str,
    system_message: str,
    *,
    settings: Settings | None = None,
) -> Any | None:
    """وكيل مساعد واحد — نقطة انطلاق لـ RoundRobinGroupChat / MagenticOne لاحقاً."""
    if not is_autogen_available():
        return None
    from autogen_agentchat.agents import AssistantAgent

    client = dealix_autogen_openai_client(settings)
    if client is None:
        return None
    return AssistantAgent(
        name=name,
        model_client=client,
        system_message=system_message,
    )
