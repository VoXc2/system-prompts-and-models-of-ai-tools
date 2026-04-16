"""
Dealix Sovereign Growth, Execution & Governance OS — master control endpoint.

Provides unified health check, plane status, event catalog, and system manifest.
"""

from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter

from app.planes.decision.schemas import ApprovalClass, ReversibilityClass, SensitivityClass
from app.planes.decision.guardrails import AUTO_ALLOWED_ACTIONS, HITL_ACTIONS
from app.planes.data.event_contracts import EVENT_CATALOG
from app.planes.data.connector_registry import CONNECTOR_REGISTRY
from app.planes.execution.workflow_engine import (
    SALES_WORKFLOW, PARTNERSHIP_WORKFLOW, MA_WORKFLOW,
    EXPANSION_WORKFLOW, PMI_WORKFLOW,
)
from app.planes.operating.release_gates import DEFAULT_GATES, Environment

router = APIRouter(prefix="/sovereign", tags=["Sovereign OS — نظام التشغيل المؤسسي"])


@router.get("/health")
async def sovereign_health():
    """Five-plane health check."""
    return {
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "planes": {
            "decision": {
                "status": "active",
                "components": ["model_router", "guardrails", "structured_outputs", "tracing"],
            },
            "execution": {
                "status": "active",
                "runtime": "celery_langgraph",
                "target_runtime": "temporal",
                "components": ["workflow_engine", "sla_tracker", "hitl_checkpoints"],
            },
            "trust": {
                "status": "active",
                "components": ["policy_engine", "authorization", "evidence_packs", "compliance_matrix"],
                "target_components": ["opa", "openfga", "vault", "keycloak"],
            },
            "data": {
                "status": "active",
                "components": ["event_contracts", "connector_registry", "postgres", "pgvector"],
                "target_components": ["airbyte", "unstructured", "great_expectations", "otel"],
            },
            "operating": {
                "status": "active",
                "components": ["release_gates", "environment_protection"],
                "target_components": ["github_rulesets", "oidc_federation", "artifact_attestations"],
            },
        },
        "os_modules": [
            {"id": "sales_revenue_os", "name_ar": "نظام المبيعات والإيرادات", "status": "active"},
            {"id": "partnership_os", "name_ar": "نظام الشراكات", "status": "active"},
            {"id": "ma_corporate_dev_os", "name_ar": "نظام الاستحواذ والتطوير المؤسسي", "status": "active"},
            {"id": "expansion_os", "name_ar": "نظام التوسع", "status": "active"},
            {"id": "pmi_strategic_pmo", "name_ar": "نظام إدارة التكامل الاستراتيجي", "status": "active"},
            {"id": "executive_board_os", "name_ar": "نظام القيادة التنفيذية ومجلس الإدارة", "status": "active"},
        ],
    }


@router.get("/manifest")
async def system_manifest():
    """Full system manifest — all OS modules, surfaces, planes, and capabilities."""
    return {
        "name": "Dealix Sovereign Growth, Execution & Governance OS",
        "name_ar": "ديلكس — نظام التشغيل المؤسسي للنمو والتنفيذ والحوكمة",
        "version": "1.0.0",
        "os_modules": {
            "sales_revenue_os": {
                "name_ar": "نظام المبيعات والإيرادات",
                "capabilities": [
                    "lead_capture", "enrichment", "scoring", "qualification", "routing",
                    "multichannel_outreach", "meeting_orchestration", "proposal_cpq",
                    "discount_approval", "e_signature", "onboarding_handoff",
                    "renewal_upsell_expansion",
                ],
            },
            "partnership_os": {
                "name_ar": "نظام الشراكات",
                "capabilities": [
                    "partner_scouting", "strategic_fit_scoring", "channel_economics",
                    "alliance_structure", "term_sheet", "approval_routing",
                    "signature_orchestration", "activation", "scorecards",
                    "contribution_margin_tracking", "health_renewal_expansion",
                ],
            },
            "ma_corporate_dev_os": {
                "name_ar": "نظام الاستحواذ والتطوير المؤسسي",
                "capabilities": [
                    "target_sourcing", "screening", "management_mapping",
                    "dd_orchestration", "dd_room_control",
                    "legal_financial_product_security_dd",
                    "valuation_range", "synergy_model", "ic_pack", "board_pack",
                    "offer_strategy", "negotiation_support",
                    "signing_close", "pmi_trigger",
                ],
            },
            "expansion_os": {
                "name_ar": "نظام التوسع",
                "capabilities": [
                    "market_scanning", "segment_prioritization",
                    "regulatory_readiness", "pricing_channel_strategy",
                    "localized_gtm", "launch_readiness", "canary_launch",
                    "stop_loss", "partner_assisted_entry", "post_launch_analytics",
                ],
            },
            "pmi_strategic_pmo": {
                "name_ar": "نظام إدارة التكامل الاستراتيجي",
                "capabilities": [
                    "day1_readiness", "30_60_90_plans", "integration_workstreams",
                    "owner_assignment", "dependency_tracking", "escalation_engine",
                    "synergy_realization_tracking", "risk_register",
                    "issue_resolution_sla", "executive_reporting",
                ],
            },
            "executive_board_os": {
                "name_ar": "نظام القيادة التنفيذية ومجلس الإدارة",
                "capabilities": [
                    "executive_room", "board_memo_view", "evidence_pack_viewer",
                    "approval_center", "risk_heatmap", "forecast_vs_actual",
                    "partner_pipeline", "acquisition_pipeline",
                    "escalation_board", "next_best_action",
                    "policy_violations_board",
                ],
            },
        },
        "live_surfaces": [
            {"id": "executive_room", "name_ar": "غرفة القيادة التنفيذية"},
            {"id": "approval_center", "name_ar": "مركز الاعتماد"},
            {"id": "evidence_pack_viewer", "name_ar": "عارض حزم الأدلة"},
            {"id": "partner_room", "name_ar": "غرفة الشراكات"},
            {"id": "dd_room", "name_ar": "غرفة الفحص النافي للجهالة"},
            {"id": "risk_board", "name_ar": "لوحة المخاطر"},
            {"id": "policy_violations_board", "name_ar": "لوحة مخالفات السياسات"},
            {"id": "forecast_dashboard", "name_ar": "لوحة الفعلي مقابل المتوقع"},
            {"id": "revenue_funnel", "name_ar": "مركز التحكم بقمع الإيرادات"},
            {"id": "partner_scorecards", "name_ar": "بطاقات أداء الشركاء"},
            {"id": "ma_pipeline", "name_ar": "مسار الاستحواذات"},
            {"id": "expansion_console", "name_ar": "وحدة تحكم التوسع"},
            {"id": "pmi_engine", "name_ar": "محرك التكامل 30/60/90"},
            {"id": "tool_ledger", "name_ar": "سجل التحقق من الأدوات"},
            {"id": "connector_health", "name_ar": "لوحة صحة الموصلات"},
            {"id": "release_gates", "name_ar": "لوحة بوابات الإصدار"},
            {"id": "compliance_matrix", "name_ar": "مصفوفة الامتثال السعودية"},
            {"id": "model_routing", "name_ar": "لوحة توجيه النماذج"},
        ],
        "approval_classes": [c.value for c in ApprovalClass],
        "sensitivity_classes": [c.value for c in SensitivityClass],
        "reversibility_classes": [c.value for c in ReversibilityClass],
    }


@router.get("/event-catalog")
async def event_catalog():
    """Full event catalog — all typed CloudEvents in the system."""
    return {
        "total_events": len(EVENT_CATALOG),
        "events": {
            k: {
                "description": v["description"],
                "description_ar": v["description_ar"],
                "schema": v["schema"],
            }
            for k, v in EVENT_CATALOG.items()
        },
    }


@router.get("/automation-map")
async def automation_map():
    """Automation classification — auto-allowed vs HITL-gated actions."""
    return {
        "fully_automated": sorted(AUTO_ALLOWED_ACTIONS),
        "fully_automated_ar": "مؤتمت بالكامل بلا اعتماد",
        "hitl_gated": sorted(HITL_ACTIONS),
        "hitl_gated_ar": "مؤتمت مع اعتماد قبل الالتزام",
    }


@router.get("/workflows")
async def workflow_catalog():
    """Available durable workflow definitions."""
    workflows = [SALES_WORKFLOW, PARTNERSHIP_WORKFLOW, MA_WORKFLOW, EXPANSION_WORKFLOW, PMI_WORKFLOW]
    return [
        {
            "type": w.workflow_type,
            "description": w.description,
            "description_ar": w.description_ar,
            "max_duration_days": w.max_duration.days if w.max_duration else None,
        }
        for w in workflows
    ]


@router.get("/release-gates")
async def release_gate_templates():
    """Release gate templates per environment."""
    return {
        env.value: gates
        for env, gates in DEFAULT_GATES.items()
    }


@router.get("/connectors")
async def list_connectors():
    """All registered connector facades."""
    return [
        {
            "connector_id": c.connector_id,
            "name": c.name,
            "name_ar": c.name_ar,
            "type": c.connector_type.value,
            "version": c.version,
            "status": c.status.value,
            "retry_config": c.retry_config,
            "audit_enabled": c.audit_enabled,
        }
        for c in CONNECTOR_REGISTRY
    ]
