"""Public Launch readiness gate — Layer 13.

Closes the loop from Paid Beta to Public Launch. All criteria are
deterministic and gated by Hard Rules (no live send, no scraping,
PDPL-first, approval-first).

Public surface:
- evaluate_public_launch_gate(state) -> GateVerdict
- pilot_tracker_summary(pilots) -> PilotSummary
- compute_pdpl_compliance(state) -> PDPLReport
- compute_brand_moat_score(state) -> BrandMoatScore
"""

from .gate import (
    GateVerdict,
    GateCriterion,
    evaluate_public_launch_gate,
    PUBLIC_LAUNCH_CRITERIA,
)
from .pilot_tracker import (
    PilotRecord,
    PilotSummary,
    pilot_tracker_summary,
)
from .pdpl_compliance import (
    PDPLReport,
    PDPLCheck,
    compute_pdpl_compliance,
)
from .brand_moat import (
    BrandMoatScore,
    BrandMoatDimension,
    compute_brand_moat_score,
)

__all__ = [
    "GateVerdict",
    "GateCriterion",
    "evaluate_public_launch_gate",
    "PUBLIC_LAUNCH_CRITERIA",
    "PilotRecord",
    "PilotSummary",
    "pilot_tracker_summary",
    "PDPLReport",
    "PDPLCheck",
    "compute_pdpl_compliance",
    "BrandMoatScore",
    "BrandMoatDimension",
    "compute_brand_moat_score",
]
