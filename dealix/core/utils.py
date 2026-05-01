"""Utility helpers | دوال مساعدة."""

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import UTC, datetime
from typing import Any

import phonenumbers


def generate_id(prefix: str = "id") -> str:
    """Generate a short unique id | وَلِّد معرفاً فريداً قصيراً."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def utcnow() -> datetime:
    """Current UTC time | الوقت الحالي UTC."""
    return datetime.now(UTC)


def hash_text(text: str) -> str:
    """Stable hash for dedup | بصمة نصية للتكرار."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def is_arabic(text: str) -> bool:
    """Detect if text is primarily Arabic | اكتشف إذا كان النص عربياً."""
    if not text:
        return False
    arabic_range = re.compile(r"[\u0600-\u06FF\u0750-\u077F]")
    arabic_chars = len(arabic_range.findall(text))
    total_chars = len([c for c in text if c.isalpha()])
    return total_chars > 0 and arabic_chars / total_chars > 0.3


def detect_locale(text: str) -> str:
    """Return 'ar' or 'en' based on script | لغة النص."""
    return "ar" if is_arabic(text) else "en"


def normalize_phone(phone: str, default_country: str = "SA") -> str | None:
    """
    Normalize phone to E.164 (e.g. +966501234567).
    وحّد رقم الهاتف بصيغة E.164.
    """
    if not phone:
        return None
    try:
        parsed = phonenumbers.parse(phone, default_country)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return None
    return None


def normalize_email(email: str) -> str | None:
    """Lowercase + strip, basic validity check."""
    if not email:
        return None
    email = email.strip().lower()
    if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return email
    return None


def safe_dict(obj: Any) -> dict[str, Any]:
    """Best-effort convert object to a JSON-safe dict."""
    if isinstance(obj, dict):
        return {k: _safe_value(v) for k, v in obj.items()}
    if hasattr(obj, "__dict__"):
        return {k: _safe_value(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    return {"value": str(obj)}


def _safe_value(v: Any) -> Any:
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, (list, tuple)):
        return [_safe_value(i) for i in v]
    if isinstance(v, dict):
        return {k: _safe_value(x) for k, x in v.items()}
    return str(v)


def truncate(text: str, max_length: int = 200, suffix: str = "…") -> str:
    """Truncate text politely | اختصار نصي."""
    if not text or len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
