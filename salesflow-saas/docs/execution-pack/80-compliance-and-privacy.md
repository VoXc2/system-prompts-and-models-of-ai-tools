# Compliance & Privacy

## PDPL (Saudi Personal Data Protection Law) Compliance

### Core Requirements
1. **Consent before collection** — Must have legal basis before processing personal data
2. **Purpose limitation** — Data used only for stated purpose
3. **Data minimization** — Collect only what's needed
4. **Right to access** — Individuals can request their data
5. **Right to deletion** — Individuals can request erasure
6. **Data breach notification** — Report breaches within 72 hours

### Product Capabilities for Compliance

| Capability | Implementation | Status |
|-----------|---------------|--------|
| Consent collection | `Consent` model + API | DONE |
| Consent tracking | consent_type, status, granted_at, revoked_at | DONE |
| Suppression list | `SuppressionEntry` model + pre-send check | DONE |
| Do-not-contact | channel-level suppression | DONE |
| Opt-out handling | Webhook + suppression auto-add | DONE |
| Audit trail | `AuditLog` model on all mutations | DONE |
| Data export | `/analytics/export` endpoint | DONE |
| Data deletion | Soft delete + retention policy | PARTIAL |

### Consent Model
```python
class Consent(TenantModel):
    lead_id = Column(UUID, FK("leads.id"), index=True)
    customer_id = Column(UUID, FK("customers.id"), index=True)
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    consent_type = Column(String(100))  # marketing_whatsapp, marketing_email, data_processing
    status = Column(String(50), index=True)  # granted, revoked
    granted_at = Column(DateTime)
    revoked_at = Column(DateTime)
    source = Column(String(100))  # form, verbal, import
    ip_address = Column(INET)
    legal_basis = Column(String(100))  # consent, legitimate_interest, contract
    privacy_notice_version = Column(String(50))
```

### Suppression Enforcement
```python
# Called before ANY outreach message
async def check_suppression(db, tenant_id, phone=None, email=None, channel="whatsapp"):
    query = select(SuppressionEntry).where(
        SuppressionEntry.tenant_id == tenant_id,
        SuppressionEntry.channel == channel,
    )
    if phone:
        query = query.where(SuppressionEntry.contact_phone == normalize_phone(phone))
    if email:
        query = query.where(SuppressionEntry.contact_email == email.lower())
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None
```

### Data Retention Rules
| Data Type | Retention | After Expiry |
|-----------|-----------|-------------|
| Active leads/deals | Indefinite while tenant active | — |
| Closed-lost deals | 2 years | Archive |
| Audit logs | 3 years | Archive to cold storage |
| AI traces | 1 year | Aggregate + delete raw |
| Webhook events | 90 days | Delete |
| Conversation messages | 2 years | Archive |
| Suppression entries | Indefinite | Never delete |

### Privacy Request Workflow (Future)
```
Request received (email/form)
  → Verify identity
    → Locate all data for contact
      → If access request: export and send
      → If deletion request:
        → Delete from leads, customers, messages
        → Keep in suppression list (to prevent re-contact)
        → Keep anonymized audit entries
        → Confirm deletion to requester
```
