# Dealix Service Level Objectives (SLO)

**Version:** 1.0.0  
**Effective:** 2026-04-23  
**Review:** Monthly, or after any incident

---

## API Availability

| SLI | Target | Measurement | Alert Threshold |
|-----|--------|-------------|-----------------|
| Uptime (monthly) | 99.5% | UptimeRobot on `/api/v1/health` | < 99% triggers incident |
| Health endpoint response | < 200ms p95 | k6 smoke test | > 500ms p95 |

## API Latency

| Endpoint Category | p50 Target | p95 Target | p99 Target |
|-------------------|------------|------------|------------|
| Health / public reads | < 50ms | < 200ms | < 500ms |
| Pricing / plans | < 100ms | < 300ms | < 1000ms |
| Lead CRUD | < 200ms | < 500ms | < 2000ms |
| AI agent calls | < 2000ms | < 5000ms | < 10000ms |
| Webhook processing | < 500ms | < 2000ms | < 5000ms |

## Error Rate

| Metric | Target | Alert |
|--------|--------|-------|
| HTTP 5xx rate | < 0.5% of requests | > 1% for 5 min |
| Webhook failure rate | < 2% | > 5% for 15 min |
| DLQ depth | < 10 entries | > 50 triggers alert |

## Recovery

| Metric | Target |
|--------|--------|
| RPO (Recovery Point Objective) | 24 hours (daily DB backup) |
| RTO (Recovery Time Objective) | 15 minutes (tested via drill) |
| Rollback time | < 5 minutes (git checkout + restart) |
| MTTR (Mean Time To Recovery) | < 30 minutes |

## Revenue Funnel

| Step | Freshness Target |
|------|-----------------|
| Lead capture → PostHog event | < 5 seconds |
| Payment webhook → PostHog event | < 10 seconds |
| DLQ entry → first retry | < 60 seconds |
| Approval request → notification | < 5 minutes |

## Monitoring

| System | Check Interval | Alert Channel |
|--------|---------------|---------------|
| UptimeRobot | 5 minutes | SMS + Email |
| Sentry | Real-time | Email |
| DLQ depth | On admin request | Dashboard |
| Circuit breakers | On admin request | Dashboard |

---

## How to Verify

```bash
# Health latency
curl -w "%{time_total}s\n" -o /dev/null -s https://api.dealix.me/api/v1/health

# k6 smoke test
k6 run --env API_BASE=https://api.dealix.me scripts/k6_smoke_test.js

# DLQ depth
curl -H "Authorization: Bearer $TOKEN" https://api.dealix.me/api/v1/admin/dlq/queues

# Circuit breaker states
curl -H "Authorization: Bearer $TOKEN" https://api.dealix.me/api/v1/admin/circuit-breakers
```

## Escalation

| Severity | Condition | Response |
|----------|-----------|----------|
| P1 - Critical | Service down > 5 min | Immediate (see RUNBOOK Scenario 1) |
| P2 - Major | Error rate > 5% for 15 min | Within 1 hour |
| P3 - Minor | Latency > SLO for 30 min | Within 4 hours |
| P4 - Low | DLQ depth > 20 | Next business day |
