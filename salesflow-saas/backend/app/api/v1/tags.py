"""Tags and segments API for leads, deals, and contacts."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Any
from uuid import uuid4
from app.api.v1.deps import get_current_user, get_db

router = APIRouter()


# --------------- Schemas ---------------

class TagCreate(BaseModel):
    name: str
    color: str = "#6366F1"
    entity_type: str  # lead | deal | contact


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    entity_type: Optional[str] = None


class TagResponse(BaseModel):
    id: str
    name: str
    color: str
    entity_type: str
    tenant_id: str
    created_at: str


class TagAssign(BaseModel):
    entity_id: str
    entity_type: str


class TagAssignResponse(BaseModel):
    tag_id: str
    entity_id: str
    entity_type: str
    assigned_at: str


class SegmentCreate(BaseModel):
    name: str
    filters: dict[str, Any]
    description: Optional[str] = None


class SegmentResponse(BaseModel):
    id: str
    name: str
    filters: dict[str, Any]
    description: Optional[str]
    tenant_id: str
    member_count: int
    created_at: str


class SegmentMember(BaseModel):
    entity_id: str
    entity_type: str
    name: str
    matched_at: str


# --------------- Mock Data ---------------

_mock_tags: dict[str, list[dict]] = {}
_mock_assignments: list[dict] = []
_mock_segments: dict[str, list[dict]] = {}

_SEED_TAGS = [
    {"name": "عميل VIP", "color": "#EAB308", "entity_type": "contact"},
    {"name": "صفقة ساخنة", "color": "#EF4444", "entity_type": "deal"},
    {"name": "ليد من معرض", "color": "#3B82F6", "entity_type": "lead"},
    {"name": "متابعة عاجلة", "color": "#F97316", "entity_type": "lead"},
]

_SEED_SEGMENTS = [
    {
        "name": "عملاء الرياض",
        "filters": {"city": "الرياض", "entity_type": "contact"},
        "description": "جميع العملاء في منطقة الرياض",
    },
    {
        "name": "صفقات فوق 50 ألف",
        "filters": {"deal_value_gte": 50000, "stage_not": "closed_lost"},
        "description": "صفقات مفتوحة بقيمة أكبر من 50,000 ريال",
    },
]

_SEED_MEMBERS = [
    {"entity_id": "lead-001", "entity_type": "lead", "name": "أحمد الغامدي"},
    {"entity_id": "lead-002", "entity_type": "lead", "name": "فاطمة العتيبي"},
    {"entity_id": "contact-003", "entity_type": "contact", "name": "خالد المطيري"},
]


def _ensure_seed(tenant_id: str):
    if tenant_id not in _mock_tags:
        now = datetime.now(timezone.utc).isoformat()
        _mock_tags[tenant_id] = [
            {
                "id": str(uuid4()),
                "tenant_id": tenant_id,
                "created_at": now,
                **t,
            }
            for t in _SEED_TAGS
        ]
    if tenant_id not in _mock_segments:
        now = datetime.now(timezone.utc).isoformat()
        _mock_segments[tenant_id] = [
            {
                "id": str(uuid4()),
                "tenant_id": tenant_id,
                "member_count": len(_SEED_MEMBERS),
                "created_at": now,
                **s,
            }
            for s in _SEED_SEGMENTS
        ]


# --------------- Tag Endpoints ---------------

@router.post("/tags", response_model=TagResponse, status_code=201)
async def create_tag(
    data: TagCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new tag."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    if data.entity_type not in ("lead", "deal", "contact"):
        raise HTTPException(status_code=400, detail="entity_type يجب أن يكون lead أو deal أو contact")

    tag = {
        "id": str(uuid4()),
        "name": data.name,
        "color": data.color,
        "entity_type": data.entity_type,
        "tenant_id": tenant_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _mock_tags[tenant_id].append(tag)
    return TagResponse(**tag)


@router.get("/tags", response_model=list[TagResponse])
async def list_tags(
    entity_type: Optional[str] = Query(None, description="Filter by entity type: lead, deal, contact"),
    current_user: dict = Depends(get_current_user),
):
    """List all tags, optionally filtered by entity_type."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    tags = _mock_tags[tenant_id]
    if entity_type:
        tags = [t for t in tags if t["entity_type"] == entity_type]
    return [TagResponse(**t) for t in tags]


@router.put("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: str,
    data: TagUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update an existing tag."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    for tag in _mock_tags[tenant_id]:
        if tag["id"] == tag_id:
            for field, value in data.model_dump(exclude_none=True).items():
                if field == "entity_type" and value not in ("lead", "deal", "contact"):
                    raise HTTPException(status_code=400, detail="entity_type يجب أن يكون lead أو deal أو contact")
                tag[field] = value
            return TagResponse(**tag)

    raise HTTPException(status_code=404, detail="التاق غير موجود")


@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a tag."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    for i, tag in enumerate(_mock_tags[tenant_id]):
        if tag["id"] == tag_id:
            _mock_tags[tenant_id].pop(i)
            return

    raise HTTPException(status_code=404, detail="التاق غير موجود")


@router.post("/tags/{tag_id}/assign", response_model=TagAssignResponse)
async def assign_tag(
    tag_id: str,
    data: TagAssign,
    current_user: dict = Depends(get_current_user),
):
    """Assign a tag to an entity (lead, deal, or contact)."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    tag_exists = any(t["id"] == tag_id for t in _mock_tags[tenant_id])
    if not tag_exists:
        raise HTTPException(status_code=404, detail="التاق غير موجود")

    if data.entity_type not in ("lead", "deal", "contact"):
        raise HTTPException(status_code=400, detail="entity_type يجب أن يكون lead أو deal أو contact")

    assignment = {
        "tag_id": tag_id,
        "entity_id": data.entity_id,
        "entity_type": data.entity_type,
        "assigned_at": datetime.now(timezone.utc).isoformat(),
    }
    _mock_assignments.append(assignment)
    return TagAssignResponse(**assignment)


# --------------- Segment Endpoints ---------------

@router.post("/segments", response_model=SegmentResponse, status_code=201)
async def create_segment(
    data: SegmentCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new segment with filter criteria."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    segment = {
        "id": str(uuid4()),
        "name": data.name,
        "filters": data.filters,
        "description": data.description,
        "tenant_id": tenant_id,
        "member_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _mock_segments[tenant_id].append(segment)
    return SegmentResponse(**segment)


@router.get("/segments", response_model=list[SegmentResponse])
async def list_segments(
    current_user: dict = Depends(get_current_user),
):
    """List all segments for the tenant."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)
    return [SegmentResponse(**s) for s in _mock_segments[tenant_id]]


@router.get("/segments/{segment_id}/members", response_model=list[SegmentMember])
async def get_segment_members(
    segment_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get members matching a segment's filters (mock data)."""
    tenant_id = current_user["tenant_id"]
    _ensure_seed(tenant_id)

    segment_exists = any(s["id"] == segment_id for s in _mock_segments[tenant_id])
    if not segment_exists:
        raise HTTPException(status_code=404, detail="الشريحة غير موجودة")

    now = datetime.now(timezone.utc).isoformat()
    return [
        SegmentMember(matched_at=now, **m)
        for m in _SEED_MEMBERS
    ]
