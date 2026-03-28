"""Contract management and e-signature API - إدارة العقود والتوقيع الإلكتروني."""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.contract import Contract, Signature

router = APIRouter()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ContractType(str, Enum):
    msa = "msa"
    sow = "sow"
    nda = "nda"
    subscription = "subscription"


CONTRACT_TYPE_LABELS = {
    "msa": "اتفاقية خدمات رئيسية",
    "sow": "بيان نطاق العمل",
    "nda": "اتفاقية عدم إفشاء",
    "subscription": "عقد اشتراك",
}


class ContractStatus(str, Enum):
    draft = "draft"              # مسودة
    sent = "sent"                # مرسل للتوقيع
    signed = "signed"            # موقّع
    voided = "voided"            # ملغي


STATUS_LABELS = {
    "draft": "مسودة",
    "sent": "مرسل للتوقيع",
    "signed": "موقّع",
    "voided": "ملغي",
}


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ContractCreate(BaseModel):
    title: str
    contract_type: ContractType
    content: str
    client_name: str
    client_email: EmailStr


class ContractUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    client_name: Optional[str] = None
    client_email: Optional[EmailStr] = None


class SignatureRequest(BaseModel):
    signer_name: str
    signer_email: EmailStr
    signature_data: str  # base64-encoded signature image
    ip_address: str


class ContractResponse(BaseModel):
    id: str
    tenant_id: str
    title: str
    contract_type: Optional[str] = None
    contract_type_label: str = ""
    content: Optional[str] = None
    status: str
    status_label: str = ""
    public_url: Optional[str] = None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, obj: Contract) -> "ContractResponse":
        ct = obj.contract_type or ""
        st = obj.status or "draft"
        return cls(
            id=str(obj.id),
            tenant_id=str(obj.tenant_id),
            title=obj.title or "",
            contract_type=ct,
            contract_type_label=CONTRACT_TYPE_LABELS.get(ct, ct),
            content=obj.content,
            status=st,
            status_label=STATUS_LABELS.get(st, st),
            public_url=obj.public_url,
            created_at=obj.created_at.isoformat() if obj.created_at else "",
            updated_at=(obj.sent_at or obj.created_at or datetime.now(timezone.utc)).isoformat(),
        )


class SignatureResponse(BaseModel):
    id: str
    contract_id: str
    signer_name: str
    signer_email: Optional[str] = None
    signature_data: Optional[str] = None
    ip_address: Optional[str] = None
    signed_at: str
    label: str = "توقيع إلكتروني"

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, obj: Signature) -> "SignatureResponse":
        return cls(
            id=str(obj.id),
            contract_id=str(obj.contract_id),
            signer_name=obj.signer_name or "",
            signer_email=obj.signer_email,
            signature_data=obj.signature_data,
            ip_address=str(obj.ip_address) if obj.ip_address else None,
            signed_at=obj.signed_at.isoformat() if obj.signed_at else (obj.created_at.isoformat() if obj.created_at else ""),
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_contract_or_404(
    db: AsyncSession, contract_id: str, tenant_id: str
) -> Contract:
    result = await db.execute(
        select(Contract).where(
            Contract.id == UUID(contract_id),
            Contract.tenant_id == tenant_id,
        )
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="العقد غير موجود")
    return contract


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", status_code=201)
async def create_contract(
    data: ContractCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """إنشاء عقد جديد - Create a new contract."""
    tenant_id = current_user["tenant_id"]

    contract = Contract(
        tenant_id=tenant_id,
        title=data.title,
        contract_type=data.contract_type.value,
        content=data.content,
        status="draft",
        extra_data={"client_name": data.client_name, "client_email": data.client_email},
    )
    db.add(contract)
    await db.commit()
    await db.refresh(contract)

    return {
        "status": "created",
        "message": "تم إنشاء العقد بنجاح",
        "contract": ContractResponse.from_orm_model(contract),
    }


@router.get("")
async def list_contracts(
    status: Optional[ContractStatus] = Query(None, description="تصفية حسب الحالة"),
    contract_type: Optional[ContractType] = Query(None, description="تصفية حسب نوع العقد"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """عرض جميع العقود - List contracts for the current tenant."""
    tenant_id = current_user["tenant_id"]

    stmt = select(Contract).where(Contract.tenant_id == tenant_id)
    if status:
        stmt = stmt.where(Contract.status == status.value)
    if contract_type:
        stmt = stmt.where(Contract.contract_type == contract_type.value)

    result = await db.execute(stmt)
    contracts = result.scalars().all()

    return {
        "total": len(contracts),
        "label": "العقود",
        "contracts": [ContractResponse.from_orm_model(c) for c in contracts],
    }


@router.get("/{contract_id}")
async def get_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """عرض تفاصيل العقد - Get contract details."""
    tenant_id = current_user["tenant_id"]
    contract = await _get_contract_or_404(db, contract_id, tenant_id)
    return {"contract": ContractResponse.from_orm_model(contract)}


@router.put("/{contract_id}")
async def update_contract(
    contract_id: str,
    data: ContractUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """تعديل العقد - Update an existing contract."""
    tenant_id = current_user["tenant_id"]
    contract = await _get_contract_or_404(db, contract_id, tenant_id)

    updated_fields = data.model_dump(exclude_none=True)
    if not updated_fields:
        raise HTTPException(status_code=400, detail="لا توجد حقول للتحديث")

    # Map API fields to model fields
    if "title" in updated_fields:
        contract.title = updated_fields["title"]
    if "content" in updated_fields:
        contract.content = updated_fields["content"]
    # client_name / client_email are stored in extra_data
    extra = dict(contract.extra_data or {})
    if "client_name" in updated_fields:
        extra["client_name"] = updated_fields["client_name"]
    if "client_email" in updated_fields:
        extra["client_email"] = updated_fields["client_email"]
    contract.extra_data = extra

    await db.commit()
    await db.refresh(contract)

    return {
        "status": "updated",
        "message": "تم تحديث العقد بنجاح",
        "updated_fields": list(updated_fields.keys()),
        "contract": ContractResponse.from_orm_model(contract),
    }


@router.post("/{contract_id}/send")
async def send_contract_for_signing(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """إرسال العقد للتوقيع - Send contract for e-signature."""
    tenant_id = current_user["tenant_id"]
    contract = await _get_contract_or_404(db, contract_id, tenant_id)

    signing_token = uuid4().hex[:12]
    signing_url = f"https://sign.dealix.sa/c/{signing_token}"

    contract.status = "sent"
    contract.sent_at = datetime.now(timezone.utc)
    contract.public_url = signing_url

    await db.commit()
    await db.refresh(contract)

    return {
        "status": "sent",
        "message": "تم إرسال العقد للتوقيع بنجاح",
        "signing_url": signing_url,
        "contract": ContractResponse.from_orm_model(contract),
    }


@router.post("/{contract_id}/sign")
async def sign_contract(
    contract_id: str,
    data: SignatureRequest,
    db: AsyncSession = Depends(get_db),
):
    """تسجيل التوقيع - Record a signature on a contract."""
    # Look up contract (no tenant filter since this is a public signing endpoint)
    result = await db.execute(
        select(Contract).where(Contract.id == UUID(contract_id))
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="العقد غير موجود")

    now = datetime.now(timezone.utc)

    signature = Signature(
        tenant_id=contract.tenant_id,
        contract_id=contract.id,
        signer_name=data.signer_name,
        signer_email=data.signer_email,
        signature_data=data.signature_data,
        ip_address=data.ip_address,
        signed_at=now,
    )
    db.add(signature)

    contract.status = "signed"
    contract.signed_at = now

    await db.commit()
    await db.refresh(signature)

    return {
        "status": "signed",
        "message": "تم تسجيل التوقيع بنجاح",
        "signature": SignatureResponse.from_orm_model(signature),
        "contract_status": "signed",
        "contract_status_label": STATUS_LABELS["signed"],
    }


@router.get("/{contract_id}/signatures")
async def list_signatures(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """عرض التوقيعات على العقد - List all signatures on a contract."""
    tenant_id = current_user["tenant_id"]
    # Verify the contract belongs to this tenant
    await _get_contract_or_404(db, contract_id, tenant_id)

    result = await db.execute(
        select(Signature).where(Signature.contract_id == UUID(contract_id))
    )
    signatures = result.scalars().all()

    return {
        "contract_id": contract_id,
        "total": len(signatures),
        "label": "التوقيعات",
        "signatures": [SignatureResponse.from_orm_model(s) for s in signatures],
    }


@router.post("/{contract_id}/void")
async def void_contract(
    contract_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """إلغاء العقد - Void a contract so it can no longer be signed."""
    tenant_id = current_user["tenant_id"]
    contract = await _get_contract_or_404(db, contract_id, tenant_id)

    contract.status = "voided"
    await db.commit()
    await db.refresh(contract)

    return {
        "status": "voided",
        "message": "تم إلغاء العقد",
        "contract": ContractResponse.from_orm_model(contract),
    }
