#!/bin/bash
# Dealix — Full deployment verification + activation
# Usage: API_BASE=https://api.dealix.me ./scripts/go_live.sh

set -e
BASE="${API_BASE:-http://localhost:8000}"
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'
PASS=0
FAIL=0

check() {
    local name="$1" url="$2" expect="${3:-200}"
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")
    if [ "$code" = "$expect" ]; then
        echo -e "${GREEN}✅ $name ($code)${NC}"
        PASS=$((PASS+1))
    else
        echo -e "${RED}❌ $name (got $code, expected $expect)${NC}"
        FAIL=$((FAIL+1))
    fi
}

echo "=== Dealix Deployment Check ==="
echo "Base: $BASE"
echo ""

echo "--- Core Health ---"
check "Health" "$BASE/health"
check "API Health" "$BASE/api/v1/health"
check "Pricing" "$BASE/api/v1/pricing/plans"

echo ""
echo "--- Automation System ---"
check "OS Stages" "$BASE/api/v1/os/stages"
check "WhatsApp Providers" "$BASE/api/v1/os/whatsapp-providers"
check "Draft Stats" "$BASE/api/v1/drafts/stats"

echo ""
echo "--- Generate Test Email ---"
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 \
    -X POST "$BASE/api/v1/automation/email/generate" \
    -H "Content-Type: application/json" \
    -d '{"company":"TestCo","sector":"saas"}' 2>/dev/null || echo "000")
if [ "$code" = "200" ]; then
    echo -e "${GREEN}✅ Email Generate ($code)${NC}"
    PASS=$((PASS+1))
else
    echo -e "${RED}❌ Email Generate (got $code)${NC}"
    FAIL=$((FAIL+1))
fi

echo ""
echo "--- Compliance Check ---"
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    -X POST "$BASE/api/v1/automation/compliance/check" \
    -H "Content-Type: application/json" \
    -d '{"company":"TestCo","email":"test@test.com","source":"website"}' 2>/dev/null || echo "000")
if [ "$code" = "200" ]; then
    echo -e "${GREEN}✅ Compliance Check ($code)${NC}"
    PASS=$((PASS+1))
else
    echo -e "${RED}❌ Compliance Check (got $code)${NC}"
    FAIL=$((FAIL+1))
fi

echo ""
echo "--- Reply Classifier ---"
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    -X POST "$BASE/api/v1/automation/reply/classify" \
    -H "Content-Type: application/json" \
    -d '{"reply_text":"مهتم أبي أجرب"}' 2>/dev/null || echo "000")
if [ "$code" = "200" ]; then
    echo -e "${GREEN}✅ Reply Classifier ($code)${NC}"
    PASS=$((PASS+1))
else
    echo -e "${RED}❌ Reply Classifier (got $code)${NC}"
    FAIL=$((FAIL+1))
fi

echo ""
echo "========================="
echo -e "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"

if [ $FAIL -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🚀 ALL CHECKS PASSED — Ready for outreach!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Seed first batch:  python scripts/seed_first_batch.py"
    echo "  2. Review drafts:     curl $BASE/api/v1/drafts?status=draft"
    echo "  3. Approve batch:     curl -X POST $BASE/api/v1/drafts/approve-batch -H 'Content-Type: application/json' -d '{\"batch_id\":\"BATCH_ID\"}'"
    echo "  4. Send emails:       curl -X POST '$BASE/api/v1/drafts/send-approved-batch?channel=email&batch_size=5'"
else
    echo ""
    echo -e "${RED}⚠️  Fix failures above before proceeding${NC}"
fi
