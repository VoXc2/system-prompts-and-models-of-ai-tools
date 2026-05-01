"""Security curator — redaction and diff inspection before agents touch repos."""

from auto_client_acquisition.security_curator.patch_firewall import inspect_diff
from auto_client_acquisition.security_curator.secret_redactor import redact_secrets, scan_payload
from auto_client_acquisition.security_curator.trace_redactor import redact_span_metadata, redact_trace_payload

__all__ = [
    "inspect_diff",
    "redact_secrets",
    "redact_span_metadata",
    "redact_trace_payload",
    "scan_payload",
]
