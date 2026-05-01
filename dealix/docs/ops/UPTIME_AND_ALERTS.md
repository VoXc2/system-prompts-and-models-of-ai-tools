# Uptime Monitoring + Alerting

## Monitors
| Service | Endpoint | Interval | Alert threshold |
|---------|----------|----------|-----------------|
| UptimeRobot | /healthz | 5 min | 2 min downtime |
| UptimeRobot | /api/v1/pricing/plans | 15 min | 5 min downtime |
| Better Stack (optional) | full status | 1 min | any fail |

## Alert Channels
- Email (primary): sami.assiri11@gmail.com
- SMS (critical): founder phone
- Slack: #dealix-alerts (when workspace exists)

## Response SLA
- Critical (site down): 15 min acknowledgment
- High (feature broken): 1 hour
- Medium (degraded): 4 hours
- Low (cosmetic): 24 hours

## Setup Guide
See Issue #85 for UptimeRobot setup steps.
