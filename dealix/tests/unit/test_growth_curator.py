"""Unit tests for the Growth Curator."""

from __future__ import annotations

from auto_client_acquisition.growth_curator import (
    build_weekly_curator_report,
    detect_duplicates,
    grade_message,
    inventory_skills,
    recommend_next_mission,
    recommend_next_playbook,
    score_mission,
    score_playbook,
    suggest_improvement,
)


# ── Skill Inventory ──────────────────────────────────────────
def test_inventory_lists_kill_feature():
    out = inventory_skills()
    assert out["total"] >= 20
    kill_ids = [s["id"] for s in out["kill_features"]]
    assert "first_10_opportunities" in kill_ids


def test_inventory_layers_present():
    out = inventory_skills()
    layers = set(out["layers"])
    assert {"platform_services", "intelligence_layer",
            "growth_curator", "security_curator"}.issubset(layers)


# ── Message Curator ──────────────────────────────────────────
def test_grades_natural_arabic_message_high():
    text = ("هلا أحمد، لاحظت توسعكم في فريق المبيعات. "
            "نشتغل على Dealix كمدير نمو عربي. "
            "يناسبك أعرض لك مثال 10 دقائق هذا الأسبوع؟")
    g = grade_message(text, sector="training")
    assert g.score >= 60
    assert g.verdict in ("publish", "needs_edit")


def test_blocks_risky_phrases():
    text = "آخر فرصة! ضمان 100% نتائج مضمونة. اضغط الآن."
    g = grade_message(text)
    assert g.risky_phrases
    assert g.verdict in ("needs_edit", "reject")


def test_rejects_non_arabic():
    text = "Hello there, just checking in. Cheers."
    g = grade_message(text)
    assert g.verdict == "reject"


def test_detects_near_duplicates():
    msgs = [
        "هلا أحمد، لاحظت توسعكم. يناسبك أعرض لك Pilot؟",
        "هلا محمد، لاحظت توسعكم. يناسبك أعرض لك Pilot؟",
        "totally unrelated message in english",
    ]
    pairs = detect_duplicates(msgs, threshold=0.8)
    assert any({i, j} == {0, 1} for i, j, _r in pairs)


def test_suggest_improvement_returns_skeleton():
    out = suggest_improvement("Hi")
    assert "suggested_skeleton_ar" in out
    assert "هلا" in out["suggested_skeleton_ar"]


# ── Playbook Curator ────────────────────────────────────────
def test_score_playbook_winner_tier():
    """Strong outcomes across all signals should push into winner/promising."""
    pb = {
        "used_count": 100, "accept_count": 90,
        "replied_count": 80, "meeting_count": 60, "deal_count": 40,
    }
    s = score_playbook(pb)
    assert s["score"] >= 50
    assert s["tier"] in ("winner", "promising")


def test_score_playbook_needs_work_tier():
    """Modest outcomes should map to needs_work."""
    pb = {
        "used_count": 100, "accept_count": 60,
        "replied_count": 40, "meeting_count": 20, "deal_count": 8,
    }
    s = score_playbook(pb)
    assert s["tier"] in ("needs_work", "promising")


def test_score_playbook_unproven_for_zero_uses():
    s = score_playbook({"used_count": 0})
    assert s["tier"] == "unproven"
    assert s["score"] == 0


def test_recommend_next_playbook_default_when_empty():
    rec = recommend_next_playbook([])
    assert rec["recommended_id"] == "default_warm_outreach"


def test_recommend_next_playbook_picks_promising_first():
    pbs = [
        {"id": "p1", "title": "Winner", "tier": "winner", "score": 80},
        {"id": "p2", "title": "Promising", "tier": "promising", "score": 60},
    ]
    rec = recommend_next_playbook(pbs)
    assert rec["recommended_id"] == "p2"


# ── Mission Curator ─────────────────────────────────────────
def test_score_mission_ship_it_with_strong_outcome():
    out = score_mission({
        "opportunities_generated": 10,
        "drafts_approved": 5,
        "meetings_booked": 3,
        "revenue_influenced_sar": 60_000,
        "time_to_value_minutes": 8,
        "risks_blocked": 2,
    })
    assert out["score"] >= 70
    assert out["verdict"] == "ship_it_widely"


def test_recommend_next_mission_starts_with_kill_feature():
    rec = recommend_next_mission(None)
    assert rec["recommended_mission_id"] == "first_10_opportunities"


def test_recommend_next_mission_after_kill_feature():
    history = [{"mission_id": "first_10_opportunities"}]
    rec = recommend_next_mission(history, growth_brain={
        "growth_priorities": ["fill_pipeline"],
    })
    assert rec["recommended_mission_id"] == "meeting_booking_sprint"


# ── Curator Report ───────────────────────────────────────────
def test_weekly_report_handles_empty_input():
    rep = build_weekly_curator_report()
    assert rep["messages"]["total"] == 0
    assert rep["playbooks"]["total"] == 0
    assert rep["missions"]["total"] == 0
    assert rep["next_playbook"]["recommended_id"]


def test_weekly_report_marks_low_quality_for_archive():
    rep = build_weekly_curator_report(messages=[
        {"id": "m1", "text": "Hi"},
        {"id": "m2", "text": "آخر فرصة! ضمان 100% نتائج مضمونة!"},
    ])
    assert rep["messages"]["to_archive"] >= 1
