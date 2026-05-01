"""Connector Catalog router — every external integration with risk + launch phase."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from auto_client_acquisition.connector_catalog import (
    all_risks,
    catalog_summary,
    connector_risks,
    connector_status,
    get_connector,
    list_connectors,
)

router = APIRouter(prefix="/api/v1/connector-catalog", tags=["connector-catalog"])


@router.get("/catalog")
async def catalog() -> dict[str, Any]:
    return list_connectors()


@router.get("/summary")
async def summary() -> dict[str, Any]:
    return catalog_summary()


@router.get("/status")
async def status() -> dict[str, Any]:
    return connector_status()


@router.get("/risks")
async def risks() -> dict[str, Any]:
    return all_risks()


@router.get("/{connector_key}")
async def detail(connector_key: str) -> dict[str, Any]:
    c = get_connector(connector_key)
    if c is None:
        return {"error": f"unknown connector: {connector_key}"}
    return {**c.to_dict(), "risks_ar": connector_risks(connector_key)}
