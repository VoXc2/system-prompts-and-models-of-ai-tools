"""Shared phone number utilities for Saudi numbers."""
import re
from typing import Optional


def extract_saudi_phone(text: str) -> Optional[str]:
    """Extract a Saudi phone number from text."""
    patterns = [
        r'(?:\+966|00966|0)5\d{8}',
        r'05\d{8}',
        r'5\d{8}',
        r'(?:\+966|00966)\s?5\d[\s-]?\d{3}[\s-]?\d{4}',
        r'(?:\+966|00966)\s?1\d[\s-]?\d{3}[\s-]?\d{4}',  # Landlines
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return normalize_saudi_phone(match.group())
    return None


def normalize_saudi_phone(phone: str) -> str:
    """Normalize a Saudi phone to 966XXXXXXXXX format."""
    phone = re.sub(r'[\s\-\(\)\+]', '', phone)
    if phone.startswith('00'):
        phone = phone[2:]
    if phone.startswith('0'):
        phone = '966' + phone[1:]
    if phone.startswith('5') and len(phone) == 9:
        phone = '966' + phone
    return phone


def is_valid_saudi_mobile(phone: str) -> bool:
    """Validate Saudi mobile number (966 5X XXXX XXXX)."""
    normalized = normalize_saudi_phone(phone)
    return bool(re.match(r'^9665\d{8}$', normalized))


def is_valid_saudi_landline(phone: str) -> bool:
    """Validate Saudi landline (966 1X XXX XXXX)."""
    normalized = normalize_saudi_phone(phone)
    return bool(re.match(r'^9661\d{8}$', normalized))


def format_saudi_phone(phone: str, style: str = "international") -> str:
    """Format Saudi phone number for display."""
    normalized = normalize_saudi_phone(phone)
    if style == "international":
        return f"+{normalized[:3]} {normalized[3:5]} {normalized[5:8]} {normalized[8:]}"
    elif style == "local":
        return f"0{normalized[3:5]} {normalized[5:8]} {normalized[8:]}"
    return normalized
