# Security Baseline

## Authentication
- JWT access tokens (30 min expiry)
- JWT refresh tokens (7 day expiry)
- Password hashing: bcrypt (12 rounds)
- Rate limiting on auth endpoints: 5/min register, 10/min login

## Authorization (RBAC)
- Role extracted from JWT claims
- Permission checks in endpoint handlers (explicit, not middleware)
- Tenant isolation via `tenant_id` from JWT
- No cross-tenant queries in application code

## Input Validation
- Pydantic schemas validate all request bodies
- UUID validation on path parameters
- Query parameter type checking via FastAPI
- SQL injection prevented by SQLAlchemy parameterized queries
- XSS prevented by React's default escaping

## Rate Limiting
| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /auth/register | 5 | 1 minute |
| POST /auth/login | 10 | 1 minute |
| POST /forms/submit | 20 | 1 minute |
| POST /webhooks/* | 100 | 1 minute |
| General API | 200 | 1 minute |

## Webhook Security
- Signature verification (HMAC-SHA256) for incoming webhooks
- Webhook secrets stored encrypted
- Replay protection (timestamp validation, 5-minute window)

## Secrets Management
- Environment variables for all secrets
- Never committed to repository
- Docker secrets in production
- `.env` file in `.gitignore`

## Error Handling
- Global exception handler catches all unhandled errors
- Stack traces NEVER exposed in API responses
- Structured error responses: `{"detail": "Human-readable message"}`
- Internal errors logged with full context

## Dependency Security
- `requirements.txt` with pinned versions
- Regular dependency updates
- No known vulnerable packages (check via `pip-audit`)

## Service Account Security (Future)
- API keys hashed before storage
- Scoped permissions per key
- Automatic rotation reminders
- Usage tracking and rate limits per key

## Admin Action Audit
All admin actions logged to `audit_log`:
- User creation/deletion/role change
- Settings changes
- Integration connections
- Data exports
- Bulk operations
