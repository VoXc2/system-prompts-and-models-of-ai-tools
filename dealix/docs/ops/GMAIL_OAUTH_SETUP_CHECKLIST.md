# Gmail OAuth Setup — for autonomous email sending

One-time setup. ~15 minutes. Free.

This gives Dealix permission to send emails from your Gmail address via OAuth refresh-token (not your password). Required for `/api/v1/email/send-approved` and `/api/v1/email/send-batch`.

## What you need before you start

- A Gmail address (personal or Workspace). For deliverability: Workspace > personal.
- Access to Google Cloud Console for that account.
- 15 minutes.

## Step-by-step

### 1. Create OAuth client in Google Cloud

Open: https://console.cloud.google.com/apis/credentials

- Project: same one you used for Custom Search + Maps (or create a new one).
- Click **"Create Credentials" → "OAuth client ID"**.
- If prompted, configure the consent screen:
  - User type: **External** (you're the only user; that's fine for `Testing` mode).
  - App name: **Dealix Sender**
  - Support email + developer email: your email
  - Add yourself as a Test user.
- Application type: **Desktop app**
- Name: **Dealix Gmail Sender**
- Click Create. **Download the JSON** — note `client_id` and `client_secret`.

### 2. Enable the Gmail API

Open: https://console.cloud.google.com/apis/library/gmail.googleapis.com → click **Enable**.

### 3. Mint the refresh token (run on your laptop)

```bash
pip install google-auth-oauthlib
python - << 'PY'
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/gmail.send'],
)
creds = flow.run_local_server(port=0, prompt='consent', access_type='offline')
print('CLIENT_ID:    ', creds.client_id)
print('CLIENT_SECRET:', creds.client_secret)
print('REFRESH_TOKEN:', creds.refresh_token)
PY
```

A browser window opens → sign in → grant **gmail.send** scope → close.
The script prints `CLIENT_ID`, `CLIENT_SECRET`, `REFRESH_TOKEN`. **Copy them.**

### 4. Add to Railway

Service `web` → Variables → Add:

```
GMAIL_CLIENT_ID=<from step 3>
GMAIL_CLIENT_SECRET=<from step 3>
GMAIL_REFRESH_TOKEN=<from step 3>
GMAIL_SENDER_EMAIL=<your @gmail address>
GMAIL_LIST_UNSUBSCRIBE=<unsubscribe@yourdomain or same Gmail>
DAILY_EMAIL_LIMIT=50
EMAIL_BATCH_SIZE=10
EMAIL_BATCH_INTERVAL_MINUTES=90
```

Click **Review → Deploy**.

### 5. Verify

```bash
curl https://api.dealix.me/api/v1/email/status | jq
# expected: gmail_configured: true, sent_today: 0, remaining_today: 50
```

### 6. Send your first test email (to yourself)

```bash
curl -X POST https://api.dealix.me/api/v1/email/send-approved \
  -H 'content-type: application/json' \
  -d '{
    "to_email": "your@gmail.com",
    "subject": "Dealix self-test",
    "body_plain": "If you see this in your inbox, OAuth + send-pipeline are live."
  }'
```

Check your inbox. The email should land within seconds with `List-Unsubscribe` header.

## What this gets you

- `/api/v1/email/send-approved` — single send (with full compliance gate)
- `/api/v1/email/send-batch` — sends up to `EMAIL_BATCH_SIZE` from outreach queue
- `/api/v1/automation/daily-targeting/run` — generates 50 personalized targets/day
- `/api/v1/automation/followups/run` — schedules +2/+5/+10 follow-ups
- `/api/v1/automation/reply/classify` — classifies inbound replies
- `/api/v1/email/replies/sync` — manual reply ingestion

## Safety guarantees baked in

- `approval_required=True` on every queued row for the first 30 days.
- Suppression list checked before EVERY send.
- Daily limit + batch size + 90-min cooldown enforced server-side.
- `List-Unsubscribe` header (RFC 8058 one-click) on every email.
- Personal email domains (gmail/hotmail/yahoo) → demoted to manual review.
- Bounced addresses → auto-suppressed for future sends.
- `STOP` reply → auto-added to suppression list.

## Quotas to know

- Personal Gmail: ~500 messages/day
- Google Workspace: ~2,000 messages/day
- Dealix default: **50/day** — well within both limits, deliverability-safe

## Doesn't work? Common issues

| Symptom | Cause | Fix |
|---|---|---|
| `auth_error` from Gmail | Refresh token expired or scope changed | Re-run step 3 |
| `quota_exceeded` | Hit Gmail rate limit | Wait 1h, lower `EMAIL_BATCH_SIZE` |
| `403` from Gmail API | Gmail API not enabled | Step 2 |
| `gmail_not_configured` from `/email/status` | Env var typo or not deployed | Verify Railway → Review → Deploy |
| `blocked_compliance: invalid_email_format` | Recipient malformed | Check normalization in `pipelines/normalize.py` |
| `blocked_compliance: batch_cooldown` | Sent another batch <90min ago | Wait |

## Upgrade paths (later)

- **Postmark / SendGrid** for transactional volume + better deliverability dashboards.
- **dealix.me as sender domain** instead of @gmail.com (better trust + DMARC).
- **Gmail Pub/Sub push for replies** — replaces the manual `/email/replies/sync` polling.
