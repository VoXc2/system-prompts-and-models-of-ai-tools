# Identity & RBAC Model

## User Model

```python
class User(TenantModel):
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    full_name_ar = Column(String(255))
    role = Column(String(50), nullable=False, default="agent")
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    # UniqueConstraint: (tenant_id, email)
```

## Role Presets

| Role | Description | Scope |
|------|-------------|-------|
| `owner` | Tenant creator. Full admin. | All resources within tenant |
| `admin` | Administrator. Can manage users, settings, integrations. | All resources within tenant |
| `manager` | Team lead. Can see team data, reassign leads. | Team + own resources |
| `agent` | Sales rep. Works leads, deals, conversations. | Own assigned resources |
| `viewer` | Read-only access. Dashboards and reports. | Read-only within tenant |
| `operator` | Dealix internal. Elevated access for managed service. | Client tenant (managed) |

## Permission Matrix

| Permission | owner | admin | manager | agent | viewer |
|-----------|-------|-------|---------|-------|--------|
| Manage users | Yes | Yes | No | No | No |
| Manage settings | Yes | Yes | No | No | No |
| Manage integrations | Yes | Yes | No | No | No |
| Manage playbooks | Yes | Yes | No | No | No |
| Manage SLA policies | Yes | Yes | No | No | No |
| View all leads | Yes | Yes | Yes | Own only | Yes |
| Create leads | Yes | Yes | Yes | Yes | No |
| Update leads | Yes | Yes | Yes | Own only | No |
| Delete leads | Yes | Yes | No | No | No |
| View all deals | Yes | Yes | Yes | Own only | Yes |
| Manage deals | Yes | Yes | Yes | Own only | No |
| View analytics | Yes | Yes | Yes | Own only | Yes |
| Export data | Yes | Yes | Yes | No | No |
| Manage sequences | Yes | Yes | Yes | No | No |
| Approve social comments | Yes | Yes | Yes | No | No |
| View audit logs | Yes | Yes | No | No | No |
| Manage billing | Yes | No | No | No | No |

## Auth Flow

```
1. POST /auth/login → validate credentials → issue JWT access + refresh tokens
2. JWT payload: {sub: user_id, tenant_id, role, exp}
3. get_current_user() → decode JWT → return {user_id, tenant_id, role}
4. Role check in endpoint (explicit, not middleware)
5. Refresh via POST /auth/refresh with refresh_token
```

## Service Accounts (Future)
- API keys for integrations
- Scoped to specific permissions
- Tracked in audit log
- Rotatable without user password change

## Teams (Future)
- Users belong to teams within a tenant
- Leads/deals can be assigned to teams
- Manager role scoped to team visibility
- Round-robin assignment within team

## Audit Requirements
- All permission changes logged to audit_log
- All login/logout events logged
- All admin actions logged with IP address
- Role changes require owner/admin role
- Bulk operations logged as single audit entry with details

## API Groups

```
POST   /auth/register      # Create tenant + owner user
POST   /auth/login          # Authenticate
POST   /auth/refresh        # Refresh tokens
GET    /auth/me             # Current user profile
GET    /users               # List tenant users (admin+)
POST   /users               # Create user (admin+)
PUT    /users/{id}          # Update user (admin+)
DELETE /users/{id}          # Deactivate user (owner only)
PUT    /users/{id}/role     # Change role (owner only)
```
