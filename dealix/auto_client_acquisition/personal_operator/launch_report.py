"""Launch readiness scoring across product areas — deterministic MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ReadinessStatus(StrEnum):
    READY = "ready"
    ALMOST_READY = "almost_ready"
    NEEDS_WORK = "needs_work"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class LaunchArea:
    key: str
    title_en: str
    title_ar: str
    score: int
    status: ReadinessStatus
    missing_items: list[str]
    next_actions: list[str]
    owner: str
    priority: str  # P0–P3


@dataclass
class LaunchReport:
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    overall_score: int = 0
    areas: list[LaunchArea] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at.isoformat(),
            "overall_score": self.overall_score,
            "areas": [
                {
                    "key": a.key,
                    "title_en": a.title_en,
                    "title_ar": a.title_ar,
                    "score": a.score,
                    "status": a.status.value,
                    "missing_items": a.missing_items,
                    "next_actions": a.next_actions,
                    "owner": a.owner,
                    "priority": a.priority,
                }
                for a in self.areas
            ],
        }


def _status_for_score(score: int) -> ReadinessStatus:
    if score >= 85:
        return ReadinessStatus.READY
    if score >= 70:
        return ReadinessStatus.ALMOST_READY
    if score >= 45:
        return ReadinessStatus.NEEDS_WORK
    return ReadinessStatus.BLOCKED


def build_launch_report() -> LaunchReport:
    """Fifteen launch areas; scores are heuristic until wired to CI/metrics."""
    blueprint: list[tuple[str, str, str, int, list[str], list[str], str, str]] = [
        (
            "backend_api",
            "Backend / API",
            "الواجهات الخلفية وواجهة البرمجة",
            78,
            ["Load tests", "Auth hardening for multi-tenant"],
            ["Add smoke tests for new routers", "Document rate limits"],
            "engineering",
            "P1",
        ),
        (
            "frontend_ui",
            "Frontend / UI",
            "الواجهة والتجربة",
            52,
            ["Next.js app optional", "Command center UI"],
            ["Polish landing + mobile QA", "Wire API examples"],
            "product",
            "P1",
        ),
        (
            "supabase_db",
            "Supabase / Database",
            "قاعدة البيانات وـ pgvector",
            60,
            ["Embeddings pipeline", "RLS policy tests"],
            ["Run migration on staging", "Service role only server-side"],
            "engineering",
            "P0",
        ),
        (
            "project_intelligence",
            "Project Intelligence",
            "ذاكرة المشروع والفهرسة",
            68,
            ["Semantic search live", "Chunk metadata redaction"],
            ["Run scripts/index_project_memory.py", "Add nightly index job"],
            "engineering",
            "P1",
        ),
        (
            "personal_operator",
            "Personal Operator",
            "المشغّل الشخصي الاستراتيجي",
            72,
            ["Persistent memory backend", "WhatsApp send adapter"],
            ["Ship daily brief + opportunities APIs", "Approval UX"],
            "product",
            "P0",
        ),
        (
            "whatsapp_flow",
            "WhatsApp flow",
            "تدفق واتساب والأزرار",
            48,
            ["Cloud API credentials", "Webhook verification"],
            ["Implement two-step buttons", "Opt-in ledger"],
            "engineering",
            "P0",
        ),
        (
            "gmail_calendar",
            "Gmail / Calendar",
            "البريد والتقويم",
            40,
            ["OAuth apps", "Draft-only enforcement in prod"],
            ["Use integrations module drafts", "Approval audit trail"],
            "engineering",
            "P1",
        ),
        (
            "ai_agents_guardrails",
            "AI / Agents / Guardrails",
            "الوكلاء والحوكمة",
            55,
            ["Langfuse eval sets", "OpenAI Agents SDK trace"],
            ["Trace tool calls", "Block outbound without approval"],
            "engineering",
            "P1",
        ),
        (
            "observability",
            "Observability",
            "المراقبة والتتبع",
            58,
            ["Dashboards", "SLOs"],
            ["Ensure Sentry DSN in staging", "OTel sampling"],
            "engineering",
            "P2",
        ),
        (
            "security_pdpl",
            "Security / PDPL",
            "الأمن والامتثال",
            62,
            ["DPA templates", "Retention automation"],
            ["Complete SECURITY_PDPL_CHECKLIST", "Export/delete runbook"],
            "security",
            "P0",
        ),
        (
            "billing_pricing",
            "Billing / Pricing",
            "الفوترة والتسعير",
            50,
            ["Stripe live mode", "Tax"],
            ["Define beta pricing", "Invoice flow"],
            "business",
            "P2",
        ),
        (
            "onboarding",
            "Onboarding",
            "تجربة الإدماج",
            45,
            ["Self-serve checklist", "In-product tours"],
            ["First-run wizard", "Sample data pack"],
            "product",
            "P1",
        ),
        (
            "gtm_sales",
            "GTM / Sales",
            "الوصول للسوق والمبيعات",
            55,
            ["ICP one-pager", "Pilot agreement"],
            ["10-founder list", "Case study template"],
            "gtm",
            "P1",
        ),
        (
            "testing_ci",
            "Testing / CI",
            "الاختبارات والتكامل المستمر",
            50,
            ["Flaky tests", "Coverage gates"],
            ["Stabilize integration suite", "Add personal operator tests"],
            "engineering",
            "P1",
        ),
        (
            "documentation",
            "Documentation",
            "التوثيق",
            70,
            ["API reference polish", "Runbooks"],
            ["Keep launch docs updated", "Arabic exec summaries"],
            "product",
            "P2",
        ),
    ]
    areas: list[LaunchArea] = []
    for key, title_en, title_ar, score, missing, next_a, owner, pri in blueprint:
        areas.append(
            LaunchArea(
                key=key,
                title_en=title_en,
                title_ar=title_ar,
                score=score,
                status=_status_for_score(score),
                missing_items=missing,
                next_actions=next_a,
                owner=owner,
                priority=pri,
            )
        )
    overall = int(round(sum(a.score for a in areas) / len(areas))) if areas else 0
    return LaunchReport(overall_score=overall, areas=areas)


def launch_report_markdown_ar(report: LaunchReport | None = None) -> str:
    report = report or build_launch_report()
    lines = [
        "# تقرير جاهزية إطلاق Dealix",
        "",
        f"- **تاريخ التوليد:** {report.generated_at.isoformat()}",
        f"- **الدرجة الإجمالية:** {report.overall_score} / 100",
        "",
        "## ملخص تنفيذي",
        "",
        "هذا تقرير أولي يعتمد على مخطط المنتج والكود الحالي؛ ربطه بمقاييس CI والإنتاج يحسّن الدقة.",
        "",
        "## تفاصيل المجالات",
        "",
    ]
    for a in report.areas:
        lines.extend(
            [
                f"### {a.title_ar} ({a.title_en})",
                f"- **الدرجة:** {a.score}",
                f"- **الحالة:** {a.status.value}",
                f"- **الأولوية:** {a.priority} — **المسؤول:** {a.owner}",
                "- **النواقص:**",
            ]
        )
        for m in a.missing_items:
            lines.append(f"  - {m}")
        lines.append("- **الخطوات التالية:**")
        for n in a.next_actions:
            lines.append(f"  - {n}")
        lines.append("")
    lines.extend(
        [
            "## معايير البيتا الخاصة",
            "",
            "- واتساب: أزرار موافقة + سجل موافقة",
            "- لا إرسال بارد تلقائي",
            "- اختبارات أساسية خضراء على staging",
            "",
            "## معايير الإطلاق العام",
            "",
            "- PDPL: سياسات واضحة + طلب حذف/تصدير",
            "- مراقبة وفوترة وجاهزية أمنية",
            "",
        ]
    )
    return "\n".join(lines)
