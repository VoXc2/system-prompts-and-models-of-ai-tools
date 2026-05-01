"""Skill Inventory — list every Dealix capability, categorized."""

from __future__ import annotations

# Curated, deterministic inventory of skills across the layers.
SKILL_INVENTORY: tuple[dict[str, object], ...] = (
    # platform_services
    {"id": "tool_gateway", "layer": "platform_services",
     "label_ar": "بوابة الأدوات الآمنة", "tier": "core"},
    {"id": "action_policy", "layer": "platform_services",
     "label_ar": "محرك سياسة الأفعال", "tier": "core"},
    {"id": "channel_registry", "layer": "platform_services",
     "label_ar": "سجل القنوات", "tier": "core"},
    {"id": "unified_inbox", "layer": "platform_services",
     "label_ar": "صندوق البريد الموحد", "tier": "core"},
    {"id": "action_ledger", "layer": "platform_services",
     "label_ar": "سجل الأفعال", "tier": "core"},
    {"id": "proof_ledger", "layer": "platform_services",
     "label_ar": "سجل الأثر", "tier": "core"},
    {"id": "service_catalog", "layer": "platform_services",
     "label_ar": "كتالوج الخدمات", "tier": "core"},
    {"id": "identity_resolution", "layer": "platform_services",
     "label_ar": "حل الهوية المتقاطع", "tier": "core"},
    # intelligence_layer
    {"id": "growth_brain", "layer": "intelligence_layer",
     "label_ar": "عقل النمو", "tier": "core"},
    {"id": "command_feed", "layer": "intelligence_layer",
     "label_ar": "بطاقات القرار اليومية", "tier": "core"},
    {"id": "mission_engine", "layer": "intelligence_layer",
     "label_ar": "محرك المهمات", "tier": "core"},
    {"id": "trust_score", "layer": "intelligence_layer",
     "label_ar": "Trust Score", "tier": "core"},
    {"id": "revenue_dna", "layer": "intelligence_layer",
     "label_ar": "DNA الإيرادات", "tier": "core"},
    {"id": "opportunity_simulator", "layer": "intelligence_layer",
     "label_ar": "محاكي الفرص", "tier": "core"},
    {"id": "competitive_moves", "layer": "intelligence_layer",
     "label_ar": "كاشف حركات المنافسين", "tier": "core"},
    {"id": "board_brief", "layer": "intelligence_layer",
     "label_ar": "موجز Founder Shadow Board", "tier": "core"},
    {"id": "decision_memory", "layer": "intelligence_layer",
     "label_ar": "ذاكرة القرارات", "tier": "core"},
    {"id": "action_graph", "layer": "intelligence_layer",
     "label_ar": "Action Graph", "tier": "core"},
    # growth_operator (existing)
    {"id": "first_10_opportunities", "layer": "growth_operator",
     "label_ar": "10 فرص في 10 دقائق", "tier": "kill_feature"},
    # security_curator
    {"id": "secret_redactor", "layer": "security_curator",
     "label_ar": "إخفاء الأسرار", "tier": "core"},
    {"id": "patch_firewall", "layer": "security_curator",
     "label_ar": "جدار الـ patches", "tier": "core"},
    # growth_curator
    {"id": "message_curator", "layer": "growth_curator",
     "label_ar": "مدقق الرسائل", "tier": "core"},
    {"id": "playbook_curator", "layer": "growth_curator",
     "label_ar": "مدقق الـ playbooks", "tier": "core"},
)


def inventory_skills() -> dict[str, object]:
    """Return the full skill inventory grouped by layer."""
    by_layer: dict[str, list[dict[str, object]]] = {}
    for s in SKILL_INVENTORY:
        layer = str(s["layer"])
        by_layer.setdefault(layer, []).append(dict(s))
    return {
        "total": len(SKILL_INVENTORY),
        "layers": sorted(by_layer.keys()),
        "by_layer": by_layer,
        "kill_features": [
            dict(s) for s in SKILL_INVENTORY if s.get("tier") == "kill_feature"
        ],
    }
