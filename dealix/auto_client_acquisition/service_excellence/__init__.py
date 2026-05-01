"""Service Excellence OS — يضمن أن كل خدمة هي الأفضل قبل الإطلاق.

Feature matrix + scoring + workflow validation + competitor gap +
proof metrics + quality review + improvement backlog + launch package.
"""

from __future__ import annotations

from .competitor_gap import compare_against_categories
from .feature_matrix import (
    build_feature_matrix,
    classify_features,
    prioritize_features,
    recommend_missing_features,
)
from .launch_package import (
    build_demo_script,
    build_landing_page_outline,
    build_onboarding_checklist,
    build_sales_script,
    build_service_launch_package,
)
from .proof_metrics import (
    build_proof_pack_template_excellence,
    calculate_service_roi_estimate,
    required_proof_metrics,
    summarize_proof_ar,
)
from .quality_review import (
    block_if_missing_approval_policy,
    block_if_missing_proof,
    block_if_unclear_pricing,
    block_if_unsafe_channel,
    review_service_before_launch,
)
from .research_lab import (
    build_monthly_service_review,
    build_service_research_brief,
    generate_feature_hypotheses,
    recommend_next_experiments,
)
from .service_improvement_backlog import (
    build_backlog,
    convert_feedback_to_backlog,
    prioritize_backlog_items,
    recommend_weekly_improvements,
)
from .service_scoring import (
    calculate_service_excellence_score,
    score_automation,
    score_clarity,
    score_compliance,
    score_proof,
    score_speed_to_value,
    score_upsell,
)

__all__ = [
    # competitor_gap
    "compare_against_categories",
    # feature_matrix
    "build_feature_matrix", "classify_features",
    "prioritize_features", "recommend_missing_features",
    # launch_package
    "build_demo_script", "build_landing_page_outline",
    "build_onboarding_checklist", "build_sales_script",
    "build_service_launch_package",
    # proof_metrics
    "build_proof_pack_template_excellence", "calculate_service_roi_estimate",
    "required_proof_metrics", "summarize_proof_ar",
    # quality_review
    "block_if_missing_approval_policy", "block_if_missing_proof",
    "block_if_unclear_pricing", "block_if_unsafe_channel",
    "review_service_before_launch",
    # research_lab
    "build_monthly_service_review", "build_service_research_brief",
    "generate_feature_hypotheses", "recommend_next_experiments",
    # service_improvement_backlog
    "build_backlog", "convert_feedback_to_backlog",
    "prioritize_backlog_items", "recommend_weekly_improvements",
    # service_scoring
    "calculate_service_excellence_score", "score_automation",
    "score_clarity", "score_compliance", "score_proof",
    "score_speed_to_value", "score_upsell",
]
