"""JSON summary for /strategy page and integrations."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["Strategy"])

_BLUEPRINT_VERSION = "5.0.0-sovereign"


@router.get("/strategy/summary")
async def strategy_summary() -> dict:
    return {
        "product": "Dealix",
        "blueprint_version": _BLUEPRINT_VERSION,
        "positioning": "Dealix Sovereign Enterprise Growth OS - Arabic-first, Saudi-ready, board-usable",
        "vision": {
            "tagline_ar": "منصة سيادية تدير القرار والتنفيذ والثقة عبر المبيعات والشراكات والتوسع والاستحواذ",
            "tagline_en": "A sovereign operating system for decisions, execution, and trust across enterprise growth",
        },
        "moat_pillars": [
            "Decision-native: every recommendation is typed, evidence-backed, policy-aware",
            "Execution-durable: commitments are resumable, idempotent, and observable",
            "Trust-enforced: authorization + policy + audit + tool-verification ledger",
            "Arabic-first and Saudi-ready by design, not localization afterthought",
            "Enterprise-saleable surfaces for executives, board, partnerships, and corp dev",
        ],
        "competitive_moat": {
            "decision_plane": "Responses API + Structured Outputs + LangGraph interrupts/HITL",
            "execution_plane": "Temporal for durable business commitments beyond short-lived agent loops",
            "trust_plane": "OPA policy, OpenFGA authorization, Vault secrets, Keycloak identity",
            "data_plane": "Postgres + pgvector + contracts (CloudEvents/JSON Schema/AsyncAPI) + OTel",
            "operating_plane": "GitHub rulesets/environments/OIDC/attestations + release evidence",
        },
        "auditable_targets": [
            {"id": "recommendation_quality", "label_ar": "جودة القرار", "target": "Structured + evidence-backed + schema-bound", "unit": "quality_gate"},
            {"id": "durable_commitments", "label_ar": "متانة التنفيذ", "target": "Long-running commitments resumable after failure", "unit": "durability"},
            {"id": "approval_coverage", "label_ar": "تغطية الاعتماد", "target": "100% للأفعال الحساسة وغير القابلة للعكس", "unit": "governance"},
            {"id": "connector_hardening", "label_ar": "صلابة التكاملات", "target": "Versioned contracts with retry/idempotency/audit mapping", "unit": "integration_quality"},
            {"id": "traceability", "label_ar": "التتبع التشغيلي", "target": "OTel traces + correlation IDs عبر جميع المسارات", "unit": "observability"},
            {"id": "saudi_compliance", "label_ar": "جاهزية السعودية", "target": "PDPL + ECC/NCA mapping + AI governance controls", "unit": "compliance"},
        ],
        "design_principles": [
            {"id": "decision_native", "title_ar": "السيادة على القرار", "summary": "كل recommendation typed + evidence-backed + policy-aware"},
            {"id": "execution_durable", "title_ar": "السيادة على التنفيذ", "summary": "التزامات الأعمال durable + resumable + compensatable"},
            {"id": "trust_enforced", "title_ar": "السيادة على الثقة", "summary": "كل فعل authorized + policy-evaluated + audited"},
            {"id": "data_governed", "title_ar": "السيادة على البيانات", "summary": "عقود بيانات/أحداث + جودة + lineage + telemetry"},
            {"id": "arabic_saudi_first", "title_ar": "عربي أولاً سعودي الجاهزية", "summary": "المحتوى التنفيذي، الأسباب، والتقارير بالعربية الاحترافية"},
            {"id": "board_usable", "title_ar": "جاهزية مجلس الإدارة", "summary": "Evidence packs + approval center + risk heatmaps + actual vs forecast"},
        ],
        "market_frame": "الهيمنة تأتي من إغلاق القرار والتنفيذ والثقة داخل المنتج، لا من زيادة عدد الوكلاء فقط",
        "planes": [
            {
                "id": "decision",
                "name_ar": "Decision Plane",
                "mission": "كشف الإشارات، التحليل، التوصية، وتهيئة evidence packs مع HITL",
                "stack": [
                    "Responses API",
                    "Structured Outputs",
                    "Function Calling / MCP",
                    "LangGraph checkpoints + interrupts",
                ],
            },
            {
                "id": "execution",
                "name_ar": "Execution Plane",
                "mission": "تنفيذ الالتزامات الطويلة متعددة الأنظمة بشكل deterministic",
                "stack": [
                    "LangGraph for cognition loops",
                    "Temporal for durable commitments",
                    "Idempotency + timeout + compensation",
                ],
            },
            {
                "id": "trust",
                "name_ar": "Trust Plane",
                "mission": "تفعيل السياسات والتفويض والتدقيق والتحقق من الأفعال",
                "stack": ["OPA", "OpenFGA", "Vault", "Keycloak", "Tool Verification Ledger"],
            },
            {
                "id": "data",
                "name_ar": "Data Plane",
                "mission": "مصدر حقيقة تشغيلي موحّد مع تعاقدات بيانات ومراقبة جودة",
                "stack": [
                    "Postgres + pgvector",
                    "Airbyte + Unstructured",
                    "Great Expectations",
                    "CloudEvents + JSON Schema + AsyncAPI",
                    "OpenTelemetry",
                ],
            },
            {
                "id": "operating",
                "name_ar": "Operating Plane",
                "mission": "ضبط SDLC والإصدارات وحماية البيئات وإثبات provenance",
                "stack": [
                    "GitHub rulesets/protected branches",
                    "Environments + deployment protections",
                    "OIDC federation",
                    "Artifact attestations",
                    "External audit-log streaming",
                ],
            },
        ],
        "program_locks": {
            "planes": 5,
            "business_tracks": 6,
            "agent_roles": 3,
            "action_classes": 3,
            "approval_classes_min": 3,
            "reversibility_classes": 4,
            "sensitivity_model": "required",
            "provenance_freshness_confidence": "required_trio",
        },
        "business_tracks": [
            {
                "id": "revenue_os",
                "name_ar": "Revenue OS",
                "scope": ["capture/enrichment/qualification", "outreach/proposals/pricing governance", "contract and renewal motions"],
            },
            {
                "id": "partnership_os",
                "name_ar": "Partnership OS",
                "scope": ["partner scouting", "fit/economics scoring", "activation + scorecards"],
            },
            {
                "id": "corpdev_os",
                "name_ar": "M&A / CorpDev OS",
                "scope": ["target sourcing/screening", "DD orchestration and valuation", "investment committee and board packs"],
            },
            {
                "id": "expansion_os",
                "name_ar": "Expansion OS",
                "scope": ["market scanning/prioritization", "launch readiness + stop-loss", "post-launch actual vs forecast"],
            },
            {
                "id": "pmi_pmo_os",
                "name_ar": "PMI / PMO OS",
                "scope": ["Day-1 readiness", "30/60/90 integration", "synergy/risk tracking"],
            },
            {
                "id": "executive_board_os",
                "name_ar": "Executive / Board OS",
                "scope": ["board-ready memos", "approval center", "risk and portfolio governance"],
            },
        ],
        "mandatory_surfaces": [
            "Executive Room",
            "Approval Center",
            "Evidence Pack Viewer",
            "Partner Room",
            "DD Room",
            "Risk Board",
            "Policy Violations Board",
            "Actual vs Forecast Dashboard",
            "Revenue Funnel Control Center",
            "Partnership Scorecards",
            "M&A Pipeline Board",
            "Expansion Launch Console",
            "PMI 30/60/90 Engine",
            "Tool Verification Ledger",
            "Connector Health Board",
            "Release Gate Dashboard",
            "Saudi Compliance Matrix",
            "Model Routing Dashboard",
        ],
        "automation_policy": {
            "full_auto": [
                "intake and enrichment",
                "scoring and memo drafting",
                "evidence aggregation and workflow kickoff",
                "SLA reminders and task assignment",
                "variance/anomaly detection",
                "connector syncs + quality checks + telemetry",
            ],
            "human_approval_required": [
                "term sheet sending",
                "signature request",
                "strategic partner activation",
                "market launch",
                "M&A offer",
                "discount خارج السياسة",
                "data sharing عالي الحساسية",
                "production promotion",
                "capital commitments",
            ],
        },
        "routing_fabric": {
            "lanes": [
                {"id": "coding_lane", "purpose": "engineering and deterministic transformations"},
                {"id": "executive_reasoning_lane", "purpose": "board-level analysis and scenario reasoning"},
                {"id": "throughput_drafting_lane", "purpose": "high-volume drafts and summaries"},
                {"id": "fallback_lane", "purpose": "resilience under model/provider degradation"},
            ],
            "measured_metrics": [
                "latency",
                "schema adherence",
                "contradiction rate",
                "Arabic quality",
                "cost per successful task",
            ],
        },
        "connector_contract_requirements": [
            "contract",
            "version",
            "retry policy",
            "timeout policy",
            "idempotency key",
            "approval policy",
            "audit mapping",
            "telemetry mapping",
            "rollback/compensation notes",
        ],
        "readiness_definition": [
            "كل قرار business-critical يكون structured + evidence-backed + schema-bound",
            "كل long-running commitment يكون durable + resumable + crash-tolerant",
            "كل action حساس يحمل metadata: approval + reversibility + sensitivity",
            "كل connector يكون versioned مع retry/idempotency/audit mapping",
            "كل release يحمل rulesets + environments + OIDC + provenance",
            "كل surface قابل للتتبع عبر OTel + correlation IDs",
            "كل deployment مؤسسي يمر security review وLLM/tool red-team",
            "كل workflow حساس في السعودية يملك mapping واضح على PDPL/NCA/AI governance",
        ],
        "saudi_compliance_matrix": [
            "PDPL controls mapping",
            "ECC/NCA cyber controls checkpoints",
            "NIST AI RMF risk lifecycle",
            "OWASP LLM Top 10 mitigations",
        ],
        "phases": [
            {"id": 0, "name": "Foundation", "horizon_days": 90},
            {"id": 1, "name": "Differentiation", "horizon_months": "3-9"},
            {"id": 2, "name": "Enterprise scale", "horizon_months": "9-18"},
            {"id": 3, "name": "Geographic / category expansion", "horizon_months": "18-36"},
        ],
        "execution_phases_detail": [
            {
                "id": 0,
                "name_ar": "Sovereign Foundation",
                "window": "0–90 يوماً",
                "deliverables": ["Program locks", "5 planes bootstrap", "Approval Center + Evidence Pack", "Traceability baseline"],
            },
            {
                "id": 1,
                "name_ar": "Execution Closure",
                "window": "شهر 2–3",
                "deliverables": ["Temporal-backed commitments", "Connector facade contracts", "Contradiction engine alpha"],
            },
            {
                "id": 2,
                "name_ar": "Enterprise Hardening",
                "window": "شهر 4–9",
                "deliverables": ["OpenFGA/OPA rollout", "Vault + Keycloak integration", "Saudi compliance matrix operationalization"],
            },
            {
                "id": 3,
                "name_ar": "Category Dominance",
                "window": "شهر 10–36",
                "deliverables": ["Board OS maturity", "M&A + expansion playbooks", "regional scale with policy routing"],
            },
        ],
        "kpis": [
            {"axis": "decision", "metric": "evidence completeness + schema adherence + contradiction rate"},
            {"axis": "execution", "metric": "workflow completion rate + retry recoveries + compensation success"},
            {"axis": "trust", "metric": "approval SLA + policy violations + authorization denials"},
            {"axis": "market", "metric": "board adoption + partner contribution + expansion actual vs forecast"},
        ],
        "doc_paths": {
            "full_markdown_web": "/strategy/DEALIX_NEXT_LEVEL_MASTER_PLAN_AR.md",
            "ultimate_execution_ar": "/strategy/ULTIMATE_EXECUTION_MASTER_AR.md",
            "integration_master_ar": "/strategy/INTEGRATION_MASTER_AR.md",
            "investor_html": "/dealix-marketing/investor/00-investor-dealix-full-ar.html",
        },
        "repo_paths": {
            "blueprint": "salesflow-saas/MASTER-BLUEPRINT.mdc",
            "openclaw_config": "salesflow-saas/openclaw/openclaw-config.yaml",
            "ultimate_doc": "salesflow-saas/docs/ULTIMATE_EXECUTION_MASTER_AR.md",
            "integration_master": "salesflow-saas/docs/INTEGRATION_MASTER_AR.md",
        },
    }
