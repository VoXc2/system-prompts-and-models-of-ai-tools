# Entitlements & Billing Model

## Plan Tiers

| Plan | Monthly | Seats | AI Calls/mo | Leads | Sequences | Social Streams |
|------|---------|-------|-------------|-------|-----------|----------------|
| **trial** | Free (14 days) | 2 | 100 | 500 | 3 | 1 |
| **basic** | 1,500 SAR | 3 | 500 | 2,000 | 10 | 3 |
| **professional** | 5,000 SAR | 10 | 2,000 | 10,000 | 50 | 10 |
| **enterprise** | 15,000 SAR | 25 | 10,000 | Unlimited | Unlimited | 25 |
| **managed** | Custom | Custom | Custom | Custom | Custom | Custom |

## Entitlement Categories

### 1. Feature Entitlements (Boolean)
| Feature | trial | basic | pro | enterprise |
|---------|-------|-------|-----|------------|
| Lead management | Yes | Yes | Yes | Yes |
| Pipeline management | Yes | Yes | Yes | Yes |
| Conversations | Yes | Yes | Yes | Yes |
| AI agents | Limited | Yes | Yes | Yes |
| Social listening | No | Yes | Yes | Yes |
| Proposals & contracts | No | Yes | Yes | Yes |
| Custom fields | No | No | Yes | Yes |
| API access | No | No | Yes | Yes |
| White-label | No | No | No | Yes |
| Custom domain | No | No | No | Yes |
| Playbooks | No | No | Yes | Yes |
| SLA tracking | No | No | Yes | Yes |

### 2. Seat Limits
- Counted by active users per tenant
- Invite blocked when at limit
- Deactivated users don't count

### 3. Usage Limits
- AI calls: counted per month, reset on billing cycle
- Leads: total active leads (not historical)
- Messages: WhatsApp/email sent per month
- Storage: file upload total size

## Subscription Schema (Current)

```python
class Subscription(TenantModel):
    plan = Column(String(50), nullable=False)  # trial, basic, professional, enterprise, managed
    status = Column(String(50), default="active", index=True)  # trial, active, past_due, cancelled
    price_monthly = Column(Numeric(10, 2))
    currency = Column(String(3), default="SAR")
    current_period_start = Column(Date)
    current_period_end = Column(Date)
```

## Billing Integration Points (Future)

```
Subscription created → webhook to billing provider
Plan changed → prorate and update
Usage threshold → notify tenant
Trial expiring → send reminder (3 days, 1 day, expired)
Payment failed → mark past_due → restrict features after grace
Cancelled → data retained 30 days → marked for deletion
```

## Usage Metering (Future)

```python
class UsageMeter(TenantModel):
    meter_type = Column(String(50))  # ai_calls, messages, leads, storage
    period_start = Column(Date)
    period_end = Column(Date)
    current_value = Column(Integer, default=0)
    limit_value = Column(Integer)
    overage_allowed = Column(Boolean, default=False)
```

## Entitlement Enforcement Points
1. **API middleware**: Check feature entitlement before route execution
2. **UI**: Hide/disable features not in plan
3. **Worker**: Skip AI calls if quota exceeded
4. **Invite flow**: Block if seat limit reached
5. **Import**: Block if lead limit reached

## Onboarding State Model

### Self-Serve
```
signup → verify_email → setup_profile → create_pipeline → import_leads → connect_whatsapp → activate
```

### Managed Service
```
contract_signed → operator_setup → data_migration → configuration → training → go_live → monitoring
```

### White-Label Partner
```
partner_agreement → branding_setup → domain_config → first_client → training → active
```

### Onboarding Checklist (Stored in tenant.settings)

```json
{
  "onboarding": {
    "mode": "self_serve",
    "steps": {
      "profile_complete": true,
      "pipeline_created": false,
      "first_lead_added": false,
      "whatsapp_connected": false,
      "first_sequence_created": false,
      "team_invited": false
    },
    "started_at": "2026-03-29T00:00:00Z",
    "completed_at": null
  }
}
```
