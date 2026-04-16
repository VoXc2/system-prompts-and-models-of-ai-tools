from __future__ import annotations

from app.planes.execution.workflow_engine import (
    DurableWorkflowEngine,
    WorkflowDefinition,
    WorkflowStep,
)


def _step(name: str, step_type: str = "auto", approval_class: str = "R0_AUTO") -> WorkflowStep:
    return WorkflowStep(name=name, step_type=step_type, approval_class=approval_class)


def register_all_workflows(engine: DurableWorkflowEngine) -> None:
    engine.register_workflow(WorkflowDefinition(
        name="sales_lead_to_close",
        name_ar="دورة المبيعات من الاستقطاب إلى الإغلاق",
        description="End-to-end sales pipeline from lead capture through close and expansion",
        description_ar="خط أنابيب المبيعات الشامل من استقطاب العميل المحتمل حتى الإغلاق والتوسع",
        os_module="sales",
        steps=[
            _step("lead_capture"),
            _step("enrichment"),
            _step("scoring"),
            _step("qualification"),
            _step("routing"),
            _step("outreach"),
            _step("meeting_orchestration"),
            _step("proposal_generation"),
            _step("margin_check"),
            _step("discount_approval", "approval_gate", "R2_APPROVE"),
            _step("e_signature_trigger", "hitl", "R2_APPROVE"),
            _step("onboarding_handoff"),
            _step("expansion_play"),
        ],
    ))

    engine.register_workflow(WorkflowDefinition(
        name="partnership_lifecycle",
        name_ar="دورة حياة الشراكات",
        description="Full partnership lifecycle from scouting to health reviews",
        description_ar="دورة حياة الشراكات الكاملة من الاستكشاف حتى مراجعات الأداء",
        os_module="partnership",
        steps=[
            _step("partner_scouting"),
            _step("strategic_fit_scoring"),
            _step("channel_economics"),
            _step("alliance_structure_design"),
            _step("term_sheet_draft"),
            _step("term_sheet_approval", "approval_gate", "R2_APPROVE"),
            _step("signature_orchestration", "hitl", "R2_APPROVE"),
            _step("partner_activation"),
            _step("partner_scorecards"),
            _step("contribution_margin_tracking"),
            _step("partner_health_review"),
        ],
    ))

    engine.register_workflow(WorkflowDefinition(
        name="ma_acquisition",
        name_ar="دورة الاستحواذ والاندماج",
        description="M&A pipeline from target sourcing through post-close integration",
        description_ar="خط أنابيب الاستحواذ والاندماج من استقطاب الأهداف حتى التكامل بعد الإغلاق",
        os_module="ma",
        steps=[
            _step("target_sourcing"),
            _step("screening"),
            _step("management_mapping"),
            _step("dd_request_orchestration"),
            _step("dd_room_control"),
            _step("legal_dd"),
            _step("financial_dd"),
            _step("product_dd"),
            _step("security_dd"),
            _step("valuation_range"),
            _step("synergy_model"),
            _step("investment_committee_pack"),
            _step("board_pack_review", "approval_gate", "R3_COMMITTEE"),
            _step("offer_strategy", "hitl", "R3_COMMITTEE"),
            _step("negotiation_support"),
            _step("signing_close", "hitl", "R3_COMMITTEE"),
            _step("post_close_integration_trigger"),
        ],
    ))

    engine.register_workflow(WorkflowDefinition(
        name="expansion_market_entry",
        name_ar="دخول الأسواق الجديدة",
        description="Market expansion from scanning through post-launch analytics",
        description_ar="التوسع في الأسواق من المسح حتى تحليلات ما بعد الإطلاق",
        os_module="expansion",
        steps=[
            _step("market_scanning"),
            _step("segment_prioritization"),
            _step("regulatory_assessment"),
            _step("pricing_strategy"),
            _step("channel_strategy"),
            _step("localized_gtm"),
            _step("launch_readiness"),
            _step("launch_approval", "approval_gate", "R2_APPROVE"),
            _step("canary_launch"),
            _step("stop_loss_check"),
            _step("partner_assisted_entry"),
            _step("post_launch_analytics"),
        ],
    ))

    engine.register_workflow(WorkflowDefinition(
        name="pmi_integration",
        name_ar="تكامل ما بعد الاندماج",
        description="Post-merger integration from day-1 readiness through executive reporting",
        description_ar="تكامل ما بعد الاندماج من جاهزية اليوم الأول حتى التقارير التنفيذية",
        os_module="pmi",
        steps=[
            _step("day1_readiness"),
            _step("plan_30_60_90"),
            _step("workstream_setup"),
            _step("owner_assignment"),
            _step("dependency_tracking"),
            _step("escalation_engine"),
            _step("synergy_realization"),
            _step("risk_register"),
            _step("issue_resolution_sla"),
            _step("executive_reporting"),
        ],
    ))
