# Capture Layer Architecture

## Purpose
Make Dealix easy to install, easy to sell, and fast to show value. Capture every revenue opportunity from every channel with minimal integration friction.

## Capture Channels

| Channel | Method | Priority |
|---------|--------|----------|
| Website forms | Embeddable widget / hosted page | P0 |
| WhatsApp | Business API webhook | P0 |
| API submit | Direct REST endpoint | P0 |
| CSV import | File upload + mapping | P0 |
| Webhook ingestion | Inbound webhook from other tools | P1 |
| Social listening | AI-detected opportunities | P1 |
| Booking widget | Embedded scheduling | P1 |
| Phone/Voice | Call log + transcript | P2 |
| Email | Forwarded email parsing | P2 |

## Capture Flow

```
Source (widget/API/webhook/import)
  → Public endpoint (no auth required)
    → Validate payload
      → UTM/source attribution
        → Dedupe check (phone/email)
          → If duplicate: merge data, update existing
          → If new: create lead
            → Score (AI if enabled)
              → Route (assignment rules)
                → Notify assigned agent
                  → Start SLA timer
                    → Enroll in sequence (if auto-sequence configured)
```

## Public Capture Endpoint

```
POST /api/v1/forms/submit

Headers:
  X-Dealix-Form-ID: {form_id}   # Identifies the form config
  X-Dealix-Tenant: {tenant_slug}  # Identifies the tenant

Body:
{
  "name": "أحمد محمد",
  "phone": "+966501234567",
  "email": "ahmed@company.sa",
  "source": "website",
  "form_type": "lead_capture",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "clinics_q1",
  "utm_content": "ad_v2",
  "utm_term": "dental clinic software",
  "page_url": "https://client.com/services",
  "referrer_url": "https://google.com",
  "custom_fields": {
    "company_size": "10-50",
    "industry": "healthcare",
    "interest": "pipeline_management"
  }
}

Response: 201
{
  "success": true,
  "lead_id": "uuid",
  "message": "شكراً لتواصلك"
}
```

## UTM/Source Attribution Schema

```python
class GrowthEvent(TenantModel):
    lead_id = Column(UUID, FK("leads.id"), index=True)
    event_type = Column(String(100), index=True)  # form_submit, page_view, meeting_booked
    source = Column(String(100), index=True)       # google, facebook, linkedin, direct
    medium = Column(String(100))                    # cpc, organic, social, email, referral
    campaign = Column(String(255))
    utm_source = Column(String(255))
    utm_medium = Column(String(255))
    utm_campaign = Column(String(255))
    utm_content = Column(String(255))
    utm_term = Column(String(255))
    page_url = Column(Text)
    referrer_url = Column(Text)
    landing_page = Column(Text)
    ip_address = Column(INET)
    device_type = Column(String(50))
    revenue_attributed = Column(Numeric(12, 2), default=0)
```

## Dedupe Strategy

### Matching Rules
1. **Phone match**: Normalize phone (remove spaces, +966 prefix) → exact match
2. **Email match**: Lowercase + trim → exact match
3. **Fuzzy name + company**: Only if phone AND email are missing

### Merge Behavior
- Existing lead found → update `extra_data` with new fields
- Track new source as additional `GrowthEvent`
- Do NOT overwrite existing assigned_to or status
- Log merge in activity timeline

### Idempotency
- Public submit endpoint uses `Idempotency-Key` header (optional)
- If same key submitted within 5 minutes, return existing lead_id
- Prevents double-submit from form widgets

## Import/Migration

### CSV Import Flow
```
1. Upload CSV → POST /files with entity_type="import"
2. Map columns → UI shows column mapping interface
3. Preview → Show first 10 rows with mapping applied
4. Execute → Background worker processes rows
5. Report → Return success/error/duplicate counts
```

### Import Worker Behavior
- Process in batches of 100
- Dedupe check per row
- Create GrowthEvent with source="import"
- Track progress in Redis (for progress bar)
- Email summary when complete

## Webhook Ingestion

### Inbound Webhook
```
POST /api/v1/webhooks/inbound/{tenant_slug}/{integration_name}

Body: provider-specific payload

Processing:
1. Verify signature (if configured)
2. Store raw payload in webhook_events table
3. Parse payload based on integration_name
4. Map to lead/activity creation
5. Process asynchronously via worker
```

### Outbound Webhook Subscriptions (Future)
```python
class WebhookSubscription(TenantModel):
    url = Column(Text, nullable=False)
    events = Column(JSONB)  # ["lead.created", "deal.stage_changed", "deal.won"]
    secret = Column(String(255))  # for HMAC signature
    is_active = Column(Boolean, default=True)
    last_delivery_at = Column(DateTime)
    failure_count = Column(Integer, default=0)
```

## Testing Requirements
- [ ] Public form submit creates lead with correct attribution
- [ ] Duplicate phone returns existing lead (merge)
- [ ] UTM parameters are correctly stored in growth_events
- [ ] CSV import handles 10K rows without timeout
- [ ] Webhook signature verification rejects invalid payloads
- [ ] Idempotency key prevents duplicate leads
