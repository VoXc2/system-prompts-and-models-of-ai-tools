"""Connector Catalog — every external integration with launch phase + risk level.

Higher-level than channel_registry: this catalogues every *integration* Dealix
can offer, including read-only and beta-status connectors, with launch phase.
"""

from __future__ import annotations

from .catalog import (
    ALL_CONNECTORS,
    Connector,
    catalog_summary,
    get_connector,
    list_connectors,
)
from .risks import all_risks, connector_risks
from .status import connector_status

__all__ = [
    "ALL_CONNECTORS",
    "Connector",
    "all_risks",
    "catalog_summary",
    "connector_risks",
    "connector_status",
    "get_connector",
    "list_connectors",
]
