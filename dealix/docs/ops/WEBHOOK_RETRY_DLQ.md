# Webhook Retry + DLQ Strategy

## Current Implementation
Webhooks from Moyasar land at `/api/v1/webhooks/moyasar`.

## Retry Policy
- 3 retry attempts with exponential backoff (1s, 10s, 60s)
- After 3 failures: mark as dead-letter, alert via Sentry

## DLQ Storage
Failed webhook events stored in DB table `webhook_dlq`:
- payload
- received_at
- attempts
- last_error
- status (pending|retrying|abandoned|replayed)

## Replay Script
```bash
python scripts/replay_webhook.py --id <dlq_id>
```

## Monitoring
- Alert if DLQ count > 5 in 1 hour
- Weekly DLQ cleanup review
