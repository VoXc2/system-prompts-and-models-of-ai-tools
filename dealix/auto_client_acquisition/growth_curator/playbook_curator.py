"""Playbook Curator — score, merge, and recommend playbooks based on outcomes."""

from __future__ import annotations

from difflib import SequenceMatcher


def score_playbook(playbook: dict[str, object]) -> dict[str, object]:
    """
    Score a playbook on outcome quality.

    Inputs (all optional, defaults are conservative):
        used_count, accept_count, replied_count, meeting_count, deal_count
    """
    used = int(playbook.get("used_count", 0) or 0)
    accepted = int(playbook.get("accept_count", 0) or 0)
    replied = int(playbook.get("replied_count", 0) or 0)
    meetings = int(playbook.get("meeting_count", 0) or 0)
    deals = int(playbook.get("deal_count", 0) or 0)

    if used <= 0:
        return {
            "score": 0, "tier": "unproven",
            "accept_rate": 0.0, "reply_rate": 0.0,
            "meeting_rate": 0.0, "deal_rate": 0.0,
        }

    accept_rate = accepted / used if used else 0.0
    reply_rate = replied / used if used else 0.0
    meeting_rate = meetings / used if used else 0.0
    deal_rate = deals / used if used else 0.0

    # Weighted score; deals matter most.
    score = int(round(
        100 * (
            0.10 * accept_rate
            + 0.20 * reply_rate
            + 0.30 * meeting_rate
            + 0.40 * deal_rate
        )
    ))
    score = max(0, min(100, score))

    if score >= 70:
        tier = "winner"
    elif score >= 40:
        tier = "promising"
    elif score >= 20:
        tier = "needs_work"
    else:
        tier = "candidate_archive"

    return {
        "score": score, "tier": tier,
        "accept_rate": round(accept_rate, 3),
        "reply_rate": round(reply_rate, 3),
        "meeting_rate": round(meeting_rate, 3),
        "deal_rate": round(deal_rate, 3),
    }


def merge_similar_playbooks(
    playbooks: list[dict[str, object]],
    *,
    field: str = "title",
    threshold: float = 0.80,
) -> list[dict[str, object]]:
    """
    Group near-identical playbooks (by title similarity) and return
    a list of merge suggestions:
        [{"keep_index", "merge_indices", "merged_title", "similarity"}]
    """
    suggestions: list[dict[str, object]] = []
    used: set[int] = set()
    n = len(playbooks)
    for i in range(n):
        if i in used:
            continue
        merge_indices: list[int] = []
        title_i = str(playbooks[i].get(field, "") or "")
        for j in range(i + 1, n):
            if j in used:
                continue
            title_j = str(playbooks[j].get(field, "") or "")
            if not title_i or not title_j:
                continue
            ratio = SequenceMatcher(None, title_i, title_j).ratio()
            if ratio >= threshold:
                merge_indices.append(j)
                used.add(j)
        if merge_indices:
            used.add(i)
            suggestions.append({
                "keep_index": i,
                "merge_indices": merge_indices,
                "merged_title": title_i,
                "similarity_threshold": threshold,
            })
    return suggestions


def recommend_next_playbook(
    scored_playbooks: list[dict[str, object]],
    *,
    sector: str | None = None,
) -> dict[str, object]:
    """
    Pick the next playbook to run given scored history.

    Strategy: prefer "promising" over "winner" (winners are saturated).
    If sector is given, prefer playbooks tagged with that sector.
    Falls back to deterministic default.
    """
    if not scored_playbooks:
        return {
            "recommended_id": "default_warm_outreach",
            "title_ar": "تواصل دافئ مع 10 جهات مختارة",
            "reason_ar": "لا يوجد تاريخ بعد — ابدأ بالـ playbook الافتراضي.",
        }

    candidates = list(scored_playbooks)
    if sector:
        sector_filtered = [
            p for p in candidates
            if sector.lower() in str(p.get("sectors", "")).lower()
        ]
        if sector_filtered:
            candidates = sector_filtered

    # Promote "promising" first, then "winner", then by score.
    tier_priority = {"promising": 0, "winner": 1, "needs_work": 2,
                     "candidate_archive": 3, "unproven": 4}
    candidates.sort(key=lambda p: (
        tier_priority.get(str(p.get("tier", "unproven")), 9),
        -int(p.get("score", 0) or 0),
    ))
    chosen = candidates[0]
    return {
        "recommended_id": chosen.get("id"),
        "title_ar": chosen.get("title", "?"),
        "reason_ar": (
            f"الـ tier: {chosen.get('tier')}, الـ score: {chosen.get('score')}."
        ),
    }
