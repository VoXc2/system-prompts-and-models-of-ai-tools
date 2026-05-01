"""Unit tests for the Security Curator."""

from __future__ import annotations

from auto_client_acquisition.security_curator import (
    detect_secret_patterns,
    inspect_diff,
    is_safe_diff,
    redact_secrets,
    redact_trace,
    sanitize_tool_output,
    sanitize_trace_event,
    scan_payload,
)


# ── Secret Redactor ──────────────────────────────────────────
def test_detects_github_pat():
    text = "my token is ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1234"
    findings = detect_secret_patterns(text)
    assert any(f.label == "github_pat" for f in findings)
    assert all("ghp_AAAA" not in f.sample_redacted for f in findings)  # never raw


def test_redacts_openai_key():
    text = "key=sk-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1234 done"
    out = redact_secrets(text)
    assert "sk-AAAA" not in out
    assert "sk-***" in out


def test_redacts_anthropic_key():
    text = "ANTHROPIC=sk-ant-aBcDeFgHiJkLmNoPqRsTuVwXyZ1234"
    out = redact_secrets(text)
    assert "sk-ant-aBcD" not in out


def test_scan_payload_dict_redacts_sensitive_keys():
    payload = {"api_key": "ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1234",
               "name": "ali"}
    result = scan_payload(payload)
    assert result["has_secrets"] is True
    assert result["redacted"]["api_key"] == "***"
    assert result["redacted"]["name"] == "ali"


def test_scan_payload_handles_nested():
    payload = {"outer": {"token": "EAA" + "x" * 40, "ok": "yes"}}
    result = scan_payload(payload)
    assert result["has_secrets"] is True
    assert result["redacted"]["outer"]["token"] == "***"


def test_scan_empty_returns_no_findings():
    out = scan_payload({})
    assert out["has_secrets"] is False
    assert out["findings"] == []


# ── Patch Firewall ───────────────────────────────────────────
def test_blocks_env_file_diff():
    diff = """diff --git a/.env b/.env
new file mode 100644
+++ b/.env
+API_KEY=ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1234
"""
    r = inspect_diff(diff)
    assert r.safe is False
    assert any(".env" in f for f in r.blocked_files)


def test_blocks_secret_in_added_line():
    diff = """+++ b/src/foo.py
+OPENAI_KEY = "sk-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1234"
"""
    r = inspect_diff(diff)
    assert r.safe is False
    assert r.secret_findings


def test_allows_safe_diff():
    diff = """+++ b/src/foo.py
+def hello():
+    return "world"
"""
    assert is_safe_diff(diff) is True


def test_empty_diff_is_safe():
    assert is_safe_diff("") is True


# ── Trace Redactor ───────────────────────────────────────────
def test_trace_masks_phone_and_email():
    payload = {"note": "call +966500000123 or email ali@example.com"}
    out = redact_trace(payload, mask_pii=True)
    assert out["had_pii"] is True
    masked = out["redacted"]["note"]
    assert "+966500000123" not in masked
    assert "ali@example.com" not in masked
    assert "@example.com" in masked  # domain preserved


def test_trace_redacts_secrets_and_pii_together():
    payload = {"token": "ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1234",
               "phone": "+966500000999"}
    out = redact_trace(payload)
    assert out["had_secrets"] is True
    assert out["redacted"]["token"] == "***"


# ── Tool Output Sanitizer ────────────────────────────────────
def test_sanitize_output_strips_secret():
    output = {"raw": "ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1234 inside"}
    out = sanitize_tool_output(output)
    assert out["safe"] is False
    assert "ghp_AAAA" not in str(out["redacted"])
    assert any("حساسة" in n for n in out["notes_ar"])


def test_sanitize_trace_event_keeps_safe_keys():
    event = {
        "event_type": "tool_call", "agent_name": "scout",
        "status": "ok", "latency_ms": 120,
        "payload": {"phone": "+966500000123"},
    }
    out = sanitize_trace_event(event)
    assert out["event_type"] == "tool_call"
    assert out["agent_name"] == "scout"
    assert out["latency_ms"] == 120
    # payload was sanitized
    assert "+966500000123" not in str(out["payload"])
