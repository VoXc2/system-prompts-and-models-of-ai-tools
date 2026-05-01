"""
Task Queue — agent tasks lifecycle: requested → approved → executed → done/failed.

Each task is auditable + replayable + revocable (if not yet executed).
The queue is in-memory; production uses a SQL-backed adapter with the
same Protocol.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


class TaskStatus:
    PENDING = "pending"           # waiting in queue
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


ALL_STATUSES: tuple[str, ...] = (
    TaskStatus.PENDING,
    TaskStatus.AWAITING_APPROVAL,
    TaskStatus.APPROVED,
    TaskStatus.REJECTED,
    TaskStatus.EXECUTING,
    TaskStatus.SUCCEEDED,
    TaskStatus.FAILED,
    TaskStatus.CANCELLED,
)


@dataclass
class AgentTask:
    """Single agent task — full lifecycle tracked."""

    task_id: str
    customer_id: str
    agent_id: str            # which of the 11 agents
    action_type: str         # one of orchestrator.policies.ACTION_TYPES
    payload: dict[str, Any]
    status: str = TaskStatus.PENDING
    requires_approval: bool = False
    approval_reason: str | None = None
    correlation_id: str | None = None
    causation_task_id: str | None = None
    parent_workflow_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    approved_at: datetime | None = None
    approved_by: str | None = None
    executed_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    result: dict[str, Any] | None = None
    retries: int = 0
    max_retries: int = 2


@dataclass
class TaskQueue:
    """Lightweight in-memory task queue."""

    tasks: dict[str, AgentTask] = field(default_factory=dict)

    def enqueue(
        self,
        *,
        customer_id: str,
        agent_id: str,
        action_type: str,
        payload: dict[str, Any] | None = None,
        requires_approval: bool = False,
        approval_reason: str | None = None,
        correlation_id: str | None = None,
        causation_task_id: str | None = None,
        parent_workflow_id: str | None = None,
    ) -> AgentTask:
        task = AgentTask(
            task_id=f"tsk_{uuid.uuid4().hex[:24]}",
            customer_id=customer_id,
            agent_id=agent_id,
            action_type=action_type,
            payload=payload or {},
            requires_approval=requires_approval,
            approval_reason=approval_reason,
            correlation_id=correlation_id,
            causation_task_id=causation_task_id,
            parent_workflow_id=parent_workflow_id,
            status=TaskStatus.AWAITING_APPROVAL if requires_approval else TaskStatus.PENDING,
        )
        self.tasks[task.task_id] = task
        return task

    def approve(self, task_id: str, *, approved_by: str) -> AgentTask:
        task = self._get(task_id)
        if task.status != TaskStatus.AWAITING_APPROVAL:
            raise ValueError(f"task {task_id} is not awaiting approval (status={task.status})")
        task.status = TaskStatus.APPROVED
        task.approved_at = datetime.now(timezone.utc).replace(tzinfo=None)
        task.approved_by = approved_by
        return task

    def reject(self, task_id: str, *, rejected_by: str, reason: str = "") -> AgentTask:
        task = self._get(task_id)
        if task.status != TaskStatus.AWAITING_APPROVAL:
            raise ValueError(f"task {task_id} is not awaiting approval (status={task.status})")
        task.status = TaskStatus.REJECTED
        task.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        task.approved_by = rejected_by
        task.error = f"rejected: {reason}" if reason else "rejected"
        return task

    def cancel(self, task_id: str) -> AgentTask:
        task = self._get(task_id)
        if task.status in (TaskStatus.SUCCEEDED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            raise ValueError(f"task {task_id} is already terminal (status={task.status})")
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        return task

    def mark_executing(self, task_id: str) -> AgentTask:
        task = self._get(task_id)
        if task.status not in (TaskStatus.PENDING, TaskStatus.APPROVED):
            raise ValueError(f"cannot execute task in status={task.status}")
        task.status = TaskStatus.EXECUTING
        task.executed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        return task

    def succeed(self, task_id: str, *, result: dict[str, Any]) -> AgentTask:
        task = self._get(task_id)
        task.status = TaskStatus.SUCCEEDED
        task.result = result
        task.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        return task

    def fail(self, task_id: str, *, error: str) -> AgentTask:
        task = self._get(task_id)
        task.error = error
        if task.retries < task.max_retries:
            task.retries += 1
            task.status = TaskStatus.PENDING
        else:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        return task

    # ── Query API ─────────────────────────────────────────────
    def by_status(self, status: str) -> list[AgentTask]:
        return [t for t in self.tasks.values() if t.status == status]

    def for_customer(self, customer_id: str) -> list[AgentTask]:
        return [t for t in self.tasks.values() if t.customer_id == customer_id]

    def for_workflow(self, workflow_id: str) -> list[AgentTask]:
        return [t for t in self.tasks.values() if t.parent_workflow_id == workflow_id]

    def summary(self, customer_id: str | None = None) -> dict[str, int]:
        out: dict[str, int] = {s: 0 for s in ALL_STATUSES}
        for t in self.tasks.values():
            if customer_id and t.customer_id != customer_id:
                continue
            out[t.status] = out.get(t.status, 0) + 1
        return out

    def _get(self, task_id: str) -> AgentTask:
        if task_id not in self.tasks:
            raise KeyError(f"unknown task: {task_id}")
        return self.tasks[task_id]
