"""File/document management endpoints for Dealix CRM."""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
from typing import Optional

from app.api.v1.deps import get_current_user, get_db

router = APIRouter()

ALLOWED_CATEGORIES = {"document", "image", "contract", "proposal", "other"}
UPLOAD_DIR = Path("uploads")

# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

def _mock_file_record(
    file_id: str,
    tenant_id: str,
    filename: str,
    category: str,
    file_size: int = 102400,
    file_type: str = "application/pdf",
) -> dict:
    """Return a structured mock file metadata record."""
    return {
        "id": file_id,
        "tenant_id": tenant_id,
        "filename": filename,
        "category": category,
        "file_size": file_size,
        "file_type": file_type,
        "storage_path": str(UPLOAD_DIR / tenant_id / file_id / filename),
        "uploaded_by": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    category: str = Query("other", description="تصنيف الملف"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    رفع ملف جديد.

    Upload a new file to the tenant's storage area.
    The file is categorised as one of: document, image, contract, proposal, other.
    """
    if category not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"تصنيف غير صالح. القيم المسموحة: {', '.join(sorted(ALLOWED_CATEGORIES))}",
        )

    tenant_id = current_user["tenant_id"]
    file_id = str(uuid4())

    # In production the bytes would be persisted here:
    #   dest = UPLOAD_DIR / tenant_id / file_id
    #   dest.mkdir(parents=True, exist_ok=True)
    #   contents = await file.read()
    #   (dest / file.filename).write_bytes(contents)

    record = _mock_file_record(
        file_id=file_id,
        tenant_id=tenant_id,
        filename=file.filename,
        category=category,
        file_size=file.size or 0,
        file_type=file.content_type or "application/octet-stream",
    )
    record["uploaded_by"] = current_user["user_id"]

    return {"status": "success", "message": "تم رفع الملف بنجاح", "data": record}


@router.get("")
async def list_files(
    category: Optional[str] = Query(None, description="تصفية حسب التصنيف"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    عرض قائمة الملفات الخاصة بالمؤسسة.

    List all files belonging to the current tenant, with optional category filter.
    """
    if category and category not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"تصنيف غير صالح. القيم المسموحة: {', '.join(sorted(ALLOWED_CATEGORIES))}",
        )

    tenant_id = current_user["tenant_id"]

    # Mock data -- in production this would query the database.
    mock_files = [
        _mock_file_record(
            file_id=str(uuid4()),
            tenant_id=tenant_id,
            filename="عقد_بيع_2026.pdf",
            category="contract",
            file_size=204800,
            file_type="application/pdf",
        ),
        _mock_file_record(
            file_id=str(uuid4()),
            tenant_id=tenant_id,
            filename="عرض_أسعار.docx",
            category="proposal",
            file_size=51200,
            file_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
        _mock_file_record(
            file_id=str(uuid4()),
            tenant_id=tenant_id,
            filename="logo.png",
            category="image",
            file_size=32768,
            file_type="image/png",
        ),
    ]

    if category:
        mock_files = [f for f in mock_files if f["category"] == category]

    total = len(mock_files)
    start = (page - 1) * per_page
    paginated = mock_files[start : start + per_page]

    return {
        "status": "success",
        "data": {
            "items": paginated,
            "total": total,
            "page": page,
            "per_page": per_page,
        },
    }


@router.get("/{file_id}")
async def get_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    جلب بيانات ملف محدد.

    Retrieve metadata for a single file by its ID.
    """
    tenant_id = current_user["tenant_id"]

    # In production: query DB and verify tenant ownership.
    record = _mock_file_record(
        file_id=file_id,
        tenant_id=tenant_id,
        filename="عقد_بيع_2026.pdf",
        category="contract",
        file_size=204800,
        file_type="application/pdf",
    )

    return {"status": "success", "data": record}


@router.delete("/{file_id}", status_code=status.HTTP_200_OK)
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    حذف ملف.

    Delete a file record and its stored content.
    """
    tenant_id = current_user["tenant_id"]

    # In production:
    #   1. Query DB for the file, verify tenant ownership.
    #   2. Remove the physical file from storage.
    #   3. Delete the database record.

    return {
        "status": "success",
        "message": "تم حذف الملف بنجاح",
        "data": {"id": file_id, "tenant_id": tenant_id, "deleted": True},
    }


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    تحميل ملف.

    Download the stored file. Returns the file content as a streaming response.
    """
    tenant_id = current_user["tenant_id"]

    # In production:
    #   record = await db.execute(select(FileModel).where(...))
    #   file_path = Path(record.storage_path)
    #   if not file_path.exists():
    #       raise HTTPException(status_code=404, detail="الملف غير موجود على الخادم")
    #   return FileResponse(
    #       path=str(file_path),
    #       filename=record.filename,
    #       media_type=record.file_type,
    #   )

    # Placeholder: construct the expected path and return 404 since no
    # physical file exists in the mock environment.
    expected_path = UPLOAD_DIR / tenant_id / file_id / "عقد_بيع_2026.pdf"
    if not expected_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الملف غير موجود على الخادم. هذا مسار وهمي للتطوير.",
        )

    return FileResponse(
        path=str(expected_path),
        filename="عقد_بيع_2026.pdf",
        media_type="application/pdf",
    )
