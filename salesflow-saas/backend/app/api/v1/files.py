"""File/document management endpoints for Dealix CRM."""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
from typing import Optional

from app.api.v1.deps import get_current_user, get_db
from app.models.file_upload import FileUpload

router = APIRouter()

ALLOWED_CATEGORIES = {"document", "image", "contract", "proposal", "other"}
UPLOAD_DIR = Path("uploads")


def _serialize(f: FileUpload) -> dict:
    return {
        "id": str(f.id),
        "tenant_id": str(f.tenant_id),
        "filename": f.file_name,
        "category": f.category or "other",
        "file_size": f.file_size or 0,
        "file_type": f.file_type or "application/octet-stream",
        "storage_path": f.storage_path,
        "public_url": f.public_url,
        "description": f.description,
        "uploaded_by": str(f.uploaded_by) if f.uploaded_by else None,
        "created_at": f.created_at.isoformat() if f.created_at else None,
        "updated_at": f.updated_at.isoformat() if f.updated_at else None,
    }


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    category: str = Query("other", description="تصنيف الملف"),
    description: Optional[str] = Query(None, description="وصف الملف"),
    entity_type: Optional[str] = Query(None, description="نوع الكيان المرتبط"),
    entity_id: Optional[str] = Query(None, description="معرف الكيان المرتبط"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """رفع ملف جديد."""
    if category not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"تصنيف غير صالح. القيم المسموحة: {', '.join(sorted(ALLOWED_CATEGORIES))}",
        )

    tenant_id = current_user["tenant_id"]
    file_id = str(uuid4())

    # Save file to disk
    dest = UPLOAD_DIR / tenant_id / file_id
    dest.mkdir(parents=True, exist_ok=True)
    contents = await file.read()
    file_path = dest / file.filename
    file_path.write_bytes(contents)

    record = FileUpload(
        id=file_id,
        tenant_id=tenant_id,
        uploaded_by=current_user["user_id"],
        file_name=file.filename,
        file_type=file.content_type or "application/octet-stream",
        file_size=len(contents),
        storage_path=str(file_path),
        category=category,
        description=description,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {"status": "success", "message": "تم رفع الملف بنجاح", "data": _serialize(record)}


@router.get("")
async def list_files(
    category: Optional[str] = Query(None, description="تصفية حسب التصنيف"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """عرض قائمة الملفات الخاصة بالمؤسسة."""
    if category and category not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"تصنيف غير صالح. القيم المسموحة: {', '.join(sorted(ALLOWED_CATEGORIES))}",
        )

    tenant_id = current_user["tenant_id"]
    query = select(FileUpload).where(FileUpload.tenant_id == tenant_id)
    if category:
        query = query.where(FileUpload.category == category)

    total_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_q)).scalar() or 0

    offset = (page - 1) * per_page
    query = query.order_by(FileUpload.created_at.desc()).offset(offset).limit(per_page)
    result = await db.execute(query)
    files = result.scalars().all()

    return {
        "status": "success",
        "data": {
            "items": [_serialize(f) for f in files],
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
    """جلب بيانات ملف محدد."""
    tenant_id = current_user["tenant_id"]
    result = await db.execute(
        select(FileUpload).where(FileUpload.id == file_id, FileUpload.tenant_id == tenant_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="الملف غير موجود")
    return {"status": "success", "data": _serialize(record)}


@router.delete("/{file_id}", status_code=status.HTTP_200_OK)
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """حذف ملف."""
    tenant_id = current_user["tenant_id"]
    result = await db.execute(
        select(FileUpload).where(FileUpload.id == file_id, FileUpload.tenant_id == tenant_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="الملف غير موجود")

    # Remove physical file
    file_path = Path(record.storage_path)
    if file_path.exists():
        file_path.unlink()
        parent = file_path.parent
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()

    await db.delete(record)
    await db.commit()

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
    """تحميل ملف."""
    tenant_id = current_user["tenant_id"]
    result = await db.execute(
        select(FileUpload).where(FileUpload.id == file_id, FileUpload.tenant_id == tenant_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="الملف غير موجود")

    file_path = Path(record.storage_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="الملف غير موجود على الخادم")

    return FileResponse(
        path=str(file_path),
        filename=record.file_name,
        media_type=record.file_type or "application/octet-stream",
    )
