#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# setup_uptimerobot.sh — إنشاء monitors + alert contacts تلقائياً
# Usage:
#   export UPTIMEROBOT_API_KEY="<your-uptimerobot-api-key-here>"
#   export ALERT_EMAIL="sami.assiri11@gmail.com"
#   # optional SMS (Twilio/Clicksend integrated in UptimeRobot):
#   # export ALERT_SMS="+9665XXXXXXXX"
#   bash scripts/infra/setup_uptimerobot.sh
# ─────────────────────────────────────────────────────────────
set -euo pipefail

API_KEY="${UPTIMEROBOT_API_KEY:?UPTIMEROBOT_API_KEY is required}"
ALERT_EMAIL="${ALERT_EMAIL:-sami.assiri11@gmail.com}"
BASE="https://api.uptimerobot.com/v2"

echo "═══ Dealix UptimeRobot Setup ═══"

# 1) Create email alert contact
echo "→ Creating email alert contact..."
AC_RESPONSE=$(curl -sS -X POST "$BASE/newAlertContact" \
  -d "api_key=$API_KEY" \
  -d "type=2" \
  -d "value=$ALERT_EMAIL" \
  -d "friendly_name=Sami (primary)" \
  -d "format=json")
echo "$AC_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  contact_id:', d.get('alertcontact',{}).get('id','EXISTS'))" || true

# Fetch contact IDs
CONTACTS=$(curl -sS -X POST "$BASE/getAlertContacts" -d "api_key=$API_KEY" -d "format=json" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(','.join(str(c['id']) for c in d.get('alert_contacts',[])))")
echo "→ Alert contacts: $CONTACTS"

# 2) Create monitors
create_monitor() {
  local name="$1" url="$2" keyword="${3:-}"
  local type=1  # HTTP
  local extras=""
  if [[ -n "$keyword" ]]; then
    type=2  # keyword
    extras='-d "keyword_type=2" -d "keyword_value='"$keyword"'"'
  fi
  echo "→ $name ($url)"
  eval curl -sS -X POST "$BASE/newMonitor" \
    -d "api_key=$API_KEY" \
    -d "friendly_name=$(echo "$name" | sed 's/ /%20/g')" \
    -d "url=$url" \
    -d "type=$type" \
    -d "interval=300" \
    -d "timeout=30" \
    -d "alert_contacts=$CONTACTS" \
    $extras \
    -d "format=json" | python3 -c "import sys,json; d=json.load(sys.stdin); m=d.get('monitor',{}); print(f'  id={m.get(\"id\",\"ERR\")} status={m.get(\"status\",\"?\")}')" || true
}

create_monitor "Dealix API Health"     "https://api.dealix.me/health"      'status":"ok'
create_monitor "Dealix API Deep Health" "https://api.dealix.me/health/deep" 'status":"ok'
create_monitor "Dealix Landing"        "https://dealix.me/"                ""

echo
echo "✓ UptimeRobot setup complete."
echo "  Dashboard: https://uptimerobot.com/dashboard"
echo "  Expected alerts: 5-min interval, email → $ALERT_EMAIL"
