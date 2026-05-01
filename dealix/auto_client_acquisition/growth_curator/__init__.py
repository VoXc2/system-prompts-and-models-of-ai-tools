"""Growth Curator — self-improving review pass over messages, playbooks, missions.

Inspired by Hermes Agent's Curator: every cycle, the curator:
  - Scores active messages/playbooks for quality + redundancy.
  - Merges duplicates.
  - Archives weak performers.
  - Recommends the next experiment.
  - Ships an Arabic weekly report ("ماذا تعلمنا هذا الأسبوع").
"""

from __future__ import annotations

from .curator_report import build_weekly_curator_report
from .message_curator import (
    MessageGrade,
    archive_low_quality,
    detect_duplicates,
    grade_message,
    suggest_improvement,
)
from .mission_curator import recommend_next_mission, score_mission
from .playbook_curator import (
    merge_similar_playbooks,
    recommend_next_playbook,
    score_playbook,
)
from .skill_inventory import inventory_skills

__all__ = [
    "MessageGrade",
    "archive_low_quality",
    "build_weekly_curator_report",
    "detect_duplicates",
    "grade_message",
    "inventory_skills",
    "merge_similar_playbooks",
    "recommend_next_mission",
    "recommend_next_playbook",
    "score_mission",
    "score_playbook",
    "suggest_improvement",
]
