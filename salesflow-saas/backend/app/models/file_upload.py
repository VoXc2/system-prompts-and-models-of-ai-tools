"""File uploads and asset library."""
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import TenantModel


class FileUpload(TenantModel):
    """Uploaded file / asset."""
    __tablename__ = "file_uploads"

    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    entity_type = Column(String(50))  # lead, deal, proposal, contract, property, message
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    file_name = Column(String(500), nullable=False)
    file_type = Column(String(100))  # image/png, application/pdf, etc.
    file_size = Column(Integer)  # bytes
    storage_path = Column(Text, nullable=False)
    public_url = Column(Text)
    category = Column(String(100))  # document, image, proposal, contract, logo, branding
    description = Column(Text)
    extra_data = Column("metadata", JSONB, default=dict)
