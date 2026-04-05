#!/usr/bin/env bash
# PostgreSQL "incremental" strategies (choose one in production):
#
# 1) Managed cloud (recommended for SaaS): AWS RDS automated backups + PITR, or Cloud SQL, or Azure.
# 2) WAL archiving: archive_command ships WAL to S3; base backup weekly + continuous WAL = incremental timeline.
# 3) pgBackRest: full + incremental + differential with built-in S3 support.
# 4) Logical daily full (backup-postgres-full.sh) + hourly WAL archives for RPO < 24h.
#
# This repo does not ship a WAL daemon; configure archive_command in postgresql.conf, e.g.:
#   archive_command = 'aws s3 cp %p s3://bucket/wal/%f'
#
# Verify WAL segments with: pg_archivecleanup (see PostgreSQL docs).

echo "See infra/backup/BACKUP_AND_RECOVERY.md § Database incremental / PITR."
exit 0
