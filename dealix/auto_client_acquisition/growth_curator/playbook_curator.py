"""Playbook merge hints — deterministic stub."""

from __future__ import annotations

from typing import Any


def suggest_playbook_merge(playbooks: list[dict[str, Any]]) -> dict[str, Any]:
    """If two titles share same first word, suggest merge (demo)."""
    if len(playbooks) < 2:
        return {"merge_groups": [], "demo": True}
    titles = [str(p.get("title_ar") or p.get("title") or "") for p in playbooks]
    merge_groups: list[list[int]] = []
    for i, a in enumerate(titles):
        for j in range(i + 1, len(titles)):
            if a and titles[j] and a.split()[:1] == titles[j].split()[:1] and a.split()[:1]:
                merge_groups.append([i, j])
    return {"merge_groups": merge_groups[:3], "demo": True}
