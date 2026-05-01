"""Competitive positioning — deterministic reference data."""

from __future__ import annotations

from typing import Any, Literal

Segment = Literal["founder", "sme", "enterprise", "agency"]


def compare_competitors() -> list[dict[str, Any]]:
    """High-level comparison; not exhaustive feature matrices."""
    return [
        {
            "name": "HubSpot",
            "strengths": ["Wide CRM/marketing suite", "AI + context narrative (2026)"],
            "weaknesses_sa_gcc": ["Not Arabic-native operator", "Generic B2B, not Saudi revenue graph"],
            "dealix_wins": ["Arabic Chief of Staff", "PDPL-first posture", "WhatsApp approval-native flows"],
            "do_not_copy": ["Boil-the-ocean suite creep"],
            "borrow": ["Context-rich AI positioning", "agent + deal progression story"],
        },
        {
            "name": "Salesforce",
            "strengths": ["Enterprise platform depth"],
            "weaknesses_sa_gcc": ["Heavy ops", "Slow founder-led adoption", "Arabic UX gap"],
            "dealix_wins": ["Founder speed", "Saudi signal packs", "Outcome pricing option"],
            "do_not_copy": ["Customization trap without outcomes"],
            "borrow": ["Account-centric revenue thinking"],
        },
        {
            "name": "Gong",
            "strengths": ["Revenue intelligence", "expanding to enablement + AM (Mission Andromeda narrative)"],
            "weaknesses_sa_gcc": ["Call-centric origins", "Arabic market nuance"],
            "dealix_wins": ["WhatsApp-first reality", "why-now radar + Arabic drafts"],
            "do_not_copy": ["Recording-heavy compliance risk without clear PDPL story"],
            "borrow": ["Revenue OS narrative breadth beyond raw calls"],
        },
        {
            "name": "Apollo / ZoomInfo",
            "strengths": ["Prospecting data scale"],
            "weaknesses_sa_gcc": ["Cold outreach culture", "Compliance friction in GCC"],
            "dealix_wins": ["Approval gates", "contactability OS", "Saudi context"],
            "do_not_copy": ["Spray-and-pray automation"],
            "borrow": ["Structured prospect lists as input, not autopilot"],
        },
        {
            "name": "Zoho / Odoo",
            "strengths": ["Price + ERP breadth"],
            "weaknesses_sa_gcc": ["Not a revenue memory + operator system"],
            "dealix_wins": ["Strategic operator + proof pack + market radar"],
            "do_not_copy": ["ERP generalism as core story"],
            "borrow": ["SMB packaging discipline"],
        },
        {
            "name": "WhatsApp automation tools",
            "strengths": ["Channel reach"],
            "weaknesses_sa_gcc": ["Cold spam risk", "weak PDPL story"],
            "dealix_wins": ["Opt-in + approval + audit", "Arabic relationship operator"],
            "do_not_copy": ["Auto-send cold campaigns"],
            "borrow": ["Interactive buttons — max 3 per message; two-step flows"],
        },
        {
            "name": "Boardy-style intro tools",
            "strengths": ["Accept/skip UX for intros"],
            "weaknesses_sa_gcc": ["Limited Saudi B2B + revenue proof loop"],
            "dealix_wins": ["Revenue memory + command center + compliance + Arabic"],
            "do_not_copy": ["Shallow CRM replacement claims"],
            "borrow": ["Relationship card UX patterns"],
        },
        {
            "name": "SocraticCode-style indexing",
            "strengths": ["Repo understanding"],
            "weaknesses_sa_gcc": ["Not revenue + market + Arabic operator"],
            "dealix_wins": ["Project intelligence + strategic memory + GTM"],
            "do_not_copy": ["Dev-only scope"],
            "borrow": ["Chunking + local index before vectors"],
        },
    ]


def dealix_differentiators() -> list[str]:
    return [
        "Saudi-first GTM context",
        "Arabic-first personal operator",
        "WhatsApp-first but compliance-safe",
        "Why-now market signals",
        "Project intelligence + strategic memory",
        "Revenue memory",
        "Agent approval flows",
        "PDPL-aware contactability",
        "Outcome / performance packaging option",
        "Founder daily brief",
        "Vertical playbooks",
        "Relationship-to-revenue workflow",
    ]


def positioning_statement(segment: Segment) -> str:
    statements: dict[Segment, str] = {
        "founder": (
            "Dealix هو نظام إيرادات B2B سعودي مع مشغّل استراتيجي عربي: يومياً يقول لك ماذا يهم، "
            "من تكلّم، ماذا تقول، وما يحتاج موافقة قبل أي إرسال خارجي."
        ),
        "sme": (
            "Dealix يربط إشارات السوق السعودية بقرارات المبيعات والمتابعة عبر واتساب وبريد "
            "بمسارات موافقة وتتبع عائد."
        ),
        "enterprise": (
            "Dealix للمؤسسات: حوكمة، تكاملات، ذاكرة مشروع/إيرادات، ووكلاء آمنون مع سياسات واضحة وSSO عند النشر الخاص."
        ),
        "agency": (
            "لوكالات النمو: تنفذون التطبيق والتدريب، وDealix يبقى منصة الاشتراك مع حزمة أداء اختيارية مُعرّفة تعاقدياً."
        ),
    }
    return statements.get(segment, statements["founder"])
