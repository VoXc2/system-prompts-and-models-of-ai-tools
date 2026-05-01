"""Launch Ops — Private Beta launch workflow + Go/No-Go gates + scorecards.

Connects everything else into a single launch-day operating layer:
  - private_beta: today's offer, gates, FAQ
  - demo_flow: 12-min demo script consolidator
  - outreach_messages: first-20 plan + per-segment messages
  - go_no_go: deterministic launch readiness gate
  - launch_scorecard: daily ops metrics
"""

from __future__ import annotations

from .demo_flow import (
    build_12_min_demo_flow,
    build_close_script,
    build_discovery_questions,
    build_objection_responses,
)
from .go_no_go import build_launch_readiness, decide_go_no_go
from .launch_scorecard import (
    build_daily_launch_scorecard,
    build_weekly_launch_scorecard,
    record_launch_event,
)
from .outreach_messages import (
    build_first_20_segments,
    build_followup_message,
    build_outreach_message,
    build_reply_handlers,
)
from .private_beta import (
    PRIVATE_BETA_OFFER,
    build_private_beta_offer,
    build_private_beta_safety_notes,
    private_beta_faq,
)

__all__ = [
    # private_beta
    "PRIVATE_BETA_OFFER",
    "build_private_beta_offer",
    "build_private_beta_safety_notes",
    "private_beta_faq",
    # demo_flow
    "build_12_min_demo_flow",
    "build_close_script",
    "build_discovery_questions",
    "build_objection_responses",
    # outreach_messages
    "build_first_20_segments",
    "build_followup_message",
    "build_outreach_message",
    "build_reply_handlers",
    # go_no_go
    "build_launch_readiness",
    "decide_go_no_go",
    # launch_scorecard
    "build_daily_launch_scorecard",
    "build_weekly_launch_scorecard",
    "record_launch_event",
]
