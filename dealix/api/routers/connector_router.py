"""Connector catalog HTTP."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from auto_client_acquisition.connectors.connector_catalog import build_connector_catalog

router = APIRouter(prefix="/api/v1/connectors", tags=["connectors"])


@router.get("/catalog")
async def catalog() -> dict[str, Any]:
    return build_connector_catalog()
