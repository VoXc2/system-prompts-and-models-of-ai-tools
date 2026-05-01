"""Curator Report — Arabic weekly summary of what improved, what was archived."""

from __future__ import annotations

from typing import Any

from .message_curator import detect_duplicates, grade_message
from .mission_curator import score_mission
from .playbook_curator import (
    merge_similar_playbooks,
    recommend_next_playbook,
    score_playbook,
)


def build_weekly_curator_report(
    *,
    messages: list[dict[str, Any]] | None = None,
    playbooks: list[dict[str, Any]] | None = None,
    missions: list[dict[str, Any]] | None = None,
    sector: str | None = None,
) -> dict[str, Any]:
    """
    Build a weekly Arabic curator report.

    Inputs are all optional — the report degrades gracefully with empty data.
    """
    messages = messages or []
    playbooks = playbooks or []
    missions = missions or []

    # 1. Grade messages.
    graded_messages: list[dict[str, Any]] = []
    for m in messages:
        text = str(m.get("text", "") or "")
        grade = grade_message(text, sector=sector)
        graded_messages.append({
            "id": m.get("id"),
            "text": text,
            "grade": grade.to_dict(),
        })
    archived_messages = [g for g in graded_messages if g["grade"]["verdict"] == "reject"]
    needs_edit = [g for g in graded_messages if g["grade"]["verdict"] == "needs_edit"]

    # 2. Detect duplicate messages.
    dup_pairs = detect_duplicates([str(m.get("text", "") or "") for m in messages])

    # 3. Score playbooks.
    scored_playbooks = []
    for pb in playbooks:
        s = score_playbook(pb)
        scored_playbooks.append({**pb, **s})
    merge_suggestions = merge_similar_playbooks(playbooks)

    # 4. Score missions.
    scored_missions = []
    for mn in missions:
        s = score_mission(mn)
        scored_missions.append({**mn, **s})

    # 5. Recommend next playbook.
    next_pb = recommend_next_playbook(scored_playbooks, sector=sector)

    # 6. Build human summary.
    summary_ar: list[str] = []
    summary_ar.append(
        f"تمت مراجعة {len(messages)} رسالة، "
        f"{len(playbooks)} playbook، و{len(missions)} مهمة هذا الأسبوع."
    )
    if archived_messages:
        summary_ar.append(
            f"تم اقتراح أرشفة {len(archived_messages)} رسالة ضعيفة الجودة."
        )
    if needs_edit:
        summary_ar.append(f"{len(needs_edit)} رسالة تحتاج تعديلاً قبل النشر.")
    if dup_pairs:
        summary_ar.append(
            f"تم اكتشاف {len(dup_pairs)} زوج رسائل متشابهة (للدمج)."
        )
    if merge_suggestions:
        summary_ar.append(
            f"تم اقتراح دمج {len(merge_suggestions)} مجموعة من الـ playbooks."
        )

    next_action_ar = next_pb.get("title_ar", "تواصل دافئ مع 10 جهات مختارة")

    return {
        "summary_ar": summary_ar,
        "messages": {
            "total": len(messages),
            "publishable": sum(1 for g in graded_messages if g["grade"]["verdict"] == "publish"),
            "needs_edit": len(needs_edit),
            "to_archive": len(archived_messages),
            "duplicate_pairs": len(dup_pairs),
        },
        "playbooks": {
            "total": len(playbooks),
            "winners": sum(1 for p in scored_playbooks if p.get("tier") == "winner"),
            "promising": sum(1 for p in scored_playbooks if p.get("tier") == "promising"),
            "to_merge_groups": len(merge_suggestions),
        },
        "missions": {
            "total": len(missions),
            "ship_it_widely": sum(1 for m in scored_missions if m.get("verdict") == "ship_it_widely"),
            "iterate": sum(1 for m in scored_missions if m.get("verdict") == "iterate"),
            "rework_or_retire": sum(1 for m in scored_missions if m.get("verdict") == "rework_or_retire"),
        },
        "next_playbook": next_pb,
        "recommended_next_action_ar": next_action_ar,
        "graded_messages": graded_messages,
        "scored_playbooks": scored_playbooks,
        "scored_missions": scored_missions,
        "merge_suggestions": merge_suggestions,
    }
