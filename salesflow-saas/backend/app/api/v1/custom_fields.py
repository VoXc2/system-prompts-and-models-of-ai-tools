"""Custom fields management API for leads, deals, and contacts."""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, model_validator
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Any

from app.api.v1.deps import get_current_user, get_db
from app.models.custom_field import CustomField

router = APIRouter()

ALLOWED_ENTITY_TYPES = ("lead", "deal", "contact")
ALLOWED_FIELD_TYPES = ("text", "number", "select", "date", "boolean", "url", "email", "phone")


# --------------- Schemas ---------------

class CustomFieldCreate(BaseModel):
    entity_type: str  # lead | deal | contact
    field_name: str
    field_label: str
    field_type: str  # text | number | select | date | boolean | url | email | phone
    options: Optional[list[str]] = None
    is_required: bool = False
    sort_order: int = 0

    @model_validator(mode="after")
    def validate_field(self):
        if self.entity_type not in ALLOWED_ENTITY_TYPES:
            raise ValueError("entity_type يجب أن يكون lead أو deal أو contact")
        if self.field_type not in ALLOWED_FIELD_TYPES:
            raise ValueError(
                f"field_type يجب أن يكون أحد: {', '.join(ALLOWED_FIELD_TYPES)}"
            )
        if self.field_type == "select" and not self.options:
            raise ValueError("حقل القائمة المنسدلة يتطلب قائمة خيارات (options)")
        return self


class CustomFieldUpdate(BaseModel):
    field_name: Optional[str] = None
    field_label: Optional[str] = None
    field_type: Optional[str] = None
    options: Optional[list[str]] = None
    is_required: Optional[bool] = None
    sort_order: Optional[int] = None

    @model_validator(mode="after")
    def validate_field(self):
        if self.field_type is not None and self.field_type not in ALLOWED_FIELD_TYPES:
            raise ValueError(
                f"field_type يجب أن يكون أحد: {', '.join(ALLOWED_FIELD_TYPES)}"
            )
        if self.field_type == "select" and self.options is not None and len(self.options) == 0:
            raise ValueError("حقل القائمة المنسدلة يتطلب قائمة خيارات (options)")
        return self


class CustomFieldResponse(BaseModel):
    id: str
    entity_type: str
    field_name: str
    field_label: str
    field_type: str
    options: Optional[list[str]]
    is_required: bool
    sort_order: int
    tenant_id: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, obj: CustomField) -> "CustomFieldResponse":
        # updated_at is stored in settings JSON; fall back to created_at
        settings = obj.settings or {}
        updated_at = settings.get("updated_at", "")
        if not updated_at and obj.created_at:
            updated_at = obj.created_at.isoformat()
        return cls(
            id=str(obj.id),
            entity_type=obj.entity_type or "",
            field_name=obj.field_name or "",
            field_label=obj.field_label or "",
            field_type=obj.field_type or "text",
            options=obj.options if obj.options else None,
            is_required=obj.is_required or False,
            sort_order=obj.sort_order or 0,
            tenant_id=str(obj.tenant_id),
            created_at=obj.created_at.isoformat() if obj.created_at else "",
            updated_at=updated_at,
        )


class ReorderItem(BaseModel):
    field_id: str
    sort_order: int


class ReorderRequest(BaseModel):
    fields: list[ReorderItem]


class CustomFieldValueSet(BaseModel):
    entity_id: str
    value: Any


class CustomFieldValueResponse(BaseModel):
    field_id: str
    field_name: str
    field_label: str
    field_type: str
    entity_id: str
    value: Any
    updated_at: str

    model_config = {"from_attributes": True}


# --------------- Endpoints ---------------

@router.post("/custom-fields", response_model=CustomFieldResponse, status_code=201)
async def create_custom_field(
    data: CustomFieldCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new custom field definition."""
    tenant_id = current_user["tenant_id"]

    # Check for duplicate field_name within same entity_type
    result = await db.execute(
        select(CustomField).where(
            CustomField.tenant_id == tenant_id,
            CustomField.field_name == data.field_name,
            CustomField.entity_type == data.entity_type,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="اسم الحقل موجود مسبقاً لهذا النوع",
        )

    now = datetime.now(timezone.utc).isoformat()
    field = CustomField(
        tenant_id=tenant_id,
        entity_type=data.entity_type,
        field_name=data.field_name,
        field_label=data.field_label,
        field_type=data.field_type,
        options=data.options,
        is_required=data.is_required,
        sort_order=data.sort_order,
        settings={"updated_at": now},
    )
    db.add(field)
    await db.commit()
    await db.refresh(field)
    return CustomFieldResponse.from_orm_model(field)


@router.get("/custom-fields", response_model=list[CustomFieldResponse])
async def list_custom_fields(
    entity_type: Optional[str] = Query(None, description="Filter by entity type: lead, deal, contact"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all custom fields, optionally filtered by entity_type."""
    tenant_id = current_user["tenant_id"]

    stmt = select(CustomField).where(CustomField.tenant_id == tenant_id)
    if entity_type:
        if entity_type not in ALLOWED_ENTITY_TYPES:
            raise HTTPException(
                status_code=400,
                detail="entity_type يجب أن يكون lead أو deal أو contact",
            )
        stmt = stmt.where(CustomField.entity_type == entity_type)

    stmt = stmt.order_by(CustomField.sort_order)
    result = await db.execute(stmt)
    fields = result.scalars().all()
    return [CustomFieldResponse.from_orm_model(f) for f in fields]


@router.put("/custom-fields/{field_id}", response_model=CustomFieldResponse)
async def update_custom_field(
    field_id: str,
    data: CustomFieldUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update an existing custom field definition."""
    tenant_id = current_user["tenant_id"]

    result = await db.execute(
        select(CustomField).where(
            CustomField.id == UUID(field_id),
            CustomField.tenant_id == tenant_id,
        )
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="الحقل المخصص غير موجود")

    updates = data.model_dump(exclude_none=True)

    # If changing to select type, require options
    new_type = updates.get("field_type", field.field_type)
    new_options = updates.get("options", field.options)
    if new_type == "select" and not new_options:
        raise HTTPException(
            status_code=400,
            detail="حقل القائمة المنسدلة يتطلب قائمة خيارات (options)",
        )

    for key, value in updates.items():
        setattr(field, key, value)

    # Track updated_at in settings
    settings = dict(field.settings or {})
    settings["updated_at"] = datetime.now(timezone.utc).isoformat()
    field.settings = settings

    await db.commit()
    await db.refresh(field)
    return CustomFieldResponse.from_orm_model(field)


@router.delete("/custom-fields/{field_id}", status_code=204)
async def delete_custom_field(
    field_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a custom field."""
    tenant_id = current_user["tenant_id"]

    result = await db.execute(
        select(CustomField).where(
            CustomField.id == UUID(field_id),
            CustomField.tenant_id == tenant_id,
        )
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="الحقل المخصص غير موجود")

    await db.delete(field)
    await db.commit()


@router.put("/custom-fields/reorder", response_model=list[CustomFieldResponse])
async def reorder_custom_fields(
    data: ReorderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Reorder custom fields by updating their sort_order values."""
    tenant_id = current_user["tenant_id"]
    now = datetime.now(timezone.utc).isoformat()

    field_ids = [UUID(item.field_id) for item in data.fields]
    result = await db.execute(
        select(CustomField).where(
            CustomField.tenant_id == tenant_id,
            CustomField.id.in_(field_ids),
        )
    )
    fields_by_id = {str(f.id): f for f in result.scalars().all()}

    updated = []
    for item in data.fields:
        field = fields_by_id.get(item.field_id)
        if not field:
            raise HTTPException(
                status_code=404,
                detail=f"الحقل المخصص غير موجود: {item.field_id}",
            )
        field.sort_order = item.sort_order
        settings = dict(field.settings or {})
        settings["updated_at"] = now
        field.settings = settings
        updated.append(field)

    await db.commit()
    for f in updated:
        await db.refresh(f)

    updated.sort(key=lambda f: f.sort_order or 0)
    return [CustomFieldResponse.from_orm_model(f) for f in updated]


@router.post(
    "/custom-fields/{field_id}/values",
    response_model=CustomFieldValueResponse,
    status_code=201,
)
async def set_custom_field_value(
    field_id: str,
    data: CustomFieldValueSet,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Set or update a custom field value for a specific entity.

    Values are stored in the custom field's settings JSONB under 'values' key.
    """
    tenant_id = current_user["tenant_id"]

    result = await db.execute(
        select(CustomField).where(
            CustomField.id == UUID(field_id),
            CustomField.tenant_id == tenant_id,
        )
    )
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="الحقل المخصص غير موجود")

    # Validate value against field_type
    _validate_field_value(field, data.value)

    now = datetime.now(timezone.utc).isoformat()

    # Store values in settings JSONB under "values" -> {entity_id: {value, updated_at}}
    settings = dict(field.settings or {})
    values_map = dict(settings.get("values", {}))
    values_map[data.entity_id] = {"value": data.value, "updated_at": now}
    settings["values"] = values_map
    field.settings = settings

    await db.commit()
    await db.refresh(field)

    return CustomFieldValueResponse(
        field_id=str(field.id),
        field_name=field.field_name,
        field_label=field.field_label,
        field_type=field.field_type,
        entity_id=data.entity_id,
        value=data.value,
        updated_at=now,
    )


@router.get(
    "/custom-fields/values/{entity_type}/{entity_id}",
    response_model=list[CustomFieldValueResponse],
)
async def get_custom_field_values(
    entity_type: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get all custom field values for a specific entity."""
    tenant_id = current_user["tenant_id"]

    if entity_type not in ALLOWED_ENTITY_TYPES:
        raise HTTPException(
            status_code=400,
            detail="entity_type يجب أن يكون lead أو deal أو contact",
        )

    result = await db.execute(
        select(CustomField).where(
            CustomField.tenant_id == tenant_id,
            CustomField.entity_type == entity_type,
        )
    )
    fields = result.scalars().all()

    values = []
    for field in fields:
        settings = field.settings or {}
        values_map = settings.get("values", {})
        if entity_id in values_map:
            entry = values_map[entity_id]
            values.append(
                CustomFieldValueResponse(
                    field_id=str(field.id),
                    field_name=field.field_name,
                    field_label=field.field_label,
                    field_type=field.field_type,
                    entity_id=entity_id,
                    value=entry["value"],
                    updated_at=entry.get("updated_at", ""),
                )
            )

    return values


# --------------- Helpers ---------------

def _validate_field_value(field: CustomField, value: Any):
    """Validate a value against its field type definition."""
    field_type = field.field_type

    if value is None:
        if field.is_required:
            raise HTTPException(status_code=400, detail="هذا الحقل مطلوب")
        return

    if field_type == "number":
        if not isinstance(value, (int, float)):
            raise HTTPException(
                status_code=400, detail="القيمة يجب أن تكون رقماً"
            )
    elif field_type == "boolean":
        if not isinstance(value, bool):
            raise HTTPException(
                status_code=400, detail="القيمة يجب أن تكون true أو false"
            )
    elif field_type == "select":
        options = field.options or []
        if value not in options:
            raise HTTPException(
                status_code=400,
                detail=f"القيمة يجب أن تكون أحد الخيارات: {', '.join(options)}",
            )
    elif field_type in ("text", "date", "url", "email", "phone"):
        if not isinstance(value, str):
            raise HTTPException(
                status_code=400, detail="القيمة يجب أن تكون نصاً"
            )
