"""Route a task to the right provider, with fallback chain + cost class."""

from __future__ import annotations

from dataclasses import dataclass

from .cost_policy import CostClass, classify_cost
from .fallback_policy import build_fallback_chain
from .provider_registry import ALL_TASK_TYPES, get_provider


@dataclass(frozen=True)
class RouteDecision:
    task_type: str
    primary_provider: str | None
    fallback_chain: list[str]
    cost_class: CostClass
    reasons_ar: list[str]
    requires_arabic: bool
    requires_vision: bool
    sensitivity: str

    def to_dict(self) -> dict[str, object]:
        return {
            "task_type": self.task_type,
            "primary_provider": self.primary_provider,
            "fallback_chain": self.fallback_chain,
            "cost_class": self.cost_class,
            "reasons_ar": self.reasons_ar,
            "requires_arabic": self.requires_arabic,
            "requires_vision": self.requires_vision,
            "sensitivity": self.sensitivity,
        }


def route_task(
    task_type: str,
    *,
    requires_arabic: bool = False,
    requires_vision: bool = False,
    sensitivity: str = "low",
    expected_input_tokens: int = 0,
    expected_output_tokens: int = 0,
    bulk: bool = False,
    primary_provider: str | None = None,
) -> RouteDecision:
    """Route a task → primary provider + ordered fallback chain + cost class."""
    reasons: list[str] = []

    if task_type not in ALL_TASK_TYPES:
        return RouteDecision(
            task_type=task_type,
            primary_provider=None,
            fallback_chain=[],
            cost_class="low",
            reasons_ar=[f"نوع المهمة غير معروف: {task_type}"],
            requires_arabic=requires_arabic,
            requires_vision=requires_vision,
            sensitivity=sensitivity,
        )

    cost_class = classify_cost(
        task_type=task_type,
        expected_input_tokens=expected_input_tokens,
        expected_output_tokens=expected_output_tokens,
        bulk=bulk,
    )

    chain = build_fallback_chain(
        task_type,
        requires_arabic=requires_arabic,
        requires_vision=requires_vision,
        sensitivity=sensitivity,
        primary_key=primary_provider,
    )

    if not chain:
        reasons.append(
            "لا يوجد مزود مناسب — راجع capabilities أو خفّف القيود (vision/arabic)."
        )

    primary = chain[0] if chain else None
    if primary:
        p = get_provider(primary)
        if p:
            reasons.append(
                f"المزود الأساسي: {p.label} — {p.notes_ar}"
            )
    if sensitivity == "high":
        reasons.append("حساسية عالية: تم تفضيل KSA-region/self-hosted أولاً.")
    if bulk:
        reasons.append("مهمة جماعية كبيرة: تم اختيار cost_class=low.")

    return RouteDecision(
        task_type=task_type,
        primary_provider=primary,
        fallback_chain=chain,
        cost_class=cost_class,
        reasons_ar=reasons,
        requires_arabic=requires_arabic,
        requires_vision=requires_vision,
        sensitivity=sensitivity,
    )
