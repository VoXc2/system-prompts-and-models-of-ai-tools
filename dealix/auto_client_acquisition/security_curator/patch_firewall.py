"""Patch Firewall — block unsafe diffs before they enter the repo."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .secret_redactor import detect_secret_patterns

# Files that should never be added to the repo via patch.
DANGEROUS_FILE_PATTERNS: tuple[str, ...] = (
    r"^\+\+\+ b/.*\.env$",
    r"^\+\+\+ b/.*\.env\.local$",
    r"^\+\+\+ b/.*\.env\.staging$",
    r"^\+\+\+ b/.*\.env\.production$",
    r"^\+\+\+ b/.*credentials\.json$",
    r"^\+\+\+ b/.*service[-_]account.*\.json$",
    r"^\+\+\+ b/.*id_rsa$",
    r"^\+\+\+ b/.*\.pem$",
    r"^\+\+\+ b/.*\.p12$",
    r"^\+\+\+ b/.*\.pfx$",
)


@dataclass(frozen=True)
class PatchFirewallResult:
    safe: bool
    reasons_ar: list[str] = field(default_factory=list)
    blocked_files: list[str] = field(default_factory=list)
    secret_findings: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "safe": self.safe,
            "reasons_ar": self.reasons_ar,
            "blocked_files": self.blocked_files,
            "secret_findings": self.secret_findings,
        }


def _added_lines(diff_text: str) -> str:
    """Concatenate only the *added* lines from a unified diff."""
    out: list[str] = []
    for line in diff_text.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            out.append(line[1:])
    return "\n".join(out)


def _blocked_files_in_diff(diff_text: str) -> list[str]:
    blocked: list[str] = []
    for line in diff_text.splitlines():
        for pat in DANGEROUS_FILE_PATTERNS:
            if re.match(pat, line):
                blocked.append(line.replace("+++ b/", ""))
                break
    return blocked


def inspect_diff(diff_text: str) -> PatchFirewallResult:
    """
    Inspect a unified-diff blob.

    Returns PatchFirewallResult.safe = False if:
      - The diff adds a file from DANGEROUS_FILE_PATTERNS, OR
      - Any added line contains a known secret pattern.
    """
    if not diff_text:
        return PatchFirewallResult(safe=True)

    reasons: list[str] = []
    blocked = _blocked_files_in_diff(diff_text)
    if blocked:
        reasons.append(f"الملفات المحظورة: {', '.join(blocked)}")

    added = _added_lines(diff_text)
    findings = detect_secret_patterns(added)
    finding_dicts = [
        {"label": f.label, "sample_redacted": f.sample_redacted}
        for f in findings
    ]
    if findings:
        labels = sorted({f.label for f in findings})
        reasons.append(f"تم اكتشاف أسرار محتملة: {', '.join(labels)}")

    safe = not reasons
    return PatchFirewallResult(
        safe=safe,
        reasons_ar=reasons,
        blocked_files=blocked,
        secret_findings=finding_dicts,
    )


def is_safe_diff(diff_text: str) -> bool:
    """Convenience boolean wrapper around inspect_diff()."""
    return inspect_diff(diff_text).safe
