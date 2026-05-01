"""
Growth Operator — thin product-facing aliases over innovation + business.

لا يكرر منطق ten-in-ten؛ يعرّف مسارات متوقعة في وثائق الـ beta والـ smoke.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from auto_client_acquisition.business.proof_pack import build_demo_proof_pack
from auto_client_acquisition.innovation.growth_missions import list_growth_missions

router = APIRouter(prefix="/api/v1/growth-operator", tags=["growth_operator"])


@router.get("/missions")
async def missions() -> dict[str, Any]:
    """نفس محتوى ``GET /api/v1/innovation/growth-missions`` مع تسمية منتجية."""
    data = list_growth_missions()
    if isinstance(data, dict):
        out = dict(data)
        out["canonical_route"] = "/api/v1/innovation/growth-missions"
        return out
    return {"missions": data, "canonical_route": "/api/v1/innovation/growth-missions"}


@router.get("/proof-pack/demo")
async def proof_pack_demo() -> dict[str, Any]:
    """نفس ``GET /api/v1/business/proof-pack/demo`` — مسار موحّد للعرض في الـ beta."""
    pack = build_demo_proof_pack()
    if isinstance(pack, dict):
        out = dict(pack)
        out["canonical_route"] = "/api/v1/business/proof-pack/demo"
        return out
    return {"pack": pack, "canonical_route": "/api/v1/business/proof-pack/demo"}
