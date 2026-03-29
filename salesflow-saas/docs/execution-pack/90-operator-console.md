# Operator Console

## Purpose
Internal dashboard for Dealix team to manage all tenant instances, monitor health, and operate managed service clients.

## Console Areas

### 1. Tenant Management
- List all tenants (status, plan, industry, created_at)
- Tenant health score (activity, SLA compliance, feature adoption)
- Quick actions: impersonate, configure, pause, archive
- Onboarding progress tracker per tenant

### 2. Approval Queue
- Pending social comments across all managed tenants
- Pending proposals requiring review
- Pending content requiring approval
- Bulk approve/reject capability

### 3. SLA Dashboard
- Active breaches across all tenants
- Breach trend (improving/degrading)
- Response time by tenant
- Escalation queue

### 4. Integration Health
- Connected integrations per tenant
- Failed webhooks (last 24h)
- Token expiry warnings
- Sync status and last sync time

### 5. AI Operations
- Total AI cost this month (by tenant, by agent)
- Error rate by agent type
- Latency trends
- Human override rate
- Cost per lead/deal

### 6. Revenue Operations
- Pipeline value across all managed tenants
- Pipeline velocity per tenant
- Deals at risk
- Follow-up compliance rates

### 7. Client Delivery
- Managed service SLA compliance
- Weekly/monthly reporting status
- Client satisfaction indicators
- Expansion opportunities

### 8. Partner Management (Future)
- Partner list and status
- Sub-tenant count per partner
- Partner performance metrics
- Revenue share tracking

## Operator Permissions
- Operators can view and manage assigned tenant data
- Operators cannot delete tenants or modify billing
- Super-admin required for tenant creation/deletion
- All operator actions logged in audit trail

## API Endpoints (Operator-Only)
```
GET    /operator/tenants              # List all tenants
GET    /operator/tenants/{id}/health  # Tenant health score
POST   /operator/tenants/{id}/impersonate  # Get tenant-scoped token
GET    /operator/approvals            # Cross-tenant approval queue
GET    /operator/sla/breaches         # Cross-tenant SLA breaches
GET    /operator/ai/costs             # AI cost summary
GET    /operator/integrations/health  # Integration status
```
