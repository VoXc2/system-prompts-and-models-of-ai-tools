"""Consent & suppression enforcement service."""
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.consent import Consent
from app.models.suppression import SuppressionEntry

logger = logging.getLogger(__name__)


class ConsentService:
    """Enforces consent and suppression rules before outreach."""

    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    async def is_contact_suppressed(
        self, phone: Optional[str] = None, email: Optional[str] = None, channel: str = "all"
    ) -> bool:
        """Check if a contact is on the suppression list."""
        conditions = [SuppressionEntry.tenant_id == self.tenant_id]

        contact_filters = []
        if phone:
            contact_filters.append(SuppressionEntry.contact_phone == phone)
        if email:
            contact_filters.append(SuppressionEntry.contact_email == email)

        if not contact_filters:
            return False

        conditions.append(or_(*contact_filters))
        conditions.append(
            SuppressionEntry.channel.in_([channel, "all"])
        )

        result = await self.db.execute(
            select(SuppressionEntry.id).where(*conditions).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def has_consent(
        self,
        consent_type: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> bool:
        """Check if contact has active consent for a specific type."""
        conditions = [
            Consent.tenant_id == self.tenant_id,
            Consent.consent_type == consent_type,
            Consent.status == "granted",
        ]

        contact_filters = []
        if phone:
            contact_filters.append(Consent.contact_phone == phone)
        if email:
            contact_filters.append(Consent.contact_email == email)

        if not contact_filters:
            return False

        conditions.append(or_(*contact_filters))

        result = await self.db.execute(
            select(Consent.id).where(*conditions).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def can_contact(
        self,
        channel: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> dict:
        """Check if we can contact someone on a given channel. Returns eligibility + reason."""
        # Check suppression first
        if await self.is_contact_suppressed(phone=phone, email=email, channel=channel):
            return {"allowed": False, "reason": "suppressed", "detail": "جهة الاتصال في قائمة الحظر"}

        # Map channel to consent type
        consent_map = {
            "whatsapp": "marketing_whatsapp",
            "email": "marketing_email",
            "sms": "marketing_sms",
        }
        consent_type = consent_map.get(channel)

        if consent_type and not await self.has_consent(consent_type, phone=phone, email=email):
            return {"allowed": False, "reason": "no_consent", "detail": f"لا يوجد موافقة على {channel}"}

        return {"allowed": True, "reason": "ok"}

    async def suppress_contact(
        self,
        channel: str,
        reason: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        suppressed_by: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> SuppressionEntry:
        """Add a contact to the suppression list."""
        entry = SuppressionEntry(
            tenant_id=self.tenant_id,
            contact_phone=phone,
            contact_email=email,
            channel=channel,
            reason=reason,
            source="admin" if suppressed_by else "system",
            suppressed_by=suppressed_by,
            suppressed_at=datetime.now(timezone.utc),
            notes=notes,
        )
        self.db.add(entry)
        logger.info("Suppressed contact phone=%s email=%s channel=%s reason=%s",
                    phone, email, channel, reason)
        return entry

    async def record_consent(
        self,
        consent_type: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        source: str = "api",
        legal_basis: str = "consent",
        ip_address: Optional[str] = None,
    ) -> Consent:
        """Record a new consent grant."""
        consent = Consent(
            tenant_id=self.tenant_id,
            contact_phone=phone,
            contact_email=email,
            consent_type=consent_type,
            status="granted",
            granted_at=datetime.now(timezone.utc),
            source=source,
            legal_basis=legal_basis,
            ip_address=ip_address,
        )
        self.db.add(consent)
        logger.info("Consent recorded: type=%s phone=%s source=%s", consent_type, phone, source)
        return consent

    async def revoke_consent(
        self, consent_type: str, phone: Optional[str] = None, email: Optional[str] = None
    ) -> int:
        """Revoke consent and auto-suppress."""
        conditions = [
            Consent.tenant_id == self.tenant_id,
            Consent.consent_type == consent_type,
            Consent.status == "granted",
        ]
        if phone:
            conditions.append(Consent.contact_phone == phone)
        if email:
            conditions.append(Consent.contact_email == email)

        result = await self.db.execute(select(Consent).where(*conditions))
        consents = result.scalars().all()

        now = datetime.now(timezone.utc)
        for c in consents:
            c.status = "revoked"
            c.revoked_at = now

        # Auto-suppress on the matching channel
        channel_map = {
            "marketing_whatsapp": "whatsapp",
            "marketing_email": "email",
            "marketing_sms": "sms",
        }
        channel = channel_map.get(consent_type, "all")
        await self.suppress_contact(
            channel=channel, reason="opt_out", phone=phone, email=email
        )

        logger.info("Consent revoked: type=%s phone=%s (%d records)", consent_type, phone, len(consents))
        return len(consents)
