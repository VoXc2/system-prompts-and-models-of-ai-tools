# Tenancy Model

## Hierarchy

```
Organization (billing entity, future)
  └── Tenant (data isolation boundary)
       ├── Workspace (logical grouping, future)
       └── Brand (white-label identity, future)
```

### Current Implementation (Phase 1)
- **Tenant** is the primary boundary. Each signup creates one tenant.
- `tenant_id` (UUID) on every business entity.
- No Organization/Workspace abstraction yet — tenant = org = workspace.

### Future Evolution (Phase 2+)
- **Organization**: Billing entity that owns one or more tenants
- **Workspace**: Logical partition within a tenant (e.g., by team or product line)
- **Brand**: White-label identity (logo, colors, domain) attached to a tenant

## Tenant Types

| Type | Description | Permissions |
|------|-------------|-------------|
| **client** | Standard SaaS customer | Full self-service |
| **managed** | Client operated by Dealix team | Client: read + approve. Operator: full access |
| **partner** | White-label reseller | Manages sub-tenants, sees aggregate data |
| **operator** | Dealix internal | Cross-tenant visibility, system admin |

## Tenant Schema (Current)

```python
class Tenant(BaseModel):
    __tablename__ = "tenants"
    # BaseModel provides: id, created_at
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255))
    slug = Column(String(100), unique=True, nullable=False, index=True)
    industry = Column(String(100))
    plan = Column(String(50), default="basic")
    logo_url = Column(String(500))
    phone = Column(String(20))
    email = Column(String(255))
    whatsapp_number = Column(String(20))
    settings = Column(JSONB, default=dict)  # timezone, locale, custom config
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True))
```

## Tenant Isolation Rules

1. **Query-level**: Every SELECT must include `WHERE tenant_id = :tid`
2. **Model-level**: `TenantModel` base class provides `tenant_id` column with index
3. **API-level**: `get_current_user()` extracts `tenant_id` from JWT claims
4. **Worker-level**: `tenant_id` passed in Celery task kwargs
5. **No cross-tenant joins**: Never join data across tenants in application code

## Tenant Lifecycle

```
created → trial → active → suspended → cancelled → deleted
                    ↑                       │
                    └───── reactivated ──────┘
```

## Tenant Settings Structure (JSONB)

```json
{
  "timezone": "Asia/Riyadh",
  "locale": "ar",
  "currency": "SAR",
  "working_days": [0, 1, 2, 3, 6],
  "working_hours": {"start": "09:00", "end": "17:00"},
  "auto_assign": true,
  "default_pipeline": "standard",
  "notifications": {"email": true, "whatsapp": true, "push": false}
}
```

## Multi-Tenant Testing Requirements
- [ ] Tenant A cannot read Tenant B's leads
- [ ] Tenant A cannot update Tenant B's deals
- [ ] Creating a lead with wrong tenant_id fails
- [ ] API returns 404 (not 403) for cross-tenant access attempts
- [ ] Background workers respect tenant_id boundaries
- [ ] Aggregate queries never leak across tenants
