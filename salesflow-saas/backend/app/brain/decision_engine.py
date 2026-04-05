"""Decision engine — scores + rule-based actions (wraps ReasoningRule when rows exist)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.second_brain import ReasoningRule


@dataclass
class DecisionScores:
    risk: float
    priority: float
    opportunity: float
    urgency: float
    confidence: float


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def score_event_payload(event_type: str, payload: Dict[str, Any]) -> DecisionScores:
    """Heuristic baseline when no ML — tuned for CRM signals."""
    risk = 20.0
    urgency = 25.0
    opportunity = 40.0
    priority = 30.0
    confidence = 70.0

    et = event_type.lower()
    if "error" in et or "failed" in et:
        risk = 75.0
        urgency = 80.0
        confidence = 50.0
    if "payment" in et and "fail" in et:
        risk = 90.0
        urgency = 85.0
    if "deal" in et and "won" in et:
        opportunity = 95.0
        priority = 70.0
    if "lead" in et and "created" in et:
        opportunity = 65.0
        urgency = 45.0
    if "whatsapp" in et or "message" in et:
        urgency = max(urgency, 55.0)

    # Payload hints
    if payload.get("value_sar"):
        try:
            v = float(payload["value_sar"])
            if v > 500_000:
                opportunity += 15.0
                priority += 10.0
        except (TypeError, ValueError):
            pass

    return DecisionScores(
        risk=_clamp(risk),
        priority=_clamp(priority),
        opportunity=_clamp(opportunity),
        urgency=_clamp(urgency),
        confidence=_clamp(confidence),
    )


async def load_enabled_rules(db: AsyncSession, tenant_id: UUID) -> List[ReasoningRule]:
    q = await db.execute(
        select(ReasoningRule)
        .where(ReasoningRule.tenant_id == tenant_id, ReasoningRule.enabled.is_(True))
        .order_by(ReasoningRule.priority.asc())
    )
    return list(q.scalars().all())


def rule_actions_for_scores(
    scores: DecisionScores,
    rules: List[ReasoningRule],
) -> List[Dict[str, Any]]:
    """Evaluate JSON conditions (subset) — extend as needed."""
    out: List[Dict[str, Any]] = []
    for rule in rules:
        cond = rule.condition or {}
        if not cond:
            continue
        matched = _match_condition(cond, scores)
        if matched:
            for a in rule.actions or []:
                if isinstance(a, dict):
                    out.append(dict(a))
    return out


def _match_condition(cond: Dict[str, Any], scores: DecisionScores) -> bool:
    if "all" in cond:
        items = cond["all"]
        if not items:
            return False
        return all(_match_condition(c, scores) if isinstance(c, dict) else False for c in items)
    if "any" in cond:
        items = cond["any"]
        if not items:
            return False
        return any(_match_condition(c, scores) if isinstance(c, dict) else False for c in items)
    metric = cond.get("metric")
    op = cond.get("op")
    value = cond.get("value")
    if metric and op is not None and value is not None:
        cur = getattr(scores, str(metric), None)
        if cur is None:
            return False
        if op == "gt":
            return float(cur) > float(value)
        if op == "gte":
            return float(cur) >= float(value)
        if op == "lt":
            return float(cur) < float(value)
        if op == "lte":
            return float(cur) <= float(value)
    return False


def suggest_agents_for_event(event_type: str, scores: DecisionScores) -> List[str]:
    """Route to agent keys by event type + scores."""
    agents: List[str] = []
    et = event_type.lower()
    if "lead" in et:
        agents.append("lead_qualification")
    if "follow" in et or "remind" in et:
        agents.append("follow_up")
    if "deal" in et:
        agents.append("sales")
    if "error" in et or "health" in et or "integration" in et:
        agents.append("monitoring")
    if scores.opportunity > 70 or "report" in et:
        agents.append("analytics")
    # Dedup preserve order
    seen = set()
    uniq = []
    for a in agents:
        if a not in seen:
            seen.add(a)
            uniq.append(a)
    return uniq
