#!/usr/bin/env bash
# Dealix Health Check Script
set -e

API_URL="${API_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
DB_HOST="${DB_HOST:-localhost}"
REDIS_HOST="${REDIS_HOST:-localhost}"

PASS=0
FAIL=0

check() {
  local name="$1"
  local cmd="$2"
  if eval "$cmd" > /dev/null 2>&1; then
    echo "✅ PASS: $name"
    PASS=$((PASS + 1))
  else
    echo "❌ FAIL: $name"
    FAIL=$((FAIL + 1))
  fi
}

echo "=========================================="
echo "  Dealix Health Check - $(date)"
echo "=========================================="
echo ""

check "Backend API (/health)" "curl -sf ${API_URL}/api/v1/health"
check "Frontend (landing page)" "curl -sf ${FRONTEND_URL} | head -1"
check "PostgreSQL connection" "pg_isready -h ${DB_HOST} -p 5432"
check "Redis connection" "redis-cli -h ${REDIS_HOST} ping"
check "Celery workers" "docker ps --filter name=celery_worker --filter status=running -q | head -1"
check "Celery beat" "docker ps --filter name=celery_beat --filter status=running -q | head -1"

echo ""
echo "=========================================="
echo "  Results: ${PASS} passed, ${FAIL} failed"
echo "=========================================="

[ $FAIL -eq 0 ] && exit 0 || exit 1
