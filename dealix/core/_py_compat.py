"""
Python compatibility shims — makes the codebase work on Python 3.10 + 3.11+.

Two stdlib features used heavily but only available on 3.11+:
  - `from datetime import UTC`     →  `core._py_compat.UTC`
  - `from enum import StrEnum`     →  `core._py_compat.StrEnum`

This module is import-safe everywhere (no third-party deps) and adds
zero runtime cost on 3.11+ (it just re-exports the stdlib names).
"""

from __future__ import annotations

import sys

# ── UTC ─────────────────────────────────────────────────────────
if sys.version_info >= (3, 11):
    from datetime import UTC  # type: ignore[attr-defined]
else:
    from datetime import timezone

    UTC = timezone.utc  # type: ignore[assignment]


# ── StrEnum ─────────────────────────────────────────────────────
if sys.version_info >= (3, 11):
    from enum import StrEnum  # type: ignore[attr-defined]
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """3.10-compatible StrEnum backport.

        Behaves like 3.11's enum.StrEnum: members are strings, str(member)
        returns the value (not 'ClassName.MEMBER').
        """

        def __new__(cls, value):
            if not isinstance(value, str):
                raise TypeError(f"values of StrEnum must be str, got {type(value)}")
            obj = str.__new__(cls, value)
            obj._value_ = value
            return obj

        def __str__(self):
            return str.__str__(self)


__all__ = ["UTC", "StrEnum"]
