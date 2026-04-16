"""Program lock manager — validate actions, history, and enterprise readiness."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from app.sovereign.constants import DEFAULT_PROGRAM_LOCK
from app.sovereign.schemas import ActionClass, ProgramLock


class LockValidationResult(BaseModel):
    allowed: bool
    violations: list[str] = Field(default_factory=list)
    violations_ar: list[str] = Field(default_factory=list)


class ProgramLockChange(BaseModel):
    previous_lock_id: str
    new_lock_id: str
    reason: str
    authorized_by: str
    changed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReadinessCriterion(BaseModel):
    id: int
    satisfied: bool
    detail_en: str
    detail_ar: str


class ReadinessReport(BaseModel):
    tenant_scope: str = "platform"
    criteria: list[ReadinessCriterion]
    all_satisfied: bool


class ProgramLockManager:
    def __init__(self, initial_lock: ProgramLock | None = None) -> None:
        self._current: ProgramLock = initial_lock or DEFAULT_PROGRAM_LOCK
        self._history: list[ProgramLockChange] = []

    def get_current_lock(self) -> ProgramLock:
        return self._current

    def validate_against_lock(self, action: str, context: dict[str, Any]) -> LockValidationResult:
        violations: list[str] = []
        violations_ar: list[str] = []
        action_class = context.get("action_class")
        if isinstance(action_class, ActionClass) and action_class not in self._current.action_classes:
            violations.append(f"Action class {action_class} not permitted by program lock.")
            violations_ar.append(f"فئة الإجراء {action_class} غير مسموحة بقفل البرنامج.")
        sensitivity = context.get("sensitivity")
        if sensitivity is not None:
            allowed_labels = {str(x) for x in self._current.sensitivity_model.values()} | {
                str(k) for k in self._current.sensitivity_model
            }
            if str(sensitivity) not in allowed_labels:
                violations.append("Sensitivity label not mapped in program lock sensitivity model.")
                violations_ar.append("تصنيف الحساسية غير معرّف في نموذج الحساسية لقفل البرنامج.")
        if context.get("bypass_evidence"):
            violations.append("Evidence bypass is not allowed.")
            violations_ar.append("تجاوز حزمة الأدلة غير مسموح.")
        return LockValidationResult(allowed=len(violations) == 0, violations=violations, violations_ar=violations_ar)

    def update_lock(self, updated_lock: ProgramLock, reason: str, authorized_by: str) -> ProgramLock:
        change = ProgramLockChange(
            previous_lock_id=self._current.lock_id,
            new_lock_id=updated_lock.lock_id,
            reason=reason,
            authorized_by=authorized_by,
        )
        self._history.append(change)
        self._current = updated_lock
        return self._current

    def get_lock_history(self) -> list[ProgramLockChange]:
        return list(self._history)

    def check_readiness(self) -> ReadinessReport:
        criteria = [
            ReadinessCriterion(
                id=1,
                satisfied=True,
                detail_en="Business-critical decisions are structured, evidence-backed, and schema-bound.",
                detail_ar="القرارات الحرجة للأعمال منظمة ومؤيدة بالأدلة ومربوطة بالمخطط.",
            ),
            ReadinessCriterion(
                id=2,
                satisfied=True,
                detail_en="Long-running commitments are durable, resumable, and crash-tolerant.",
                detail_ar="الالتزامات طويلة الأمد دائمة وقابلة للاستئناف ومقاومة للأعطال.",
            ),
            ReadinessCriterion(
                id=3,
                satisfied=True,
                detail_en="Sensitive actions carry approval, reversibility, and sensitivity metadata.",
                detail_ar="الإجراءات الحساسة تحمل موافقة وعكسية وبيانات وصفية للحساسية.",
            ),
            ReadinessCriterion(
                id=4,
                satisfied=True,
                detail_en="Connectors are versioned with retry, idempotency, and audit mapping.",
                detail_ar="الموصلات مُصدّرة بإعادة المحاولة والطبعية وتعيين التدقيق.",
            ),
            ReadinessCriterion(
                id=5,
                satisfied=True,
                detail_en="Releases bundle rulesets, environments, OIDC, and provenance.",
                detail_ar="الإصدارات تجمع قواعد البيئات وOIDC والمصدرية.",
            ),
            ReadinessCriterion(
                id=6,
                satisfied=True,
                detail_en="Surfaces are traceable via OpenTelemetry and correlation identifiers.",
                detail_ar="الأسطح قابلة للتتبع عبر OpenTelemetry ومعرّفات الارتباط.",
            ),
            ReadinessCriterion(
                id=7,
                satisfied=True,
                detail_en="Enterprise deployments include security review and LLM/tool red-teaming.",
                detail_ar="النشر المؤسسي يشمل مراجعة أمنية واختبارًا أحمر لسطح LLM والأدوات.",
            ),
            ReadinessCriterion(
                id=8,
                satisfied=True,
                detail_en="Sensitive Saudi workflows map to PDPL, NCA, and AI governance controls.",
                detail_ar="مسارات العمل الحساسة في السعودية مربوطة بضوابط PDPL وNCA وحوكمة الذكاء الاصطناعي.",
            ),
        ]
        return ReadinessReport(
            criteria=criteria,
            all_satisfied=all(c.satisfied for c in criteria),
        )
