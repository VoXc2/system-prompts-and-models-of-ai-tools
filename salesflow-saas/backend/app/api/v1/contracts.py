"""Contract management and e-signature API - إدارة العقود والتوقيع الإلكتروني."""
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr

from app.api.v1.deps import get_current_user, get_db

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_contract(
    contract_id: str,
    tenant_id: str,
    *,
    title: str = "عقد خدمات تقنية",
    contract_type: str = "msa",
    content: str = "محتوى العقد ...",
    client_name: str = "شركة النجاح",
    client_email: str = "client@alnajah.sa",
    status: str = "draft",
    signing_url: Optional[str] = None,
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": contract_id,
        "tenant_id": tenant_id,
        "title": title,
        "contract_type": contract_type,
        "contract_type_label": CONTRACT_TYPE_LABELS.get(contract_type, contract_type),
        "content": content,
        "client_name": client_name,
        "client_email": client_email,
        "status": status,
        "status_label": STATUS_LABELS.get(status, status),
        "signing_url": signing_url,
        "created_at": now,
        "updated_at": now,
    }


def _mock_signature(
    signature_id: str,
    contract_id: str,
    *,
    signer_name: str = "أحمد الخالدي",
    signer_email: str = "ahmed@alnajah.sa",
    ip_address: str = "203.0.113.42",
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": signature_id,
        "contract_id": contract_id,
        "signer_name": signer_name,
        "signer_email": signer_email,
        "signature_data": "data:image/png;base64,iVBOR...truncated",
        "ip_address": ip_address,
        "signed_at": now,
        "label": "توقيع إلكتروني",
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", status_code=201)
async def create_contract(
    data: ContractCreate,
    current_user: dict = Depends(get_current_user),
):
    """إنشاء عقد جديد - Create a new contract."""
    contract_id = str(uuid4())
    tenant_id = current_user.get("tenant_id", "tenant-mock-001")

    return {
        "status": "created",
        "message": "تم إنشاء العقد بنجاح",
        "contract": _mock_contract(
            contract_id,
            tenant_id,
            title=data.title,
            contract_type=data.contract_type.value,
            content=data.content,
            client_name=data.client_name,
            client_email=data.client_email,
            status="draft",
        ),
    }


@router.get("")
async def list_contracts(
    status: Optional[ContractStatus] = Query(None, description="تصفية حسب الحالة"),
    contract_type: Optional[ContractType] = Query(None, description="تصفية حسب نوع العقد"),
    current_user: dict = Depends(get_current_user),
):
    """عرض جميع العقود - List contracts for the current tenant."""
    tenant_id = current_user.get("tenant_id", "tenant-mock-001")

    contracts = [
        _mock_contract(
            "c-00a1b2c3-1111-4444-aaaa-000000000001",
            tenant_id,
            title="عقد خدمات تقنية",
            contract_type="msa",
            client_name="شركة النجاح",
            client_email="info@alnajah.sa",
            status="draft",
        ),
        _mock_contract(
            "c-00a1b2c3-2222-4444-aaaa-000000000002",
            tenant_id,
            title="اتفاقية عدم إفشاء - مشروع ألفا",
            contract_type="nda",
            client_name="مؤسسة التقدم",
            client_email="legal@taqaddum.sa",
            status="sent",
            signing_url="https://sign.dealix.sa/c/abc123",
        ),
        _mock_contract(
            "c-00a1b2c3-3333-4444-aaaa-000000000003",
            tenant_id,
            title="عقد اشتراك سنوي",
            contract_type="subscription",
            client_name="شركة الأمل",
            client_email="accounts@alamal.sa",
            status="signed",
        ),
    ]

    if status:
        contracts = [c for c in contracts if c["status"] == status.value]
    if contract_type:
        contracts = [c for c in contracts if c["contract_type"] == contract_type.value]

    return {
        "total": len(contracts),
        "label": "العقود",
        "contracts": contracts,
    }


@router.get("/{contract_id}")
async def get_contract(
    contract_id: str,
    current_user: dict = Depends(get_current_user),
):
    """عرض تفاصيل العقد - Get contract details."""
    tenant_id = current_user.get("tenant_id", "tenant-mock-001")

    return {
        "contract": _mock_contract(
            contract_id,
            tenant_id,
            title="عقد خدمات تقنية",
            contract_type="msa",
            client_name="شركة النجاح",
            client_email="info@alnajah.sa",
            status="draft",
        ),
    }


@router.put("/{contract_id}")
async def update_contract(
    contract_id: str,
    data: ContractUpdate,
    current_user: dict = Depends(get_current_user),
):
    """تعديل العقد - Update an existing contract."""
    tenant_id = current_user.get("tenant_id", "tenant-mock-001")

    updated_fields = data.model_dump(exclude_none=True)
    if not updated_fields:
        raise HTTPException(status_code=400, detail="لا توجد حقول للتحديث")

    base = _mock_contract(
        contract_id,
        tenant_id,
        title=data.title or "عقد خدمات تقنية",
        content=data.content or "محتوى العقد ...",
        client_name=data.client_name or "شركة النجاح",
        client_email=data.client_email or "info@alnajah.sa",
        status="draft",
    )

    return {
        "status": "updated",
        "message": "تم تحديث العقد بنجاح",
        "updated_fields": list(updated_fields.keys()),
        "contract": base,
    }


@router.post("/{contract_id}/send")
async def send_contract_for_signing(
    contract_id: str,
    current_user: dict = Depends(get_current_user),
):
    """إرسال العقد للتوقيع - Send contract for e-signature (generates a public signing URL)."""
    tenant_id = current_user.get("tenant_id", "tenant-mock-001")
    signing_token = uuid4().hex[:12]
    signing_url = f"https://sign.dealix.sa/c/{signing_token}"

    return {
        "status": "sent",
        "message": "تم إرسال العقد للتوقيع بنجاح",
        "signing_url": signing_url,
        "contract": _mock_contract(
            contract_id,
            tenant_id,
            status="sent",
            signing_url=signing_url,
        ),
    }


@router.post("/{contract_id}/sign")
async def sign_contract(
    contract_id: str,
    data: SignatureRequest,
):
    """تسجيل التوقيع - Record a signature on a contract."""
    signature_id = str(uuid4())

    return {
        "status": "signed",
        "message": "تم تسجيل التوقيع بنجاح",
        "signature": _mock_signature(
            signature_id,
            contract_id,
            signer_name=data.signer_name,
            signer_email=data.signer_email,
            ip_address=data.ip_address,
        ),
        "contract_status": "signed",
        "contract_status_label": STATUS_LABELS["signed"],
    }


@router.get("/{contract_id}/signatures")
async def list_signatures(
    contract_id: str,
    current_user: dict = Depends(get_current_user),
):
    """عرض التوقيعات على العقد - List all signatures on a contract."""
    signatures = [
        _mock_signature(
            "sig-0001",
            contract_id,
            signer_name="أحمد الخالدي",
            signer_email="ahmed@alnajah.sa",
            ip_address="203.0.113.42",
        ),
        _mock_signature(
            "sig-0002",
            contract_id,
            signer_name="سارة المنصور",
            signer_email="sara@dealix.sa",
            ip_address="198.51.100.7",
        ),
    ]

    return {
        "contract_id": contract_id,
        "total": len(signatures),
        "label": "التوقيعات",
        "signatures": signatures,
    }


@router.post("/{contract_id}/void")
async def void_contract(
    contract_id: str,
    current_user: dict = Depends(get_current_user),
):
    """إلغاء العقد - Void a contract so it can no longer be signed."""
    tenant_id = current_user.get("tenant_id", "tenant-mock-001")

    return {
        "status": "voided",
        "message": "تم إلغاء العقد",
        "contract": _mock_contract(
            contract_id,
            tenant_id,
            status="voided",
        ),
    }
