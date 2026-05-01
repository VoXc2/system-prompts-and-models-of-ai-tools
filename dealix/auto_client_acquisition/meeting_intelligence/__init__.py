"""Meeting Intelligence — pre-meeting briefs + post-meeting follow-ups.

Designed to consume Google Meet transcripts (when OAuth + scopes allow) but
works fine with manually-pasted transcripts during private beta.

All outputs are Arabic, deterministic, and approval-required before any
external action.
"""

from __future__ import annotations

from .deal_risk import compute_deal_risk
from .followup_builder import build_post_meeting_followup
from .meeting_brief import build_pre_meeting_brief
from .objection_extractor import extract_objections
from .transcript_parser import parse_transcript_entries, summarize_meeting

__all__ = [
    "build_post_meeting_followup",
    "build_pre_meeting_brief",
    "compute_deal_risk",
    "extract_objections",
    "parse_transcript_entries",
    "summarize_meeting",
]
