"""
Orchestrator Runtime — runs agent workflows.

A WorkflowDefinition is a graph of WorkflowSteps. Each step:
  - chooses the agent that runs it
  - declares its action_type
  - takes inputs (often outputs from prior steps)
  - emits AgentTask + RevenueEvent

The Orchestrator handles policy checks, approval gates, retries, and
event emission. It is deterministic given the same inputs + policy.

Key design: agents themselves are pluggable via a `tool_registry` callable.
This means the runtime is testable without spinning up real LLMs / providers.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from auto_client_acquisition.orchestrator.policies import (
    BudgetUsage,
    Policy,
    requires_approval,
    within_budget,
)
from auto_client_acquisition.orchestrator.queue import AgentTask, TaskQueue, TaskStatus
from auto_client_acquisition.revenue_memory.event_store import EventStore
from auto_client_acquisition.revenue_memory.events import RevenueEvent, make_event

log = logging.getLogger(__name__)


# ── Workflow definition ───────────────────────────────────────────
@dataclass
class WorkflowStep:
    step_id: str                 # unique within workflow
    agent_id: str                # which of the 11 agents
    action_type: str             # one of policies.ACTION_TYPES
    inputs_from: tuple[str, ...] = ()  # step_ids whose outputs feed this step
    description: str = ""


@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str
    description: str
    steps: tuple[WorkflowStep, ...]


# ── The flagship workflow: Daily Growth Run ──────────────────────
DAILY_GROWTH_RUN = WorkflowDefinition(
    workflow_id="daily_growth_run",
    name="Daily Growth Run — اكتشاف + تأهيل + إرسال",
    description=(
        "كل صباح: اكتشاف 200 شركة → اختيار 40 بإشارات → enrichment → "
        "compliance check → personalization → human approval → send → "
        "classify replies → تقرير نهاية اليوم."
    ),
    steps=(
        WorkflowStep("1_discover", "prospecting", "discover_leads",
                     description="200 شركة جديدة من Saudi Maps + LinkedIn"),
        WorkflowStep("2_signals", "signal", "discover_leads",
                     ("1_discover",), "اختيار أعلى 40 بإشارات شراء"),
        WorkflowStep("3_enrich", "enrichment", "enrich_lead",
                     ("2_signals",), "تكميل بيانات DM + size + tech"),
        WorkflowStep("4_compliance", "compliance", "draft_message",
                     ("3_enrich",), "فحص PDPL + opt-out قبل أي صياغة"),
        WorkflowStep("5_personalize", "personalization", "draft_message",
                     ("4_compliance",), "صياغة رسالة عربية مخصصة لكل شركة"),
        WorkflowStep("6_send", "outreach", "send_message",
                     ("5_personalize",), "إرسال عبر القناة الأنسب"),
        WorkflowStep("7_classify", "reply", "classify_reply",
                     ("6_send",), "تصنيف كل رد + اقتراح next action"),
        WorkflowStep("8_brief", "executive_analyst", "generate_qbr",
                     ("7_classify",), "تقرير نهاية اليوم"),
    ),
)


# ── Executor signature ────────────────────────────────────────────
ExecutorFunc = Callable[[AgentTask], dict[str, Any]]
"""An executor takes a task, runs it, returns a result dict (or raises)."""


# ── The Orchestrator ──────────────────────────────────────────────
@dataclass
class Orchestrator:
    """Runs workflows + enforces policy + emits events."""

    queue: TaskQueue
    event_store: EventStore
    policy_resolver: Callable[[str], Policy]    # customer_id → Policy
    executor_registry: dict[str, ExecutorFunc]  # action_type → executor
    budget_usage: dict[str, BudgetUsage] = field(default_factory=dict)

    # ── Public API ───────────────────────────────────────────
    def run_workflow(
        self,
        *,
        workflow: WorkflowDefinition,
        customer_id: str,
        initial_inputs: dict[str, Any] | None = None,
        actor: str = "system",
    ) -> dict[str, Any]:
        """
        Plan + dispatch one full workflow run.

        Returns the final summary: tasks created, executed, awaiting_approval, failed.
        """
        correlation_id = f"wf_{uuid.uuid4().hex[:16]}"
        policy = self.policy_resolver(customer_id)
        usage = self.budget_usage.setdefault(customer_id, BudgetUsage())

        created_tasks: list[AgentTask] = []
        outputs: dict[str, dict[str, Any]] = {}
        if initial_inputs:
            outputs["initial"] = initial_inputs

        for step in workflow.steps:
            # Gather inputs from upstream steps
            step_inputs: dict[str, Any] = {}
            for src in step.inputs_from:
                if src in outputs:
                    step_inputs[src] = outputs[src]
            if "initial" in outputs and not step.inputs_from:
                step_inputs["initial"] = outputs["initial"]

            # Build the risk profile for the policy decision
            risks = {
                "is_first_send_to_account": step_inputs.get("is_first_send_to_account", False),
                "deal_value_sar": step_inputs.get("deal_value_sar", 0),
                "contains_legal_topic": step_inputs.get("contains_legal_topic", False),
                "sector": step_inputs.get("sector"),
                "draft_text": step_inputs.get("draft_text", ""),
                "consecutive_followup_index": step_inputs.get("consecutive_followup_index", 0),
            }
            needs_approval, reason = requires_approval(
                action_type=step.action_type, policy=policy, risk_factors=risks
            )

            ok, budget_reason = within_budget(usage=usage, budget=policy.budget)
            if not ok:
                log.warning("budget_exhausted: %s", budget_reason)
                self._emit_event(
                    customer_id=customer_id,
                    event_type="agent.action_rejected",
                    actor=actor,
                    correlation_id=correlation_id,
                    payload={
                        "agent_id": step.agent_id,
                        "step_id": step.step_id,
                        "reason": f"budget:{budget_reason}",
                    },
                )
                break

            task = self.queue.enqueue(
                customer_id=customer_id,
                agent_id=step.agent_id,
                action_type=step.action_type,
                payload={"step_id": step.step_id, "inputs": step_inputs},
                requires_approval=needs_approval,
                approval_reason=reason,
                correlation_id=correlation_id,
                parent_workflow_id=workflow.workflow_id,
            )
            created_tasks.append(task)
            self._emit_event(
                customer_id=customer_id,
                event_type="agent.action_requested",
                actor=actor,
                correlation_id=correlation_id,
                payload={
                    "agent_id": step.agent_id,
                    "task_id": task.task_id,
                    "step_id": step.step_id,
                    "requires_approval": needs_approval,
                    "approval_reason": reason,
                },
            )

            # Execute immediately if no approval needed
            if not needs_approval:
                result = self._execute_task(task, actor=actor, correlation_id=correlation_id)
                if result is not None:
                    outputs[step.step_id] = result

        return {
            "workflow_id": workflow.workflow_id,
            "correlation_id": correlation_id,
            "customer_id": customer_id,
            "tasks_created": len(created_tasks),
            "awaiting_approval": [
                t.task_id for t in created_tasks if t.status == TaskStatus.AWAITING_APPROVAL
            ],
            "succeeded": [t.task_id for t in created_tasks if t.status == TaskStatus.SUCCEEDED],
            "failed": [t.task_id for t in created_tasks if t.status == TaskStatus.FAILED],
        }

    def approve_and_execute(self, *, task_id: str, approved_by: str) -> AgentTask:
        """Human approves a pending task — orchestrator runs it."""
        task = self.queue.approve(task_id, approved_by=approved_by)
        self._emit_event(
            customer_id=task.customer_id,
            event_type="agent.action_approved",
            actor=approved_by,
            correlation_id=task.correlation_id,
            payload={"agent_id": task.agent_id, "task_id": task_id},
        )
        self._execute_task(task, actor=approved_by, correlation_id=task.correlation_id)
        return task

    def reject_task(self, *, task_id: str, rejected_by: str, reason: str = "") -> AgentTask:
        task = self.queue.reject(task_id, rejected_by=rejected_by, reason=reason)
        self._emit_event(
            customer_id=task.customer_id,
            event_type="agent.action_rejected",
            actor=rejected_by,
            correlation_id=task.correlation_id,
            payload={"agent_id": task.agent_id, "task_id": task_id, "reason": reason},
        )
        return task

    # ── Internal ─────────────────────────────────────────────
    def _execute_task(
        self,
        task: AgentTask,
        *,
        actor: str,
        correlation_id: str | None,
    ) -> dict[str, Any] | None:
        executor = self.executor_registry.get(task.action_type)
        if executor is None:
            self.queue.fail(task.task_id, error=f"no executor for {task.action_type}")
            self._emit_event(
                customer_id=task.customer_id,
                event_type="agent.action_failed",
                actor=actor,
                correlation_id=correlation_id,
                payload={"task_id": task.task_id, "error": "no_executor"},
            )
            return None

        self.queue.mark_executing(task.task_id)
        try:
            result = executor(task)
            self.queue.succeed(task.task_id, result=result)
            self._emit_event(
                customer_id=task.customer_id,
                event_type="agent.action_executed",
                actor=actor,
                correlation_id=correlation_id,
                payload={
                    "agent_id": task.agent_id,
                    "task_id": task.task_id,
                    "action_type": task.action_type,
                },
            )
            usage = self.budget_usage.setdefault(task.customer_id, BudgetUsage())
            if task.action_type == "send_message":
                usage.messages_today += 1
            usage.api_calls_today += 1
            return result
        except Exception as exc:
            self.queue.fail(task.task_id, error=str(exc)[:500])
            self._emit_event(
                customer_id=task.customer_id,
                event_type="agent.action_failed",
                actor=actor,
                correlation_id=correlation_id,
                payload={
                    "task_id": task.task_id,
                    "error": str(exc)[:500],
                    "retries": task.retries,
                },
            )
            return None

    def _emit_event(
        self,
        *,
        customer_id: str,
        event_type: str,
        actor: str,
        correlation_id: str | None,
        payload: dict[str, Any],
    ) -> None:
        e = make_event(
            event_type=event_type,
            customer_id=customer_id,
            subject_type="agent_task",
            subject_id=payload.get("task_id", payload.get("step_id", "unknown")),
            payload=payload,
            actor=actor,
            correlation_id=correlation_id,
        )
        self.event_store.append(e)
