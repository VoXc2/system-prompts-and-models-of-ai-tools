"""Custom fields management API for leads, deals, and contacts."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, model_validator
from typing import Optional, Any
from uuid import uuid4
from app.api.v1.deps import get_current_user, get_db

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


# --------------- Mock Data ---------------

_mock_fields: dict[str, list[dict]] = {}
_mock_values: dict[str, list[dict]] = {}

_SEED_FIELDS = [
    {
        "entity_type": "lead",
        "field_name": "lead_source",
        "field_label": "مصدر العميل",
        "field_type": "select",
        "options": ["موقع إلكتروني", "معرض", "إحالة", "إعلان", "اتصال مباشر"],
        "is_required": True,
        "sort_order": 1,
    },
    {
        "entity_type": "lead",
        "field_name": "company_size",
        "field_label": "حجم الشركة",
        "field_type": "select",
        "options": ["1-10", "11-50", "51-200", "201-500", "500+"],
        "is_required": False,
        "sort_order": 2,
    },
    {
        "entity_type": "deal",
        "field_name": "expected_budget",
        "field_label": "الميزانية المتوقعة",
        "field_type": "number",
        "options": None,
        "is_required": True,
        "sort_order": 1,
    },
    {
        "entity_type": "deal",
        "field_name": "closing_date",
        "field_label": "تاريخ الإغلاق المتوقع",
        "field_type": "date",
        "options": None,
        "is_required": False,
        "sort_order": 2,
    },
    {
        "entity_type": "contact",
        "field_name": "website",
        "field_label": "الموقع الإلكتروني",
        "field_type": "url",
        "options": None,
        "is_required": False,
        "sort_order": 1,
    },
    {
        "entity_type": "contact",
        "field_name": "is_decision_maker",
        "field_label": "صانع القرار",
        "field_type": "boolean",
        "options": None,
        "is_required": False,
        "sort_order": 2,
    },
    {
        "entity_type": "contact",
        "field_name": "secondary_phone",
        "field_label": "رقم الهاتف الإضافي",
        "field_type": "phone",
        "options": None,
        "is_required": False,
        "sort_order": 3,
    },
]

_SEED_VALUES = [
    {
        "field_name": "lead_source",
        "field_label": "مصدر العميل",
        "field_type": "select",
        "entity_id": "lead-001",
        "value": "معرض",
    },
    {
        "field_name": "company_size",
        "field_label": "حجم الشركة",
        "field_type": "select",
        "entity_id": "lead-001",
        "value": "51-200",
    },
    {
        "field_name": "expected_budget",
        "field_label": "الميزانية المتوقعة",
        "field_type": "number",
        "entity_id": "deal-001",
        "value": 75000,
    },
]


def _ensure_seed(tenant_id: str):
    if tenant_id not in _mock_fields:
        now = datetime.now(timezone.utc).isoformat()
        _mock_fields[tenant_id] = [
            {
                "id": str(uuid4()),
                "tenant_id": tenant_id,
                "created_at": now,
                "updated_at": now,
                **f,
            }
            for f in _SEED_FIELDS
        ]
        _mock_values[tenant_id] = []
        for sv in _SEED_VALUES:
            field = next(
                f for f in _mock_fields[tenant_id] if f["field_name"] == sv["field_name"]
            )
            _mock_values[tenant_id].append(
                {
                    "field_id": field["id"],
                    "field_name": sv["field_name"],
                    "field_label": sv["field_label"],
                    "field_type": sv["field_type"],
                    "entity_id": sv["entity_id"],
                    "value": sv["value"],
                    "updated_at": now,
                }
            )


# --------------- Endpoints ---------------

@router.post("/custom-fields", response_model=CustomFieldResponse, status_code=201)
async def create_custom_field(
    data: CustomFieldCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new custom field definition."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    # Check for duplicate field_name within same entity_type
    for f in _mock_fields[tenant_id]:
        if f["field_name"] == data.field_name and f["entity_type"] == data.entity_type:
            raise HTTPException(
                status_code=400,
                detail="اسم الحقل موجود مسبقاً لهذا النوع",
            )

    now = datetime.now(timezone.utc).isoformat()
    field = {
        "id": str(uuid4()),
        "entity_type": data.entity_type,
        "field_name": data.field_name,
        "field_label": data.field_label,
        "field_type": data.field_type,
        "options": data.options,
        "is_required": data.is_required,
        "sort_order": data.sort_order,
        "tenant_id": tenant_id,
        "created_at": now,
        "updated_at": now,
    }
    _mock_fields[tenant_id].append(field)
    return CustomFieldResponse(**field)


@router.get("/custom-fields", response_model=list[CustomFieldResponse])
async def list_custom_fields(
    entity_type: Optional[str] = Query(None, description="Filter by entity type: lead, deal, contact"),
    current_user: dict = Depends(get_current_user),
):
    """List all custom fields, optionally filtered by entity_type."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    fields = _mock_fields[tenant_id]
    if entity_type:
        if entity_type not in ALLOWED_ENTITY_TYPES:
            raise HTTPException(
                status_code=400,
                detail="entity_type يجب أن يكون lead أو deal أو contact",
            )
        fields = [f for f in fields if f["entity_type"] == entity_type]

    fields = sorted(fields, key=lambda f: f["sort_order"])
    return [CustomFieldResponse(**f) for f in fields]


@router.put("/custom-fields/{field_id}", response_model=CustomFieldResponse)
async def update_custom_field(
    field_id: str,
    data: CustomFieldUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update an existing custom field definition."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    for field in _mock_fields[tenant_id]:
        if field["id"] == field_id:
            updates = data.model_dump(exclude_none=True)
            # If changing to select type, require options
            new_type = updates.get("field_type", field["field_type"])
            new_options = updates.get("options", field["options"])
            if new_type == "select" and not new_options:
                raise HTTPException(
                    status_code=400,
                    detail="حقل القائمة المنسدلة يتطلب قائمة خيارات (options)",
                )
            for key, value in updates.items():
                field[key] = value
            field["updated_at"] = datetime.now(timezone.utc).isoformat()
            return CustomFieldResponse(**field)

    raise HTTPException(status_code=404, detail="الحقل المخصص غير موجود")


@router.delete("/custom-fields/{field_id}", status_code=204)
async def delete_custom_field(
    field_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a custom field and its associated values."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    for i, field in enumerate(_mock_fields[tenant_id]):
        if field["id"] == field_id:
            _mock_fields[tenant_id].pop(i)
            # Remove associated values
            _mock_values[tenant_id] = [
                v for v in _mock_values[tenant_id] if v["field_id"] != field_id
            ]
            return

    raise HTTPException(status_code=404, detail="الحقل المخصص غير موجود")


@router.put("/custom-fields/reorder", response_model=list[CustomFieldResponse])
async def reorder_custom_fields(
    data: ReorderRequest,
    current_user: dict = Depends(get_current_user),
):
    """Reorder custom fields by updating their sort_order values."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    field_map = {f["id"]: f for f in _mock_fields[tenant_id]}
    now = datetime.now(timezone.utc).isoformat()
    updated = []

    for item in data.fields:
        if item.field_id not in field_map:
            raise HTTPException(
                status_code=404,
                detail=f"الحقل المخصص غير موجود: {item.field_id}",
            )
        field_map[item.field_id]["sort_order"] = item.sort_order
        field_map[item.field_id]["updated_at"] = now
        updated.append(field_map[item.field_id])

    updated = sorted(updated, key=lambda f: f["sort_order"])
    return [CustomFieldResponse(**f) for f in updated]


@router.post(
    "/custom-fields/{field_id}/values",
    response_model=CustomFieldValueResponse,
    status_code=201,
)
async def set_custom_field_value(
    field_id: str,
    data: CustomFieldValueSet,
    current_user: dict = Depends(get_current_user),
):
    """Set or update a custom field value for a specific entity."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    # Find the field definition
    field = None
    for f in _mock_fields[tenant_id]:
        if f["id"] == field_id:
            field = f
            break
    if not field:
        raise HTTPException(status_code=404, detail="الحقل المخصص غير موجود")

    # Validate value against field_type
    _validate_field_value(field, data.value)

    now = datetime.now(timezone.utc).isoformat()

    # Update existing or create new
    for v in _mock_values[tenant_id]:
        if v["field_id"] == field_id and v["entity_id"] == data.entity_id:
            v["value"] = data.value
            v["updated_at"] = now
            return CustomFieldValueResponse(**v)

    value_record = {
        "field_id": field_id,
        "field_name": field["field_name"],
        "field_label": field["field_label"],
        "field_type": field["field_type"],
        "entity_id": data.entity_id,
        "value": data.value,
        "updated_at": now,
    }
    _mock_values[tenant_id].append(value_record)
    return CustomFieldValueResponse(**value_record)


@router.get(
    "/custom-fields/values/{entity_type}/{entity_id}",
    response_model=list[CustomFieldValueResponse],
)
async def get_custom_field_values(
    entity_type: str,
    entity_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get all custom field values for a specific entity."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    if entity_type not in ALLOWED_ENTITY_TYPES:
        raise HTTPException(
            status_code=400,
            detail="entity_type يجب أن يكون lead أو deal أو contact",
        )

    # Get field IDs that belong to this entity_type
    entity_field_ids = {
        f["id"] for f in _mock_fields[tenant_id] if f["entity_type"] == entity_type
    }

    values = [
        v
        for v in _mock_values[tenant_id]
        if v["entity_id"] == entity_id and v["field_id"] in entity_field_ids
    ]
    return [CustomFieldValueResponse(**v) for v in values]


# --------------- Helpers ---------------

def _validate_field_value(field: dict, value: Any):
    """Validate a value against its field type definition."""
    field_type = field["field_type"]

    if value is None:
        if field.get("is_required"):
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
        if value not in (field.get("options") or []):
            raise HTTPException(
                status_code=400,
                detail=f"القيمة يجب أن تكون أحد الخيارات: {', '.join(field.get('options', []))}",
            )
    elif field_type in ("text", "date", "url", "email", "phone"):
        if not isinstance(value, str):
            raise HTTPException(
                status_code=400, detail="القيمة يجب أن تكون نصاً"
            )
