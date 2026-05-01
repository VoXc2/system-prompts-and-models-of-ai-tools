"""Registry of model providers + task types."""

from __future__ import annotations

from dataclasses import dataclass, field

# Task types Dealix actually routes.
ALL_TASK_TYPES: tuple[str, ...] = (
    "strategic_reasoning",
    "arabic_copywriting",
    "classification",
    "compliance_guardrail",
    "meeting_analysis",
    "vision_analysis",
    "extraction",
    "summarization",
    "coding_project_understanding",
    "low_cost_bulk",
)


@dataclass(frozen=True)
class Provider:
    """A model provider entry."""
    key: str
    label: str
    family: str             # "anthropic" | "openai" | "google" | "azure" | "local"
    capabilities: tuple[str, ...]   # subset of ALL_TASK_TYPES
    cost_class: str         # "low" | "mid" | "high"
    latency_class: str      # "fast" | "balanced" | "slow"
    supports_vision: bool
    supports_arabic: bool
    privacy_tier: str       # "vendor_cloud" | "ksa_region" | "self_hosted"
    notes_ar: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key, "label": self.label, "family": self.family,
            "capabilities": list(self.capabilities),
            "cost_class": self.cost_class, "latency_class": self.latency_class,
            "supports_vision": self.supports_vision,
            "supports_arabic": self.supports_arabic,
            "privacy_tier": self.privacy_tier,
            "notes_ar": self.notes_ar,
        }


# Conservative provider list — Dealix can swap any of these without code change.
ALL_PROVIDERS: tuple[Provider, ...] = (
    Provider(
        key="claude_sonnet",
        label="Claude Sonnet",
        family="anthropic",
        capabilities=(
            "strategic_reasoning", "arabic_copywriting",
            "compliance_guardrail", "meeting_analysis", "summarization",
            "coding_project_understanding",
        ),
        cost_class="mid",
        latency_class="balanced",
        supports_vision=True,
        supports_arabic=True,
        privacy_tier="vendor_cloud",
        notes_ar="مناسب للاستراتيجية والكتابة العربية والامتثال.",
    ),
    Provider(
        key="claude_haiku",
        label="Claude Haiku",
        family="anthropic",
        capabilities=("classification", "extraction", "low_cost_bulk", "summarization"),
        cost_class="low",
        latency_class="fast",
        supports_vision=False,
        supports_arabic=True,
        privacy_tier="vendor_cloud",
        notes_ar="رخيص وسريع — للتصنيف الكثيف والاستخراج.",
    ),
    Provider(
        key="gpt_4_class",
        label="GPT-4-class",
        family="openai",
        capabilities=(
            "strategic_reasoning", "vision_analysis",
            "coding_project_understanding", "meeting_analysis",
        ),
        cost_class="high",
        latency_class="balanced",
        supports_vision=True,
        supports_arabic=True,
        privacy_tier="vendor_cloud",
        notes_ar="بديل قوي للاستراتيجية والرؤية.",
    ),
    Provider(
        key="gpt_4o_mini",
        label="GPT-4o mini",
        family="openai",
        capabilities=("classification", "extraction", "low_cost_bulk"),
        cost_class="low",
        latency_class="fast",
        supports_vision=True,
        supports_arabic=True,
        privacy_tier="vendor_cloud",
        notes_ar="بديل رخيص للمهام الكثيفة.",
    ),
    Provider(
        key="gemini_pro",
        label="Gemini Pro",
        family="google",
        capabilities=(
            "vision_analysis", "summarization", "meeting_analysis",
            "extraction",
        ),
        cost_class="mid",
        latency_class="balanced",
        supports_vision=True,
        supports_arabic=True,
        privacy_tier="vendor_cloud",
        notes_ar="ممتاز للرؤية والاجتماعات.",
    ),
    Provider(
        key="azure_oai_ksa",
        label="Azure OpenAI (KSA region)",
        family="azure",
        capabilities=(
            "strategic_reasoning", "arabic_copywriting",
            "compliance_guardrail", "extraction", "summarization",
        ),
        cost_class="mid",
        latency_class="balanced",
        supports_vision=True,
        supports_arabic=True,
        privacy_tier="ksa_region",
        notes_ar="منطقة KSA — مناسب للعملاء الحساسين للامتثال.",
    ),
    Provider(
        key="local_qwen_ar",
        label="Local Qwen (Arabic-tuned)",
        family="local",
        capabilities=("classification", "extraction", "low_cost_bulk", "arabic_copywriting"),
        cost_class="low",
        latency_class="balanced",
        supports_vision=False,
        supports_arabic=True,
        privacy_tier="self_hosted",
        notes_ar="نموذج محلي — للحالات الحساسة جداً.",
    ),
)


def get_provider(key: str) -> Provider | None:
    return next((p for p in ALL_PROVIDERS if p.key == key), None)


@dataclass(frozen=True)
class TaskType:
    """Description of a routed task."""
    key: str
    label_ar: str
    requires_arabic: bool
    requires_vision: bool
    sensitivity: str        # "low" | "medium" | "high"
    notes_ar: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key, "label_ar": self.label_ar,
            "requires_arabic": self.requires_arabic,
            "requires_vision": self.requires_vision,
            "sensitivity": self.sensitivity,
            "notes_ar": self.notes_ar,
        }
