# Observability Architecture

## Three Pillars

### 1. Structured Logging
- All logs as JSON (not plain text)
- Every log includes: `timestamp`, `level`, `tenant_id`, `user_id`, `request_id`, `module`
- Sensitive data (tokens, passwords) NEVER logged
- Log levels: DEBUG (dev only), INFO (operations), WARNING (degraded), ERROR (failure), CRITICAL (outage)

### Log Format
```json
{
  "timestamp": "2026-03-29T14:30:00.123Z",
  "level": "INFO",
  "module": "sequence_worker",
  "tenant_id": "uuid",
  "request_id": "uuid",
  "message": "Sequence step executed",
  "data": {
    "enrollment_id": "uuid",
    "step_type": "send_whatsapp",
    "step_order": 2,
    "duration_ms": 450
  }
}
```

### 2. Traces (AI-Specific)
Every AI call creates an `AITrace` record:

```python
class AITrace(TenantModel):
    workflow = Column(String(100), index=True)   # qualification, content, routing
    action = Column(String(100))                  # score_lead, draft_comment
    provider = Column(String(50))                 # openai, anthropic
    model = Column(String(100))                   # gpt-4o-mini, claude-sonnet
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost_usd = Column(Numeric(10, 6), default=0)
    latency_ms = Column(Integer)
    status = Column(String(50), index=True)       # success, error, timeout, filtered
    was_filtered = Column(String(50))              # content_filter, hallucination
    human_override = Column(String(50))            # approved, rejected, edited
    error_message = Column(Text)
```

### AI Cost Dashboard
| Metric | Query |
|--------|-------|
| Total cost (monthly) | SUM(cost_usd) WHERE month = current |
| Cost per workflow | GROUP BY workflow |
| Cost per tenant | GROUP BY tenant_id |
| Avg latency | AVG(latency_ms) |
| Error rate | COUNT(status=error) / COUNT(*) |
| Human override rate | COUNT(human_override IS NOT NULL) / COUNT(*) |

### 3. Metrics (Application Health)
| Metric | Type | Source |
|--------|------|--------|
| `api.request.duration` | Histogram | Middleware |
| `api.request.count` | Counter | Middleware |
| `api.request.error` | Counter | Error handler |
| `worker.task.duration` | Histogram | Celery signal |
| `worker.task.success` | Counter | Celery signal |
| `worker.task.failure` | Counter | Celery signal |
| `db.query.duration` | Histogram | SQLAlchemy event |
| `redis.command.duration` | Histogram | Redis wrapper |
| `ai.call.duration` | Histogram | AI brain wrapper |
| `ai.call.cost` | Counter | AI brain wrapper |
| `ai.call.tokens` | Counter | AI brain wrapper |

## Correlation ID Rules
- Every HTTP request gets a `X-Request-ID` (generated or from client)
- Passed to all service calls, DB queries, worker tasks
- Stored in AI traces and audit logs
- Enables full request tracing from API → service → worker → external call

## Health Check Endpoints
```
GET /health           # Basic liveness (returns 200)
GET /health/ready     # Readiness (checks DB + Redis connectivity)
GET /health/detailed  # Full status (admin only)
```

### Detailed Health Response
```json
{
  "status": "healthy",
  "checks": {
    "database": {"status": "up", "latency_ms": 5},
    "redis": {"status": "up", "latency_ms": 2},
    "celery": {"status": "up", "workers": 3},
    "ai_providers": {
      "openai": {"status": "up", "latency_ms": 200},
      "anthropic": {"status": "up", "latency_ms": 180}
    }
  },
  "version": "1.0.0",
  "uptime_seconds": 86400
}
```

## Incident Response Placeholders
- **RPO** (Recovery Point Objective): 1 hour (PostgreSQL PITR)
- **RTO** (Recovery Time Objective): 4 hours
- **Backup**: Daily automated, PITR-enabled
- **Runbook location**: `docs/runbooks/` (to be created)
