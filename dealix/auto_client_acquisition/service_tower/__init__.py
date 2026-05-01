"""Service Tower — كل قدرات Dealix كخدمات قابلة للبيع والتشغيل الذاتي.

العميل يختار هدفه → النظام يوصي بالخدمة → يجمع البيانات → يقيّم المخاطر →
يكتب الخطة → يطلب الموافقات → يشغّل القنوات → يطلع Proof Pack.
"""

from __future__ import annotations

from .contract_templates import (
    draft_sla_outline,
    list_contract_templates,
)
from .deliverables import (
    build_client_report_outline,
    build_deliverables,
    build_internal_operator_checklist,
    build_proof_pack_template,
)
from .vertical_service_map import (
    VERTICALS_AR,
    list_verticals,
    map_industry_to_vertical,
    recommend_services_for_vertical,
)
from .mission_templates import (
    build_service_workflow,
    get_default_mission_steps,
    map_service_to_growth_mission,
)
from .pricing_engine import (
    calculate_monthly_offer,
    calculate_setup_fee,
    quote_service,
    recommend_plan_after_service,
)
from .service_catalog import (
    ALL_SERVICES,
    Service,
    catalog_summary,
    get_service,
    list_all_services,
)
from .service_scorecard import (
    build_service_scorecard,
    calculate_service_success_score,
    recommend_next_step,
    summarize_scorecard_ar,
)
from .service_wizard import (
    build_intake_questions,
    recommend_service,
    summarize_recommendation_ar,
    validate_service_inputs,
)
from .upgrade_paths import (
    build_upsell_message_ar,
    map_service_to_subscription,
    recommend_upgrade,
)
from .whatsapp_ceo_control import (
    build_ceo_daily_service_brief,
    build_end_of_day_service_report,
    build_risk_alert_card,
    build_service_approval_card,
)

__all__ = [
    # service_catalog
    "ALL_SERVICES", "Service", "catalog_summary",
    "get_service", "list_all_services",
    # service_wizard
    "build_intake_questions", "recommend_service",
    "summarize_recommendation_ar", "validate_service_inputs",
    # mission_templates
    "build_service_workflow", "get_default_mission_steps",
    "map_service_to_growth_mission",
    # pricing_engine
    "calculate_monthly_offer", "calculate_setup_fee",
    "quote_service", "recommend_plan_after_service",
    # deliverables
    "build_client_report_outline", "build_deliverables",
    "build_internal_operator_checklist", "build_proof_pack_template",
    # service_scorecard
    "build_service_scorecard", "calculate_service_success_score",
    "recommend_next_step", "summarize_scorecard_ar",
    # whatsapp_ceo_control
    "build_ceo_daily_service_brief", "build_end_of_day_service_report",
    "build_risk_alert_card", "build_service_approval_card",
    # upgrade_paths
    "build_upsell_message_ar", "map_service_to_subscription",
    "recommend_upgrade",
    # contract_templates
    "draft_sla_outline", "list_contract_templates",
    # vertical_service_map
    "VERTICALS_AR", "list_verticals", "map_industry_to_vertical",
    "recommend_services_for_vertical",
]
