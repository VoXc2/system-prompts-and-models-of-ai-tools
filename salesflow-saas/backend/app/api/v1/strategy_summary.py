"""JSON summary for /strategy page and integrations."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["Strategy"])

_BLUEPRINT_VERSION = "5.0.0-sovereign"

_MOAT_PILLARS = [
    "Decision-native recommendations that are typed, evidence-backed, policy-aware, and freshness-aware",
    "Durable business commitments with resumable execution instead of fragile agent-only side effects",
    "Trust plane controls: approvals, authorization, secrets governance, tool verification, and auditability",
    "Arabic-first and Saudi-ready operating surfaces for boards, partnerships, expansion, and compliance",
    "Connector facade discipline with versioning, retries, idempotency, telemetry, and rollback notes",
]

_AUDITABLE_TARGETS = [
    {"id": "revenue", "label_ar": "النمو الإيرادي", "target": "3–5× سنوياً مقابل خط أساس", "unit": "growth_vs_baseline"},
    {"id": "efficiency", "label_ar": "كفاءة المبيعات", "target": "−70–80% عمل يدوي في المسار", "unit": "manual_work_reduction"},
    {"id": "forecast", "label_ar": "دقة التنبؤ", "target": "أفق 30 يوماً — بيانات نظيفة ونماذج معايرة", "unit": "accuracy_horizon_30d"},
    {"id": "cycle", "label_ar": "دورة الإغلاق", "target": "حوالي −40% زمن مقارنة بالخط الأساسي", "unit": "cycle_time_delta"},
    {"id": "board", "label_ar": "جاهزية المجلس", "target": "كل قرار business-critical مع evidence pack وmetadata كامل", "unit": "board_readiness"},
    {"id": "compliance", "label_ar": "الامتثال", "target": "PDPL + NCA + AI governance mapping للمسارات الحساسة", "unit": "policy"},
]

_PLANES = [
    {
        "id": "decision",
        "name_ar": "Decision Plane",
        "name_en": "Decision Plane",
        "mission": "استكشاف الإشارات، الفرز، تحليل السيناريوهات، توليد المذكرات، التنبؤ، التوصية، وتجميع evidence packs.",
        "capabilities": [
            "signal detection",
            "triage",
            "scenario analysis",
            "memo generation",
            "forecasting",
            "next best action",
        ],
        "building_blocks": ["Responses API", "Structured Outputs", "function calling / MCP", "LangGraph interrupts"],
        "outcome": "كل recommendation يجب أن يكون typed + evidence-backed + approval-aware.",
    },
    {
        "id": "execution",
        "name_ar": "Execution Plane",
        "name_en": "Execution Plane",
        "mission": "تنفيذ الالتزامات التشغيلية الطويلة عبر أنظمة متعددة مع retry وtimeout وcompensation وresume.",
        "capabilities": [
            "durable workflows",
            "approval / resume later",
            "timeout handling",
            "compensation",
            "idempotent side effects",
            "cross-system orchestration",
        ],
        "building_blocks": ["Temporal", "LangGraph", "Celery", "connector facade", "idempotency keys"],
        "outcome": "كل business commitment يجب أن يكون durable + resumable + idempotent + observable.",
    },
    {
        "id": "trust",
        "name_ar": "Trust Plane",
        "name_en": "Trust Plane",
        "mission": "فرض السياسات والتفويض والموافقات وحوكمة الأسرار وسجل التحقق والتدقيق.",
        "capabilities": [
            "policy engine",
            "approval routing",
            "fine-grained authorization",
            "secrets governance",
            "tool verification ledger",
            "contradiction detection",
        ],
        "building_blocks": ["OPA", "OpenFGA", "Vault", "Keycloak", "tool_verification.py"],
        "outcome": "كل فعل حساس يجب أن يكون authorized + policy-evaluated + audited + verified against actual execution.",
    },
    {
        "id": "data",
        "name_ar": "Data Plane",
        "name_en": "Data Plane",
        "mission": "إدارة مصدر الحقيقة التشغيلي والذاكرة الدلالية والجودة والعقود والتتبّع على مستوى المنصة.",
        "capabilities": [
            "operational source of truth",
            "semantic memory",
            "document extraction",
            "data quality",
            "event contracts",
            "telemetry",
        ],
        "building_blocks": [
            "PostgreSQL",
            "pgvector",
            "Airbyte",
            "Unstructured",
            "Great Expectations",
            "CloudEvents + AsyncAPI",
            "OpenTelemetry",
        ],
        "outcome": "كل surface يجب أن يكون traceable مع correlation IDs وعقود بيانات واضحة.",
    },
    {
        "id": "operating",
        "name_ar": "Operating Plane",
        "name_en": "Operating Plane",
        "mission": "تحويل SDLC والإصدارات والإثباتات والضوابط إلى جزء من تشغيل المنتج نفسه.",
        "capabilities": [
            "rulesets",
            "protected branches",
            "deployment protection",
            "OIDC federation",
            "artifact attestations",
            "external audit streaming",
        ],
        "building_blocks": ["GitHub rulesets", "CODEOWNERS", "environments", "OIDC", "artifact attestations"],
        "outcome": "كل release مؤسسي يجب أن يحمل provenance واضحًا وبوابات نشر قابلة للتدقيق.",
    },
]

_BUSINESS_TRACKS = [
    {
        "id": "revenue",
        "name_ar": "Revenue OS",
        "scope": [
            "capture من جميع القنوات",
            "enrichment / qualification / scoring / routing",
            "outreach وmeeting orchestration",
            "proposal generation",
            "pricing / discount governance",
            "handoff إلى العقد ثم onboarding ثم renewal",
        ],
        "automation_mode": "أتمتة كاملة للـ intake/enrichment/scoring، واعتماد إلزامي للتخفيضات الخارجة عن السياسة أو الالتزامات التجارية الحساسة.",
        "primary_surfaces": ["Revenue Funnel Control Center", "Actual vs Forecast Dashboard", "Approval Center"],
    },
    {
        "id": "partnerships",
        "name_ar": "Partnership OS",
        "scope": [
            "partner scouting",
            "strategic fit scoring",
            "channel economics",
            "alliance structure recommendation",
            "term sheet draft",
            "partner activation and scorecards",
        ],
        "automation_mode": "الأتمتة للمسح والتحليل والـ drafts، مع اعتماد إلزامي لتفعيل الشريك أو إرسال term sheet.",
        "primary_surfaces": ["Partner Room", "Partnership Scorecards", "Approval Center"],
    },
    {
        "id": "corpdev",
        "name_ar": "M&A / CorpDev OS",
        "scope": [
            "target sourcing and screening",
            "DD orchestration",
            "DD room access control",
            "valuation range and synergy modeling",
            "investment committee memos",
            "offer strategy and close readiness",
        ],
        "automation_mode": "التحليل والتجميع والمذكرات مؤتمتة؛ العروض والالتزامات الرأسمالية وراء board / IC approval.",
        "primary_surfaces": ["DD Room", "M&A Pipeline Board", "Evidence Pack Viewer"],
    },
    {
        "id": "expansion",
        "name_ar": "Expansion OS",
        "scope": [
            "market scanning and prioritization",
            "compliance readiness",
            "localization",
            "pricing/channel plan",
            "launch readiness",
            "post-launch actual vs forecast",
        ],
        "automation_mode": "الأتمتة للـ scanning والـ variance detection؛ والإطلاقات وراء launch approvals وstop-loss logic.",
        "primary_surfaces": ["Expansion Launch Console", "Saudi Compliance Matrix", "Actual vs Forecast Dashboard"],
    },
    {
        "id": "pmi_pmo",
        "name_ar": "PMI / PMO OS",
        "scope": [
            "Day-1 readiness",
            "30/60/90 integration plans",
            "dependency tracking",
            "owner assignment",
            "escalation engine",
            "synergy realization tracking",
        ],
        "automation_mode": "المهام والتذكيرات والـ SLA tracking مؤتمتة؛ أما التغييرات التنظيمية الحرجة فتحتاج موافقات مالكين وتنفيذيين.",
        "primary_surfaces": ["PMI 30/60/90 Engine", "Risk Board", "Weekly Executive Review"],
    },
    {
        "id": "executive_board",
        "name_ar": "Executive / Board OS",
        "scope": [
            "board-ready memos",
            "evidence packs",
            "approval center",
            "risk heatmaps",
            "actual vs forecast",
            "policy violations and next best action",
        ],
        "automation_mode": "التجميع والتحضير مؤتمت؛ الاعتمادات النهائية والقرارات الحرجة بشرية وإلزامية.",
        "primary_surfaces": ["Executive Room", "Evidence Pack Viewer", "Approval Center"],
    },
]

_OPERATING_SURFACES = [
    {"id": "executive_room", "name_ar": "Executive Room", "owner_track": "executive_board", "status": "build_next", "summary": "غرفة تنفيذية موحدة للمجلس والإدارة مع المذكرات، المخاطر، وnext best action."},
    {"id": "approval_center", "name_ar": "Approval Center", "owner_track": "executive_board", "status": "repo_anchor", "summary": "مركز اعتماد موحد للمسارات الحساسة وربط القرار بالفعل الفعلي."},
    {"id": "evidence_pack_viewer", "name_ar": "Evidence Pack Viewer", "owner_track": "executive_board", "status": "build_next", "summary": "عرض حي للمصادر والافتراضات والحداثة وpolicy notes وبدائل القرار."},
    {"id": "partner_room", "name_ar": "Partner Room", "owner_track": "partnerships", "status": "build_next", "summary": "غرفة شريك تجمع fit scoring، economics، term sheets، والتفعيل."},
    {"id": "dd_room", "name_ar": "DD Room", "owner_track": "corpdev", "status": "repo_anchor", "summary": "غرفة عناية واجبة مع تحكم وصول، مستندات، ومراحل DD/readiness."},
    {"id": "risk_board", "name_ar": "Risk Board", "owner_track": "pmi_pmo", "status": "build_next", "summary": "لوحة مخاطر موحدة تعرض الحرارة، المالك، الحالة، والتصعيد التنفيذي."},
    {"id": "policy_violations_board", "name_ar": "Policy Violations Board", "owner_track": "executive_board", "status": "build_next", "summary": "لوحة انتهاكات السياسات وربطها بالموافقات والأدلة والإجراءات."},
    {"id": "actual_vs_forecast_dashboard", "name_ar": "Actual vs Forecast Dashboard", "owner_track": "revenue", "status": "build_next", "summary": "لوحة variance موحدة للإيراد، التوسع، والتكامل بعد الإطلاق."},
    {"id": "revenue_funnel_control_center", "name_ar": "Revenue Funnel Control Center", "owner_track": "revenue", "status": "repo_anchor", "summary": "مركز تحكم للفunnel من capture إلى renewal مع scoring وrouting وgovernance."},
    {"id": "partnership_scorecards", "name_ar": "Partnership Scorecards", "owner_track": "partnerships", "status": "target_required", "summary": "بطاقات أداء الشركاء وهوامش المساهمة وتفعيل الشركاء."},
    {"id": "ma_pipeline_board", "name_ar": "M&A Pipeline Board", "owner_track": "corpdev", "status": "build_next", "summary": "لوحة pipeline للصفقات الاستراتيجية من screening إلى close readiness."},
    {"id": "expansion_launch_console", "name_ar": "Expansion Launch Console", "owner_track": "expansion", "status": "target_required", "summary": "كونسول جاهزية الإطلاق والتوطين والامتثال وstop-loss."},
    {"id": "pmi_engine", "name_ar": "PMI 30/60/90 Engine", "owner_track": "pmi_pmo", "status": "target_required", "summary": "محرك متابعة الدمج Day-1 ثم 30/60/90 مع dependencies وsynergy tracking."},
    {"id": "tool_verification_ledger", "name_ar": "Tool Verification Ledger", "owner_track": "trust", "status": "repo_anchor", "summary": "سجل يطابق intended action وclaimed action وactual tool call والآثار الجانبية."},
    {"id": "connector_health_board", "name_ar": "Connector Health Board", "owner_track": "operating", "status": "build_next", "summary": "لوحة صحة الموصلات مع versioning وretry/timeout وتاريخ التغييرات."},
    {"id": "release_gate_dashboard", "name_ar": "Release Gate Dashboard", "owner_track": "operating", "status": "repo_anchor", "summary": "لوحة rulesets وenvironments وOIDC وprovenance وبوابات الإطلاق."},
    {"id": "saudi_compliance_matrix", "name_ar": "Saudi Compliance Matrix", "owner_track": "expansion", "status": "build_next", "summary": "مصفوفة مواءمة واضحة لـ PDPL/NCA/AI governance على المسارات الحساسة."},
    {"id": "model_routing_dashboard", "name_ar": "Model Routing Dashboard", "owner_track": "decision", "status": "build_next", "summary": "لوحة lanes والسياسات والتكلفة والجودة العربية وcontradiction rate."},
]

_PROGRAM_LOCKS = {
    "counts": {"planes": 5, "business_tracks": 6, "agent_roles": 3},
    "action_classes": [
        {"id": "advisory", "label_ar": "استشاري", "description": "تحليل وتوصية دون side effects."},
        {"id": "assistive", "label_ar": "مساعد", "description": "تحضير drafts وتجميع أدلة وإطلاق workflows دون التزام خارجي مباشر."},
        {"id": "committing", "label_ar": "ملتزم", "description": "أفعال تنشئ التزاماً خارجياً أو مادياً ويجب أن تمر بالاعتماد المناسب."},
    ],
    "approval_classes": [
        {"id": "standard", "label_ar": "تشغيلي", "description": "اعتماد مدير أو مالك مسار لتغييرات قابلة للعكس."},
        {"id": "sensitive", "label_ar": "حساس", "description": "اعتماد إلزامي للبيانات الحساسة، التشارك، التخفيضات الخارجة عن السياسة، والإطلاقات."},
        {"id": "board", "label_ar": "مجلس / لجنة", "description": "اعتماد للمخاطر الرأسمالية أو M&A أو الالتزامات غير القابلة للعكس."},
    ],
    "reversibility_classes": [
        {"id": "reversible", "label_ar": "قابل للعكس", "description": "يمكن التراجع عنه دون ضرر خارجي كبير."},
        {"id": "time_bound", "label_ar": "قابل للعكس ضمن نافذة", "description": "يحتاج rollback سريعاً ضمن نافذة زمنية محددة."},
        {"id": "hard_to_reverse", "label_ar": "صعب العكس", "description": "التراجع ممكن لكن بتكلفة تشغيلية أو سمعة."},
        {"id": "irreversible", "label_ar": "غير قابل للعكس", "description": "لا ينفذ إلا مع approval واضح وevidence كامل."},
    ],
    "sensitivity_levels": ["public", "internal", "confidential", "restricted"],
    "metadata_trio": ["provenance", "freshness", "confidence"],
}

_AUTOMATION_POLICY = {
    "fully_automated": [
        "intake",
        "enrichment",
        "scoring",
        "memo drafting",
        "evidence aggregation",
        "workflow kickoff",
        "reminders and SLA tracking",
        "variance detection and anomaly alerts",
        "document extraction",
        "connector syncs and quality checks",
        "telemetry collection",
    ],
    "approval_required": [
        "term sheet sending",
        "signature request",
        "strategic partner activation",
        "market launch",
        "M&A offer",
        "discount outside policy",
        "high-sensitivity data sharing",
        "production promotion",
        "capital commitments",
    ],
}

_ROUTING_FABRIC = {
    "lanes": [
        {
            "id": "coding",
            "name_ar": "Coding Lane",
            "purpose": "مهام الكود والتحليل الهيكلي وإخراج artifacts الهندسية.",
            "models": ["DeepSeek", "Claude", "internal tools"],
            "optimize_for": ["correctness", "repo grounding", "tool use"],
        },
        {
            "id": "executive_reasoning",
            "name_ar": "Executive Reasoning Lane",
            "purpose": "المذكرات التنفيذية، السيناريوهات، التوصيات، والقرارات عالية الأثر.",
            "models": ["Claude", "Gemini", "OpenAI"],
            "optimize_for": ["reasoning depth", "Arabic quality", "contradiction control"],
        },
        {
            "id": "throughput_drafting",
            "name_ar": "Throughput Drafting Lane",
            "purpose": "التلخيص السريع، التصنيف، الإثراء، والصياغات ذات الحجم العالي.",
            "models": ["Groq", "OpenAI mini"],
            "optimize_for": ["latency", "cost per successful task", "schema adherence"],
        },
        {
            "id": "fallback",
            "name_ar": "Fallback Lane",
            "purpose": "الاستمرارية الآمنة عند تعطل lane أساسي أو انخفاض الثقة.",
            "models": ["OpenAI mini", "local cached response"],
            "optimize_for": ["availability", "safe degradation", "bounded cost"],
        },
    ],
    "scorecard": ["latency", "schema adherence", "contradiction rate", "Arabic quality", "cost per successful task"],
}

_DESIGN_PRINCIPLES = [
    {"id": "decision_native", "title_ar": "Decision-native", "summary": "كل قرار مهم يخرج typed + evidence-backed + policy-aware."},
    {"id": "durable_execution", "title_ar": "Durable execution", "summary": "الالتزامات الطويلة تخرج من منطق الوكيل إلى workflow runtime حتمي."},
    {"id": "trust_enforced", "title_ar": "Trust-enforced", "summary": "الموافقات والسياسات والتفويض وسجل التحقق جزء من المنتج نفسه."},
    {"id": "data_governed", "title_ar": "Data-governed", "summary": "المصدر التشغيلي والذاكرة الدلالية والعقود والجودة مراقبة مع OTel."},
    {"id": "arabic_first", "title_ar": "Arabic-first", "summary": "التصنيف والمذكرات والاعتمادات والبحث والواجهة التنفيذية عربية أولاً."},
    {"id": "board_usable", "title_ar": "Board-usable", "summary": "المنصة تُنتج board-ready memos وevidence packs وليست CRM ذكي فقط."},
]

_PHASES = [
    {"id": 0, "name": "Sovereign foundation", "horizon_days": 90},
    {"id": 1, "name": "Decision + trust closure", "horizon_months": "3-9"},
    {"id": 2, "name": "Enterprise workflow durability", "horizon_months": "9-18"},
    {"id": 3, "name": "Board-scale expansion", "horizon_months": "18-36"},
]

_EXECUTION_PHASES_DETAIL = [
    {
        "id": 0,
        "name_ar": "قفل الأساس السيادي",
        "window": "0–90 يوماً",
        "deliverables": ["5 planes + 6 tracks داخل المنتج", "Approval Center + Release Gate", "strategy surfaces حيّة", "وثائق سيادية مرتبطة بالمستودع"],
    },
    {
        "id": 1,
        "name_ar": "إغلاق القرار والثقة",
        "window": "3–9 أشهر",
        "deliverables": ["Evidence Pack Viewer", "Policy Violations Board", "Model Routing Dashboard", "Saudi Compliance Matrix"],
    },
    {
        "id": 2,
        "name_ar": "تنفيذ مؤسسي durable",
        "window": "9–18 شهراً",
        "deliverables": ["Temporal-backed commitments", "Connector Health Board", "PMI 30/60/90 Engine", "Expansion Launch Console"],
    },
    {
        "id": 3,
        "name_ar": "هيمنة سوقية قابلة للبيع",
        "window": "18–36 شهراً",
        "deliverables": ["Executive Room كامل", "Partnership / M&A scale-up", "Board-grade evidence ops", "توسع سوقي عربي/خليجي"],
    },
]

_KPIS = [
    {"axis": "decision", "metric": "schema adherence + contradiction rate + evidence completeness"},
    {"axis": "execution", "metric": "workflow durability + resume success + idempotency incidents"},
    {"axis": "trust", "metric": "approval latency + policy violations + verified actions"},
    {"axis": "market", "metric": "Arabic quality + board adoption + enterprise win rate"},
]

_READINESS_DEFINITION = [
    "كل قرار business-critical structured + evidence-backed + schema-bound.",
    "كل long-running commitment durable + resumable + crash-tolerant.",
    "كل action حساس يحمل approval/reversibility/sensitivity metadata.",
    "كل connector versioned وله retry/idempotency/audit mapping.",
    "كل release له rulesets + environments + OIDC + provenance.",
    "كل surface traceable عبر OTel + correlation IDs.",
    "كل deployment مؤسسي له security review وred-team لسطوح LLM/tool execution.",
    "كل workflow حساس في السعودية له mapping واضح على PDPL/NCA/AI governance.",
]

_DOC_PATHS = {
    "full_markdown_web": "/strategy/DEALIX_NEXT_LEVEL_MASTER_PLAN_AR.md",
    "sovereign_operating_model_ar": "/strategy/SOVEREIGN_ENTERPRISE_GROWTH_OS_AR.md",
    "ultimate_execution_ar": "/strategy/ULTIMATE_EXECUTION_MASTER_AR.md",
    "integration_master_ar": "/strategy/INTEGRATION_MASTER_AR.md",
    "investor_html": "/dealix-marketing/investor/00-investor-dealix-full-ar.html",
}

_REPO_PATHS = {
    "blueprint": "salesflow-saas/MASTER-BLUEPRINT.mdc",
    "openclaw_config": "salesflow-saas/openclaw/openclaw-config.yaml",
    "sovereign_doc": "salesflow-saas/docs/SOVEREIGN_ENTERPRISE_GROWTH_OS_AR.md",
    "ultimate_doc": "salesflow-saas/docs/ULTIMATE_EXECUTION_MASTER_AR.md",
    "integration_master": "salesflow-saas/docs/INTEGRATION_MASTER_AR.md",
}


@router.get("/strategy/summary")
async def strategy_summary() -> dict:
    return {
        "product": "Dealix",
        "blueprint_version": _BLUEPRINT_VERSION,
        "positioning": "Sovereign Enterprise Growth OS - Saudi-ready, decision-native, durable, trust-enforced",
        "vision": {
            "tagline_ar": "ديلكس ليس CRM ذكيًا فقط؛ بل منصة سيادية تدير القرار والتنفيذ والثقة والنمو المؤسسي على قاعدة واحدة.",
            "tagline_en": "Dealix is not just an AI CRM; it is a sovereign enterprise growth operating system.",
        },
        "sovereign_model": {
            "name": "Dealix Sovereign Enterprise Growth OS",
            "operating_rule_ar": "AI يستكشف ويحلل ويقترح، الأنظمة تنفذ، والبشر يعتمدون القرارات الحرجة.",
            "operating_rule_en": "AI explores, analyzes, and recommends; systems execute; humans approve critical decisions.",
            "thesis_ar": "السيادة الحقيقية تأتي من decision-native design + durable execution + trust enforcement + Saudi readiness.",
        },
        "moat_pillars": _MOAT_PILLARS,
        "competitive_moat": {
            "decision_sovereignty": "Recommendations carry provenance, freshness, confidence, policy notes, and alternatives.",
            "durable_runtime": "Long-running commitments move from agent-only logic to deterministic workflow runtimes.",
            "trust_enforcement": "Approvals, authorization, secrets, and verification sit in-product, not in tribal process.",
            "saudi_first": "Arabic-first UX, PDPL-aware handling, and Saudi compliance mapping are core, not localization afterthoughts.",
        },
        "auditable_targets": _AUDITABLE_TARGETS,
        "planes": _PLANES,
        "business_tracks": _BUSINESS_TRACKS,
        "operating_surfaces": _OPERATING_SURFACES,
        "program_locks": _PROGRAM_LOCKS,
        "automation_policy": _AUTOMATION_POLICY,
        "routing_fabric": _ROUTING_FABRIC,
        "design_principles": _DESIGN_PRINCIPLES,
        "market_frame": "Move from AI CRM positioning to sovereign enterprise growth execution with board-grade evidence and durable commitments.",
        "phases": _PHASES,
        "execution_phases_detail": _EXECUTION_PHASES_DETAIL,
        "kpis": _KPIS,
        "readiness_definition": _READINESS_DEFINITION,
        "doc_paths": _DOC_PATHS,
        "repo_paths": _REPO_PATHS,
    }
