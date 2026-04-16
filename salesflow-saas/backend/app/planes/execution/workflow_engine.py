"""
Durable Workflow Engine — abstraction over Celery (now) and Temporal (target).

Provides a unified interface for:
- Starting workflows with typed inputs
- Checkpointing / resuming from interrupts
- SLA-aware step execution
- Idempotent external calls
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional
from pydantic import BaseModel, Field


class WorkflowStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class StepStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_HUMAN = "waiting_human"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowDefinition(BaseModel):
    workflow_type: str
    version: str = "1.0.0"
    description: str = ""
    description_ar: str = ""
    max_duration: Optional[timedelta] = None
    retry_policy: dict[str, Any] = Field(default_factory=lambda: {
        "max_retries": 3,
        "backoff_coefficient": 2.0,
        "initial_interval_seconds": 5,
    })


class WorkflowStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    name_ar: str
    order: int
    status: StepStatus = StepStatus.PENDING
    requires_approval: bool = False
    approval_class: Optional[str] = None
    sla_hours: Optional[float] = None
    owner_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class WorkflowInstance(BaseModel):
    instance_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    workflow_type: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: int = 0
    steps: list[WorkflowStep] = Field(default_factory=list)
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    def advance(self) -> Optional[WorkflowStep]:
        """Move to next step if current is completed. Returns next step or None."""
        if self.current_step < len(self.steps):
            current = self.steps[self.current_step]
            if current.status == StepStatus.COMPLETED:
                self.current_step += 1
                self.updated_at = datetime.utcnow()
                if self.current_step < len(self.steps):
                    return self.steps[self.current_step]
                self.status = WorkflowStatus.COMPLETED
                self.completed_at = datetime.utcnow()
        return None

    def is_sla_breached(self) -> bool:
        """Check if current step has breached its SLA."""
        if self.current_step >= len(self.steps):
            return False
        step = self.steps[self.current_step]
        if step.sla_hours and step.started_at:
            deadline = step.started_at + timedelta(hours=step.sla_hours)
            return datetime.utcnow() > deadline
        return False


# ── Workflow Templates ──────────────────────────────────────────

SALES_WORKFLOW = WorkflowDefinition(
    workflow_type="sales_revenue_os",
    description="Full sales cycle: capture → close → expand",
    description_ar="دورة المبيعات الكاملة: التقاط → إغلاق → توسع",
    max_duration=timedelta(days=90),
)

PARTNERSHIP_WORKFLOW = WorkflowDefinition(
    workflow_type="partnership_os",
    description="Partner lifecycle: scout → activate → track",
    description_ar="دورة الشراكة: اكتشاف → تفعيل → متابعة",
    max_duration=timedelta(days=120),
)

MA_WORKFLOW = WorkflowDefinition(
    workflow_type="ma_corporate_dev_os",
    description="M&A lifecycle: source → DD → close → integrate",
    description_ar="دورة الاستحواذ: اكتشاف → فحص → إغلاق → دمج",
    max_duration=timedelta(days=365),
)

EXPANSION_WORKFLOW = WorkflowDefinition(
    workflow_type="expansion_os",
    description="Market expansion: scan → launch → optimize",
    description_ar="التوسع: مسح → إطلاق → تحسين",
    max_duration=timedelta(days=180),
)

PMI_WORKFLOW = WorkflowDefinition(
    workflow_type="pmi_strategic_pmo",
    description="Post-merger integration: Day-1 → 30/60/90 → synergy realization",
    description_ar="تكامل ما بعد الاستحواذ: اليوم الأول → 30/60/90 → تحقيق التآزر",
    max_duration=timedelta(days=365),
)
