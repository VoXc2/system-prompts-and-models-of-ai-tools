# Backup + Restore Strategy

## What to back up
1. PostgreSQL database (Railway managed)
2. Application secrets (never in repo)
3. Customer data exports

## Backup Frequency
- Database: daily automated (Railway provides)
- Hourly snapshots: via scheduled script (TODO)
- Monthly cold archive: to S3 or equivalent

## Restore Drill
Run quarterly:
1. Spin up staging DB
2. Restore from latest backup
3. Verify data integrity
4. Document time-to-restore

## Retention
- Daily backups: 7 days
- Weekly: 4 weeks
- Monthly: 12 months
- Yearly: 7 years (legal)
