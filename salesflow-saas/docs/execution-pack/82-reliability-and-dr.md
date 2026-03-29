# Reliability & Disaster Recovery

## Health Checks
- `GET /health` — Liveness (200 OK)
- `GET /health/ready` — Readiness (DB + Redis)
- Docker healthcheck configured

## Database Reliability
- **PostgreSQL 16** with `pool_pre_ping=True` (connection validation)
- Connection pool: 20 connections, 10 overflow
- PITR (Point-in-Time Recovery) enabled in production
- Daily automated backups
- WAL archiving for continuous backup

## Redis Reliability
- Redis 7 with persistence (RDB + AOF)
- Used for: Celery broker, rate limiting, caching
- Not used as primary data store (crash-safe)

## Worker Reliability
- Celery with `acks_late=True` (task not lost on worker crash)
- Task visibility timeout: 10 minutes
- Failed tasks: retry 3x with exponential backoff
- Dead letter queue for permanently failed tasks

## RPO/RTO Targets

| Scenario | RPO | RTO |
|----------|-----|-----|
| Database corruption | 1 hour (PITR) | 4 hours |
| Server failure | 0 (if replica) | 15 minutes (failover) |
| Region failure | 24 hours | 8 hours (manual) |
| Application bug | 0 (git revert) | 30 minutes |

## Backup Strategy
| Component | Method | Frequency | Retention |
|-----------|--------|-----------|-----------|
| PostgreSQL | pg_dump + PITR | Continuous + daily full | 30 days |
| Redis | RDB snapshot | Hourly | 7 days |
| File uploads | S3 versioning | Continuous | 90 days |
| Configuration | Git | Every change | Indefinite |

## Incident Runbooks (Placeholder)

### Database Unreachable
1. Check PostgreSQL process status
2. Check connection limits (`max_connections`)
3. Check disk space
4. Restart if needed
5. Verify via `/health/ready`

### Worker Queue Backed Up
1. Check Celery worker count
2. Check Redis memory usage
3. Scale workers if needed
4. Check for stuck tasks
5. Restart workers if necessary

### API Response Time Degraded
1. Check database query performance
2. Check Redis latency
3. Review recent deployments
4. Check for N+1 query patterns
5. Scale if load-related

## Rollback Plan
- Every deployment is tagged in git
- Rollback = deploy previous tag
- Database migrations: always write reversible migrations
- Feature flags for risky features (future)
