"""Service orchestrator — runs the canonical service pipeline."""

from __future__ import annotations

from typing import Any

# Canonical pipeline every service goes through.
SERVICE_PIPELINE_STEPS: tuple[str, ...] = (
    "intake",
    "data_check",
    "targeting",
    "contactability",
    "strategy",
    "drafting",
    "approval",
    "execution_or_export",
    "tracking",
    "proof",
    "upsell",
)

_STEP_LABELS_AR: dict[str, str] = {
    "intake": "جمع المدخلات",
    "data_check": "فحص جودة البيانات",
    "targeting": "تحديد الأهداف",
    "contactability": "تقييم إمكانية التواصل",
    "strategy": "صياغة الاستراتيجية",
    "drafting": "كتابة المسودات",
    "approval": "اعتماد بشري",
    "execution_or_export": "تنفيذ أو تصدير",
    "tracking": "متابعة النتائج",
    "proof": "Proof Pack",
    "upsell": "ترقية الخدمة",
}


def build_service_pipeline(
    service_id: str, *, customer_id: str = "",
) -> dict[str, Any]:
    """Build the canonical pipeline state for a service."""
    return {
        "service_id": service_id,
        "customer_id": customer_id,
        "current_step": "intake",
        "completed_steps": [],
        "steps": [
            {
                "step_id": s,
                "label_ar": _STEP_LABELS_AR.get(s, s),
                "completed": False,
                "approval_required": s in {
                    "drafting", "approval", "execution_or_export",
                },
            }
            for s in SERVICE_PIPELINE_STEPS
        ],
        "approval_required": True,
        "live_send_allowed": False,
    }


def run_service_step(
    pipeline: dict[str, Any], *, step_id: str | None = None,
) -> dict[str, Any]:
    """
    Mark the current (or supplied) step as run + advance the pipeline.

    Does NOT execute any external action — only updates state.
    """
    target = step_id or pipeline.get("current_step")
    steps = list(pipeline.get("steps", []))
    found = False
    for i, s in enumerate(steps):
        if s.get("step_id") == target:
            s["completed"] = True
            steps[i] = s
            found = True
            # Move to next step.
            if i + 1 < len(steps):
                pipeline["current_step"] = steps[i + 1]["step_id"]
            else:
                pipeline["current_step"] = "done"
            break

    if not found:
        return {**pipeline, "error": f"unknown step: {target}"}

    completed = [s["step_id"] for s in steps if s["completed"]]
    pipeline["steps"] = steps
    pipeline["completed_steps"] = completed
    pipeline["progress_pct"] = round(
        100 * len(completed) / max(1, len(steps)), 1,
    )
    return pipeline
