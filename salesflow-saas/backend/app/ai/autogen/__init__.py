"""
Microsoft AutoGen (AgentChat) — تنسيق فرق وكلاء متعددين، RoundRobin، Selector، وتعلّم من المحادثات.

التهيئة: `dealix_autogen_openai_client()` و`dealix_assistant_agent()`.
يُفضّل تشغيل الحلقات الذاتية التحسين من `app.flows.self_improvement_flow` مع وكلاء AutoGen كطبقة تنفيذ.
"""

from app.ai.autogen.factory import (
    dealix_assistant_agent,
    dealix_autogen_openai_client,
    is_autogen_available,
)

__all__ = [
    "dealix_assistant_agent",
    "dealix_autogen_openai_client",
    "is_autogen_available",
]
