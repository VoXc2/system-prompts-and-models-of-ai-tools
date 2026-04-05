"""Agent lifecycle — sessions in DB, state transitions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.brain.profiles import AGENT_PROFILES
from app.brain.types import AgentState
from app.models.brain_runtime import BrainAgentSession, BrainSkillInvocation


async def start_session(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    agent_key: str,
    correlation_id: Optional[str],
    input_payload: Dict[str, Any],
) -> BrainAgentSession:
    if agent_key not in AGENT_PROFILES:
        raise ValueError(f"unknown_agent:{agent_key}")
    row = BrainAgentSession(
        tenant_id=tenant_id,
        agent_key=agent_key,
        state=AgentState.RUNNING.value,
        correlation_id=correlation_id,
        input_payload=input_payload,
        heartbeat_at=datetime.now(timezone.utc),
    )
    db.add(row)
    await db.flush()
    return row


async def transition(
    db: AsyncSession,
    session: BrainAgentSession,
    new_state: AgentState,
    *,
    output_payload: Optional[Dict[str, Any]] = None,
    error_text: Optional[str] = None,
) -> None:
    session.state = new_state.value
    session.heartbeat_at = datetime.now(timezone.utc)
    if output_payload is not None:
        session.output_payload = output_payload
    if error_text is not None:
        session.error_text = error_text
    if new_state in (AgentState.COMPLETED, AgentState.ERROR):
        session.completed_at = datetime.now(timezone.utc)
    await db.flush()


async def record_skill_invocation(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    session_id: UUID,
    skill_key: str,
    status: str,
    attempts: int,
    result: Dict[str, Any],
    error: Optional[str] = None,
) -> BrainSkillInvocation:
    row = BrainSkillInvocation(
        tenant_id=tenant_id,
        session_id=session_id,
        skill_key=skill_key,
        status=status,
        attempts=attempts,
        result=result,
        error=error,
    )
    db.add(row)
    await db.flush()
    return row
