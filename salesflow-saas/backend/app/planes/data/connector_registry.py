"""
Connector Registry — Versioned facades for all external integrations.

Every connector is versioned with retry/idempotency/audit mapping.
Facade pattern prevents vendor chaos.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class ConnectorStatus(str, enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    ERROR = "error"
    UNKNOWN = "unknown"
    DISABLED = "disabled"


class ConnectorType(str, enum.Enum):
    CRM = "crm"
    COMMUNICATION = "communication"
    PAYMENT = "payment"
    DOCUMENT = "document"
    DATA_WAREHOUSE = "data_warehouse"
    IDENTITY = "identity"
    AI_PROVIDER = "ai_provider"
    STORAGE = "storage"
    COMPLIANCE = "compliance"


class ConnectorDefinition(BaseModel):
    connector_id: str
    name: str
    name_ar: str
    connector_type: ConnectorType
    version: str
    status: ConnectorStatus = ConnectorStatus.UNKNOWN
    health_check_url: Optional[str] = None
    retry_config: dict[str, Any] = Field(default_factory=lambda: {
        "max_retries": 3,
        "backoff_seconds": [1, 2, 4],
        "idempotency_key_header": "X-Idempotency-Key",
    })
    last_health_check: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None
    error_count_24h: int = 0
    audit_enabled: bool = True


CONNECTOR_REGISTRY: list[ConnectorDefinition] = [
    ConnectorDefinition(
        connector_id="whatsapp-business",
        name="WhatsApp Business API",
        name_ar="واجهة واتساب للأعمال",
        connector_type=ConnectorType.COMMUNICATION,
        version="2.0.0",
    ),
    ConnectorDefinition(
        connector_id="email-smtp",
        name="Email SMTP Gateway",
        name_ar="بوابة البريد الإلكتروني",
        connector_type=ConnectorType.COMMUNICATION,
        version="1.0.0",
    ),
    ConnectorDefinition(
        connector_id="stripe-payments",
        name="Stripe Payment Processing",
        name_ar="معالجة مدفوعات Stripe",
        connector_type=ConnectorType.PAYMENT,
        version="3.0.0",
    ),
    ConnectorDefinition(
        connector_id="groq-llm",
        name="Groq LLM Provider",
        name_ar="مزود نماذج لغوية Groq",
        connector_type=ConnectorType.AI_PROVIDER,
        version="1.0.0",
    ),
    ConnectorDefinition(
        connector_id="openai-llm",
        name="OpenAI LLM Provider",
        name_ar="مزود نماذج لغوية OpenAI",
        connector_type=ConnectorType.AI_PROVIDER,
        version="1.0.0",
    ),
    ConnectorDefinition(
        connector_id="postgres-primary",
        name="PostgreSQL Primary",
        name_ar="قاعدة البيانات الرئيسية",
        connector_type=ConnectorType.DATA_WAREHOUSE,
        version="16.0",
    ),
    ConnectorDefinition(
        connector_id="redis-cache",
        name="Redis Cache & Broker",
        name_ar="ذاكرة التخزين المؤقت Redis",
        connector_type=ConnectorType.STORAGE,
        version="7.0",
    ),
    ConnectorDefinition(
        connector_id="unstructured-io",
        name="Unstructured Document Extraction",
        name_ar="استخراج المستندات غير المهيكلة",
        connector_type=ConnectorType.DOCUMENT,
        version="1.0.0",
    ),
]
