# UptimeRobot Setup — Dealix

## Monitors المطلوبة

| Name                  | URL                                  | Type  | Interval |
|-----------------------|--------------------------------------|-------|----------|
| Dealix API Health     | https://api.dealix.sa/health         | HTTP  | 5 min    |
| Dealix API Deep Health| https://api.dealix.sa/health/deep    | HTTP  | 15 min   |
| Dealix Landing        | https://dealix.me                    | HTTP  | 5 min    |
| Dealix Dashboard      | https://dashboard.dealix.sa          | HTTP  | 15 min   |

## إعداد عبر API

```bash
UR_KEY="<your-uptimerobot-api-key>"

for M in \
  "Dealix API Health|https://api.dealix.sa/health|300" \
  "Dealix API Deep|https://api.dealix.sa/health/deep|900" \
  "Dealix Landing|https://dealix.me|300" \
  "Dealix Dashboard|https://dashboard.dealix.sa|900"
do
  IFS='|' read -r NAME URL INT <<< "$M"
  curl -s -X POST https://api.uptimerobot.com/v2/newMonitor \
    -d "api_key=${UR_KEY}" \
    -d "friendly_name=${NAME}" \
    -d "url=${URL}" \
    -d "type=1" \
    -d "interval=${INT}"
done
```

## تنبيهات
- SMS إلى sami.assiri11@gmail.com
- Email إلى sami.assiri11@gmail.com
- Webhook POST إلى `https://api.dealix.sa/api/v1/webhooks/uptime` (يستخدم N8N_WEBHOOK_SECRET)
