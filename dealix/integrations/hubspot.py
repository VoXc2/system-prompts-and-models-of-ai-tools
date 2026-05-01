"""
HubSpot thin client wrapper — re-exports the CRMAgent in a convenience facade.
واجهة مبسطة لـ HubSpot.
"""

from __future__ import annotations

from auto_client_acquisition.agents.crm import CRMAgent, CRMSyncResult
from auto_client_acquisition.agents.intake import Lead

__all__ = ["CRMSyncResult", "HubSpotClient"]


class HubSpotClient:
    """Convenience wrapper over CRMAgent."""

    def __init__(self) -> None:
        self._agent = CRMAgent()

    async def sync_lead(self, lead: Lead, create_deal: bool = True) -> CRMSyncResult:
        return await self._agent.run(lead=lead, create_deal=create_deal)

    @property
    def configured(self) -> bool:
        return self._agent._configured
