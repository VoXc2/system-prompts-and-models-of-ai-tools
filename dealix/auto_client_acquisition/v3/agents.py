"""Safe AI Agent Runtime for Dealix v3.

This is intentionally deterministic and policy-first. It can later be backed by
LangGraph, OpenAI Agents SDK, CrewAI, or Google ADK without changing the public
contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from uuid import uuid4


class AgentName(StrEnum):
    PROSPECTING = "prospecting"
    SIGNAL = "signal"
    ENRICHMENT = "enrichment"
    PERSONALIZATION = "personalization"
    COMPLIANCE = "compliance"
    OUTREACH = "outreach"
    REPLY = "reply"
    MEETING = "meeting"
    DEAL_COACH = "deal_coach"
    CUSTOMER_SUCCESS = "customer_success"
    EXECUTIVE_ANALYST = "executive_analyst"


class TaskStatus(StrEnum):
    CREATED = "created"
    NEEDS_APPROVAL = "needs_approval"
    APPROVED = "approved"
    EXECUTED = "executed"
    REJECTED = "rejected"
    BLOCKED = "blocked"


@dataclass
class AgentTask:
    agent: AgentName
    objective: str
    customer_id: str
    context: dict[str, Any] = field(default_factory=dict)
    requires_approval: bool = True
    risk_level: str = "medium"
    task_id: str = field(default_factory=lambda: f"task_{uuid4().hex[:12]}")
    status: TaskStatus = TaskStatus.CREATED

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent": self.agent.value,
            "objective": self.objective,
            "customer_id": self.customer_id,
            "context": self.context,
            "requires_approval": self.requires_approval,
            "risk_level": self.risk_level,
            "status": self.status.value,
        }


class SafeAgentRuntime:
    """Small policy-first runtime for agent tasks."""

    restricted_actions = {"send_cold_whatsapp", "auto_linkedin_dm", "delete_data", "export_pii"}

    def __init__(self) -> None:
        self.tasks: dict[str, AgentTask] = {}

    def create_task(self, task: AgentTask) -> AgentTask:
        action = str(task.context.get("action", ""))
        if action in self.restricted_actions:
            task.status = TaskStatus.BLOCKED
            task.risk_level = "blocked"
        elif task.requires_approval:
            task.status = TaskStatus.NEEDS_APPROVAL
        else:
            task.status = TaskStatus.APPROVED
        self.tasks[task.task_id] = task
        return task

    def approve(self, task_id: str) -> AgentTask:
        task = self.tasks[task_id]
        if task.status == TaskStatus.BLOCKED:
            return task
        task.status = TaskStatus.APPROVED
        return task

    def reject(self, task_id: str) -> AgentTask:
        task = self.tasks[task_id]
        task.status = TaskStatus.REJECTED
        return task

    def execute(self, task_id: str) -> dict[str, Any]:
        task = self.tasks[task_id]
        if task.status not in {TaskStatus.APPROVED, TaskStatus.EXECUTED}:
            return {"ok": False, "task": task.to_dict(), "reason": "approval_required_or_blocked"}
        task.status = TaskStatus.EXECUTED
        return {
            "ok": True,
            "task": task.to_dict(),
            "result": {
                "summary": f"{task.agent.value} completed objective: {task.objective}",
                "next_step": "record_outcome_in_revenue_memory",
            },
        }


def agent_catalog() -> list[dict[str, str]]:
    return [
        {"agent": AgentName.PROSPECTING.value, "job": "Find high-fit Saudi B2B accounts."},
        {"agent": AgentName.SIGNAL.value, "job": "Detect why-now buying triggers."},
        {"agent": AgentName.ENRICHMENT.value, "job": "Complete company/contact context."},
        {"agent": AgentName.PERSONALIZATION.value, "job": "Draft Arabic/English outreach."},
        {"agent": AgentName.COMPLIANCE.value, "job": "Block unsafe PDPL/contactability actions."},
        {"agent": AgentName.OUTREACH.value, "job": "Queue or send approved messages."},
        {"agent": AgentName.REPLY.value, "job": "Classify replies and intent."},
        {"agent": AgentName.MEETING.value, "job": "Convert positive replies into meetings."},
        {"agent": AgentName.DEAL_COACH.value, "job": "Recommend next best deal action."},
        {"agent": AgentName.CUSTOMER_SUCCESS.value, "job": "Prevent churn and surface expansion."},
        {"agent": AgentName.EXECUTIVE_ANALYST.value, "job": "Write founder daily brief."},
    ]
