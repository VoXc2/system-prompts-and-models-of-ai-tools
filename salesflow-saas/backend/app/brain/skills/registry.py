"""
Skill registry — maps skill_id → executor + metadata.

Executors are thin wrappers: call existing services when available; otherwise record intent in memory.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.brain.types import SkillRisk


@dataclass(frozen=True)
class SkillDefinition:
    key: str
    description: str
    risk: SkillRisk
    required_permissions: tuple[str, ...]
    max_retries: int = 2
    timeout_seconds: int = 60


SKILL_DEFINITIONS: dict[str, SkillDefinition] = {
    "send_email": SkillDefinition(
        key="send_email",
        description="Queue or send email via configured provider.",
        risk=SkillRisk.MEDIUM,
        required_permissions=("messages:send",),
        max_retries=3,
        timeout_seconds=30,
    ),
    "send_whatsapp_message": SkillDefinition(
        key="send_whatsapp_message",
        description="Send WhatsApp template or session message.",
        risk=SkillRisk.MEDIUM,
        required_permissions=("messages:send",),
        max_retries=2,
        timeout_seconds=45,
    ),
    "create_lead": SkillDefinition(
        key="create_lead",
        description="Create CRM lead record.",
        risk=SkillRisk.LOW,
        required_permissions=("leads:write",),
    ),
    "update_deal": SkillDefinition(
        key="update_deal",
        description="Patch deal stage/value/metadata.",
        risk=SkillRisk.LOW,
        required_permissions=("deals:write",),
    ),
    "generate_report": SkillDefinition(
        key="generate_report",
        description="Build analytics snapshot / PDF payload.",
        risk=SkillRisk.LOW,
        required_permissions=("reports:write", "analytics:read"),
    ),
    "scrape_website": SkillDefinition(
        key="scrape_website",
        description="Fetch public URL (robots-respecting).",
        risk=SkillRisk.HIGH,
        required_permissions=("seo:read",),
        max_retries=1,
        timeout_seconds=20,
    ),
    "analyze_data": SkillDefinition(
        key="analyze_data",
        description="Run deterministic or LLM analysis on structured payload.",
        risk=SkillRisk.MEDIUM,
        required_permissions=("analytics:read",),
    ),
    "generate_content": SkillDefinition(
        key="generate_content",
        description="Draft text with tenant tone.",
        risk=SkillRisk.MEDIUM,
        required_permissions=("knowledge:read",),
    ),
    "schedule_task": SkillDefinition(
        key="schedule_task",
        description="Create activity / Celery ETA task.",
        risk=SkillRisk.LOW,
        required_permissions=("tasks:create",),
    ),
    "notify_user": SkillDefinition(
        key="notify_user",
        description="In-app or webhook notification.",
        risk=SkillRisk.LOW,
        required_permissions=("notifications:send",),
    ),
}


SkillHandler = Callable[[AsyncSession, Any, str, Dict[str, Any]], Awaitable[Dict[str, Any]]]


async def _noop_skill(
    db: AsyncSession,
    tenant_id: Any,
    skill_key: str,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """Placeholder until wired to real services; still observable."""
    return {"status": "recorded", "skill": skill_key, "note": "executor_pending_integration", "context_keys": list(context.keys())}


# Handlers registered at import; swap with real implementations incrementally.
_SKILL_HANDLERS: dict[str, SkillHandler] = {k: _noop_skill for k in SKILL_DEFINITIONS}


def register_skill_handler(skill_key: str, fn: SkillHandler) -> None:
    _SKILL_HANDLERS[skill_key] = fn


def get_skill_definition(skill_key: str) -> Optional[SkillDefinition]:
    return SKILL_DEFINITIONS.get(skill_key)


async def execute_skill(
    db: AsyncSession,
    *,
    tenant_id: Any,
    skill_key: str,
    context: Dict[str, Any],
    agent_permissions: Optional[set[str]] = None,
) -> Dict[str, Any]:
    sd = SKILL_DEFINITIONS.get(skill_key)
    if not sd:
        return {"status": "error", "detail": f"unknown_skill:{skill_key}"}
    if agent_permissions is not None:
        missing = [p for p in sd.required_permissions if p not in agent_permissions]
        if missing:
            return {"status": "forbidden", "missing_permissions": missing}
    handler = _SKILL_HANDLERS.get(skill_key, _noop_skill)
    return await handler(db, tenant_id, skill_key, context)
