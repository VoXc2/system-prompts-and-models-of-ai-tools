"""Sovereign PMI — Post-merger integration programs and tasks."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class PMIService:
    """Manages post-merger integration programs and their tasks."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Programs ───────────────────────────────────

    async def create_program(
        self, tenant_id: str, data: dict,
    ) -> "PMIProgram":
        from app.models.sovereign_pmi import PMIProgram

        program = PMIProgram(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            title=data["title"],
            title_ar=data.get("title_ar"),
            ma_target_id=uuid.UUID(data["ma_target_id"]) if data.get("ma_target_id") else None,
            status=data.get("status", "planning"),
            day1_readiness=data.get("day1_readiness"),
            integration_plan_30=data.get("integration_plan_30"),
            integration_plan_60=data.get("integration_plan_60"),
            integration_plan_90=data.get("integration_plan_90"),
            synergy_realization=data.get("synergy_realization"),
            risk_register=data.get("risk_register"),
            escalation_rules=data.get("escalation_rules"),
            owner_id=uuid.UUID(data["owner_id"]) if data.get("owner_id") else None,
            next_review_at=data.get("next_review_at"),
            notes=data.get("notes"),
        )
        self.db.add(program)
        await self.db.flush()
        return program

    async def list_programs(
        self,
        tenant_id: str,
        status: Optional[str] = None,
    ) -> list:
        from app.models.sovereign_pmi import PMIProgram

        query = select(PMIProgram).where(
            PMIProgram.tenant_id == uuid.UUID(tenant_id),
        )
        if status:
            query = query.where(PMIProgram.status == status)

        query = query.order_by(PMIProgram.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_program(
        self, tenant_id: str, program_id: str,
    ) -> Optional["PMIProgram"]:
        from app.models.sovereign_pmi import PMIProgram

        result = await self.db.execute(
            select(PMIProgram)
            .options(selectinload(PMIProgram.tasks))
            .where(
                PMIProgram.id == uuid.UUID(program_id),
                PMIProgram.tenant_id == uuid.UUID(tenant_id),
            )
        )
        return result.scalar_one_or_none()

    # ── Tasks ──────────────────────────────────────

    async def create_task(
        self, tenant_id: str, data: dict,
    ) -> "PMITask":
        from app.models.sovereign_pmi import PMITask

        task = PMITask(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            program_id=uuid.UUID(data["program_id"]),
            title=data["title"],
            title_ar=data.get("title_ar"),
            status=data.get("status", "pending"),
            priority=data.get("priority", "medium"),
            phase=data["phase"],
            assigned_to_id=uuid.UUID(data["assigned_to_id"]) if data.get("assigned_to_id") else None,
            depends_on=data.get("depends_on"),
            due_date=data.get("due_date"),
            notes=data.get("notes"),
        )
        self.db.add(task)
        await self.db.flush()
        return task

    async def update_task_status(
        self,
        tenant_id: str,
        task_id: str,
        status: str,
    ) -> Optional["PMITask"]:
        from app.models.sovereign_pmi import PMITask

        result = await self.db.execute(
            select(PMITask).where(
                PMITask.id == uuid.UUID(task_id),
                PMITask.tenant_id == uuid.UUID(tenant_id),
            )
        )
        task = result.scalar_one_or_none()
        if not task:
            return None

        task.status = status
        task.updated_at = datetime.now(timezone.utc)
        if status == "completed":
            task.completed_at = datetime.now(timezone.utc)

        await self.db.flush()
        return task

    # ── 30/60/90 Engine ────────────────────────────

    async def get_pmi_engine(self, tenant_id: str) -> dict:
        from app.models.sovereign_pmi import PMIProgram, PMITask

        tid = uuid.UUID(tenant_id)

        total_programs = (await self.db.execute(
            select(func.count()).where(PMIProgram.tenant_id == tid)
        )).scalar() or 0

        by_status_result = await self.db.execute(
            select(
                PMIProgram.status,
                func.count().label("count"),
            ).where(PMIProgram.tenant_id == tid).group_by(PMIProgram.status)
        )
        programs_by_status = {row.status: row.count for row in by_status_result.all()}

        phases = ["day1", "30", "60", "90"]
        task_matrix: dict = {}
        for phase in phases:
            total = (await self.db.execute(
                select(func.count()).where(
                    PMITask.tenant_id == tid,
                    PMITask.phase == phase,
                )
            )).scalar() or 0

            completed = (await self.db.execute(
                select(func.count()).where(
                    PMITask.tenant_id == tid,
                    PMITask.phase == phase,
                    PMITask.status == "completed",
                )
            )).scalar() or 0

            overdue = (await self.db.execute(
                select(func.count()).where(
                    PMITask.tenant_id == tid,
                    PMITask.phase == phase,
                    PMITask.status != "completed",
                    PMITask.due_date < datetime.now(timezone.utc),
                )
            )).scalar() or 0

            task_matrix[phase] = {
                "total": total,
                "completed": completed,
                "overdue": overdue,
                "completion_pct": round(completed / total * 100, 1) if total > 0 else 0.0,
            }

        total_tasks = (await self.db.execute(
            select(func.count()).where(PMITask.tenant_id == tid)
        )).scalar() or 0

        completed_tasks = (await self.db.execute(
            select(func.count()).where(
                PMITask.tenant_id == tid,
                PMITask.status == "completed",
            )
        )).scalar() or 0

        return {
            "total_programs": total_programs,
            "programs_by_status": programs_by_status,
            "task_matrix": task_matrix,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "overall_completion_pct": round(completed_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0.0,
        }
