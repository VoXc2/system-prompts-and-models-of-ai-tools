"""Brain OS — shared types (no DB)."""

from __future__ import annotations

import enum


class AgentState(str, enum.Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"


class MemoryTier(str, enum.Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    AGENT = "agent"
    SYSTEM = "system"
    USER = "user"


class DecisionAxis(str, enum.Enum):
    RISK = "risk"
    PRIORITY = "priority"
    OPPORTUNITY = "opportunity"
    URGENCY = "urgency"
    CONFIDENCE = "confidence"


class SkillRisk(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
