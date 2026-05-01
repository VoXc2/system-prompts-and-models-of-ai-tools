"""
Compliance OS v2 — PDPL operating layer.

Goes beyond the existing 11-gate pre-send check to a full ledger system:
  - consent_ledger: every consent (or refusal) recorded with lawful basis
  - contactability: per-contact status (safe / risky / blocked)
  - retention_policy: per-data-class retention rules
  - data_subject_requests: DSR workflow + completion tracking
  - ropa: Records of Processing Activities exporter
  - risk_engine: per-campaign PDPL risk scoring
  - vendor_registry: subprocessor list (per Article-Y of PDPL)
  - audit_exports: SDAIA / DPO inspection bundles
"""

from auto_client_acquisition.compliance_os.consent_ledger import (
    ConsentRecord,
    LawfulBasis,
    record_consent,
    record_opt_out,
)
from auto_client_acquisition.compliance_os.contactability import (
    ContactabilityStatus,
    check_contactability,
)
from auto_client_acquisition.compliance_os.data_subject_requests import (
    DSRStatus,
    DataSubjectRequest,
    open_dsr,
    process_dsr,
)
from auto_client_acquisition.compliance_os.risk_engine import (
    CampaignRiskAssessment,
    score_campaign_risk,
)
from auto_client_acquisition.compliance_os.ropa import (
    ProcessingActivity,
    RoPAExporter,
    build_ropa,
)
from auto_client_acquisition.compliance_os.vendor_registry import (
    Vendor,
    VendorStatus,
    register_vendor,
    vendors_summary,
)

__all__ = [
    "ConsentRecord",
    "LawfulBasis",
    "record_consent",
    "record_opt_out",
    "ContactabilityStatus",
    "check_contactability",
    "DSRStatus",
    "DataSubjectRequest",
    "open_dsr",
    "process_dsr",
    "CampaignRiskAssessment",
    "score_campaign_risk",
    "ProcessingActivity",
    "RoPAExporter",
    "build_ropa",
    "Vendor",
    "VendorStatus",
    "register_vendor",
    "vendors_summary",
]
