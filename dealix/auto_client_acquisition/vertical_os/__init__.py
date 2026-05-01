"""
Vertical OS — each Saudi B2B sector becomes a mini-product.

Per vertical: ICP templates, signals catalog, objections, playbooks,
KPI dashboard fields, message library, proposal template, QBR template,
ROI model, compliance notes.

Public API:
    from auto_client_acquisition.vertical_os import (
        get_vertical, ALL_VERTICALS, VerticalOS,
    )
"""

from auto_client_acquisition.vertical_os.base import (
    ALL_VERTICALS,
    KPI,
    MessageTemplate,
    VerticalOS,
    get_vertical,
    list_vertical_summaries,
)
from auto_client_acquisition.vertical_os.clinics import CLINICS
from auto_client_acquisition.vertical_os.real_estate import REAL_ESTATE
from auto_client_acquisition.vertical_os.logistics import LOGISTICS

__all__ = [
    "VerticalOS",
    "KPI",
    "MessageTemplate",
    "ALL_VERTICALS",
    "get_vertical",
    "list_vertical_summaries",
    "CLINICS",
    "REAL_ESTATE",
    "LOGISTICS",
]
