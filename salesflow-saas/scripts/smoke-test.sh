#!/usr/bin/env bash
# Dealix API Smoke Test
set -e

API_URL="${API_URL:-http://localhost:8000}"
PASS=0
FAIL=0

test_endpoint() {
  local method="$1"
  local path="$2"
  local data="$3"
  local expected_code="${4:-200}"

  if [ -n "$data" ]; then
    code=$(curl -sf -o /dev/null -w "%{http_code}" -X "$method" "${API_URL}${path}" \
      -H "Content-Type: application/json" -d "$data" 2>/dev/null || echo "000")
  else
    code=$(curl -sf -o /dev/null -w "%{http_code}" -X "$method" "${API_URL}${path}" 2>/dev/null || echo "000")
  fi

  if [ "$code" = "$expected_code" ]; then
    echo "✅ ${method} ${path} → ${code}"
    PASS=$((PASS + 1))
  else
    echo "❌ ${method} ${path} → ${code} (expected ${expected_code})"
    FAIL=$((FAIL + 1))
  fi
}

echo "=========================================="
echo "  Dealix API Smoke Test - $(date)"
echo "=========================================="
echo ""

# Health endpoints
test_endpoint "GET" "/api/v1/health" "" "200"

# Auth endpoints
test_endpoint "POST" "/api/v1/auth/register" '{"company_name":"Test Co","full_name":"Test User","email":"smoke-test-'$(date +%s)'@test.com","password":"TestPass123!","phone":"+966500000000"}' "201"
test_endpoint "POST" "/api/v1/auth/login" '{"email":"smoke-test@test.com","password":"TestPass123!"}' "200"

echo ""
echo "=========================================="
echo "  Results: ${PASS} passed, ${FAIL} failed"
echo "=========================================="

[ $FAIL -eq 0 ] && exit 0 || exit 1
