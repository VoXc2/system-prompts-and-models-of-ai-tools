"""Shared tenant scope for sovereign routes."""

from typing import Annotated

from fastapi import Depends, Query

DEFAULT_SOVEREIGN_TENANT_ID = "default_tenant"


def _tenant_id_query(
    tenant_id: str = Query(
        default=DEFAULT_SOVEREIGN_TENANT_ID,
        alias="tenant_id",
        description="Tenant scope for sovereign operations (نطاق المستأجر للعمليات السيادية).",
    ),
) -> str:
    return tenant_id


TenantIdQuery = Annotated[str, Depends(_tenant_id_query)]
