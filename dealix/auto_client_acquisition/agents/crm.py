"""
CRM Agent — syncs leads to HubSpot (contact + deal creation).
وكيل CRM — يُزامن العملاء مع HubSpot.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from auto_client_acquisition.agents.icp_matcher import FitScore
from auto_client_acquisition.agents.intake import Lead, LeadStatus
from core.agents.base import BaseAgent
from core.config.settings import get_settings
from core.errors import IntegrationError


@dataclass
class CRMSyncResult:
    synced: bool
    contact_id: str | None = None
    deal_id: str | None = None
    provider: str = "hubspot"
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "synced": self.synced,
            "contact_id": self.contact_id,
            "deal_id": self.deal_id,
            "provider": self.provider,
            "reason": self.reason,
        }


# Map internal status → HubSpot deal stage (customize per portal)
STATUS_TO_STAGE: dict[LeadStatus, str] = {
    LeadStatus.NEW: "appointmentscheduled",
    LeadStatus.QUALIFIED: "qualifiedtobuy",
    LeadStatus.DISCOVERY: "presentationscheduled",
    LeadStatus.PROPOSAL: "decisionmakerboughtin",
    LeadStatus.NEGOTIATION: "contractsent",
    LeadStatus.WON: "closedwon",
    LeadStatus.LOST: "closedlost",
    LeadStatus.DISQUALIFIED: "closedlost",
}


class CRMAgent(BaseAgent):
    """Creates/updates contacts and deals in HubSpot."""

    name = "crm"
    HUBSPOT_BASE_URL = "https://api.hubapi.com"

    def __init__(self) -> None:
        super().__init__()
        self.settings = get_settings()

    @property
    def _configured(self) -> bool:
        return self.settings.hubspot_access_token is not None

    def _headers(self) -> dict[str, str]:
        if not self.settings.hubspot_access_token:
            raise IntegrationError("HUBSPOT_ACCESS_TOKEN not configured")
        token = self.settings.hubspot_access_token.get_secret_value()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def run(
        self,
        *,
        lead: Lead,
        fit_score: FitScore | None = None,
        create_deal: bool = True,
        **_: Any,
    ) -> CRMSyncResult:
        """Sync a lead to HubSpot: upsert contact, optionally create deal."""
        if not self._configured:
            self.log.warning("crm_not_configured")
            return CRMSyncResult(synced=False, reason="HubSpot not configured — skipped")

        try:
            contact_id = await self._upsert_contact(lead, fit_score)
            deal_id: str | None = None
            if create_deal and lead.company_name:
                deal_id = await self._create_deal(lead, contact_id, fit_score)

            self.log.info("crm_sync_ok", lead_id=lead.id, contact_id=contact_id, deal_id=deal_id)
            return CRMSyncResult(synced=True, contact_id=contact_id, deal_id=deal_id)
        except Exception as e:
            self.log.exception("crm_sync_failed", error=str(e))
            return CRMSyncResult(synced=False, reason=str(e))

    # ── Contact upsert ──────────────────────────────────────────
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def _upsert_contact(self, lead: Lead, fit: FitScore | None) -> str:
        """Create or update contact by email, return contact_id."""
        properties: dict[str, Any] = {
            "email": lead.contact_email or f"noemail+{lead.id}@ai-company.sa",
            "firstname": (lead.contact_name or "").split(" ")[0] if lead.contact_name else "",
            "lastname": " ".join((lead.contact_name or "").split(" ")[1:]),
            "phone": lead.contact_phone or "",
            "company": lead.company_name,
            "lifecyclestage": "lead",
            "hs_lead_status": "NEW" if lead.status == LeadStatus.NEW else "OPEN",
        }
        if lead.sector:
            properties["industry"] = lead.sector
        if fit:
            properties["hs_analytics_source_data_1"] = f"fit_tier_{fit.tier}"

        payload = {"properties": properties}

        async with httpx.AsyncClient(timeout=30) as client:
            # Try create first
            response = await client.post(
                f"{self.HUBSPOT_BASE_URL}/crm/v3/objects/contacts",
                json=payload,
                headers=self._headers(),
            )
            if response.status_code == 409:
                # Already exists — search by email
                search_url = f"{self.HUBSPOT_BASE_URL}/crm/v3/objects/contacts/search"
                search_resp = await client.post(
                    search_url,
                    json={
                        "filterGroups": [
                            {
                                "filters": [
                                    {
                                        "propertyName": "email",
                                        "operator": "EQ",
                                        "value": properties["email"],
                                    }
                                ]
                            }
                        ],
                        "limit": 1,
                    },
                    headers=self._headers(),
                )
                search_resp.raise_for_status()
                results = search_resp.json().get("results", [])
                if not results:
                    raise IntegrationError("Contact exists but cannot be found")
                contact_id = str(results[0]["id"])
                # Update
                update_resp = await client.patch(
                    f"{self.HUBSPOT_BASE_URL}/crm/v3/objects/contacts/{contact_id}",
                    json=payload,
                    headers=self._headers(),
                )
                update_resp.raise_for_status()
                return contact_id

            response.raise_for_status()
            return str(response.json()["id"])

    # ── Deal creation ───────────────────────────────────────────
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def _create_deal(self, lead: Lead, contact_id: str, fit: FitScore | None) -> str:
        """Create a deal and associate with contact."""
        stage = STATUS_TO_STAGE.get(lead.status, "appointmentscheduled")
        deal_name = f"{lead.company_name} — {lead.sector or 'Discovery'}"
        amount = lead.budget or 0.0

        payload = {
            "properties": {
                "dealname": deal_name,
                "dealstage": stage,
                "amount": str(amount),
                "pipeline": "default",
            }
        }
        if fit:
            payload["properties"]["description"] = (
                f"Fit tier {fit.tier} (score {fit.overall_score:.2f}). "
                + "; ".join(fit.reasons[:3])
            )

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.HUBSPOT_BASE_URL}/crm/v3/objects/deals",
                json=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
            deal_id = str(response.json()["id"])

            # Associate deal with contact
            await client.put(
                f"{self.HUBSPOT_BASE_URL}/crm/v4/objects/deals/{deal_id}/associations/"
                f"default/contacts/{contact_id}",
                headers=self._headers(),
            )
            return deal_id
