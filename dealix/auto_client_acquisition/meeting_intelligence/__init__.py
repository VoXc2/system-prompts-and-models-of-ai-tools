"""Meeting intelligence — transcript text to brief/follow-up (no Calendar insert)."""

from auto_client_acquisition.meeting_intelligence.followup_builder import build_post_meeting_followup
from auto_client_acquisition.meeting_intelligence.meeting_brief import build_pre_meeting_brief
from auto_client_acquisition.meeting_intelligence.transcript_parser import summarize_transcript_text

__all__ = [
    "build_post_meeting_followup",
    "build_pre_meeting_brief",
    "summarize_transcript_text",
]
