"""Buying committee role lines — business roles only, no fabricated individuals."""

from __future__ import annotations

from typing import List

from app.models.lead_engine import LeadEngineStakeholderRole


DEFAULT_ROLE_KEYS = [
    ("owner", "owner", 85),
    ("sales_head", "director", 70),
    ("operations", "manager", 55),
    ("finance", "manager", 45),
    ("it_digital", "manager", 40),
]


def build_stakeholder_rows_for_lead(
    tenant_id, lead_id, icp_buyer_roles: List[str], source: str = "icp_template"
) -> List[LeadEngineStakeholderRole]:
    """Create role rows from ICP; influence weights are templates, not people."""
    rows = []
    roles = icp_buyer_roles or [r[0] for r in DEFAULT_ROLE_KEYS]
    for rk in roles[:8]:
        match = next((x for x in DEFAULT_ROLE_KEYS if x[0] == rk), None)
        inf = match[2] if match else 50
        rows.append(
            LeadEngineStakeholderRole(
                tenant_id=tenant_id,
                lead_id=lead_id,
                role_key=rk,
                seniority=match[1] if match else "unknown",
                influence_0_100=inf,
                confidence=60,
                source=source,
                engagement_path_hint="whatsapp_then_call" if rk in ("owner", "sales_head") else "email",
            )
        )
    if not rows:
        for rk, sen, inf in DEFAULT_ROLE_KEYS:
            rows.append(
                LeadEngineStakeholderRole(
                    tenant_id=tenant_id,
                    lead_id=lead_id,
                    role_key=rk,
                    seniority=sen,
                    influence_0_100=inf,
                    confidence=55,
                    source=source,
                    engagement_path_hint="whatsapp_then_call",
                )
            )
    return rows
