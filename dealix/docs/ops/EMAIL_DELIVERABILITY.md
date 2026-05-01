# Email Deliverability — Dealix Operations

Practical checklist to keep Sami's Gmail (and later @dealix.me) inbox-trusted.

## Phase 1 — Personal Gmail (now)

Limits Google enforces on a personal Gmail address:

- ~500 messages/day soft cap
- 2,000 messages/day for Workspace
- Bulk sender rules apply at ~5,000+ messages/day to consumer inboxes (one-click List-Unsubscribe required, spam rate < 0.3%)

### What Dealix already enforces

- Default `DAILY_EMAIL_LIMIT=50` (well under 500)
- Default `EMAIL_BATCH_SIZE=10`
- Default `EMAIL_BATCH_INTERVAL_MINUTES=90`
- `List-Unsubscribe` header (RFC 8058 one-click) on every send
- Plain-text opt-out line at the bottom of every Arabic body
- Bounce auto-suppress: any 4xx/5xx send → recipient added to suppression list
- STOP/إيقاف reply auto-suppresses

### What Sami should monitor weekly

- Gmail Postmaster Tools → reputation: keep IP and domain at "High"
- Spam-reported rate: keep under 0.1% (Google enforces 0.3% cap)
- Bounce rate: keep under 5%; if >10% → Dealix auto-pauses sends

## Phase 2 — Move sender to @dealix.me (after first 3 paid pilots)

Once you have proof, switch to a domain you control. Better trust + survives any single Gmail action.

### Required DNS records

| Type | Name | Value | Why |
|---|---|---|---|
| TXT | `dealix.me` | `v=spf1 include:_spf.google.com -all` | SPF — declares Google as authorized sender |
| TXT | `default._domainkey.dealix.me` | (paste DKIM key from Workspace/SendGrid) | DKIM — cryptographic signing |
| TXT | `_dmarc.dealix.me` | `v=DMARC1; p=quarantine; rua=mailto:dmarc@dealix.me; pct=100` | DMARC — alignment policy |
| TXT | `_dmarc.dealix.me` | After 30 days clean: `p=reject` | Stricter policy once stable |
| MX | `dealix.me` | Workspace MX 10 priority | If using Google Workspace |

### Verification

- `dig +short TXT dealix.me`
- `dig +short TXT default._domainkey.dealix.me`
- `dig +short TXT _dmarc.dealix.me`
- mxtoolbox.com/SuperTool.aspx — paste domain → "SPF/DKIM/DMARC Lookup"

## Phase 3 — Move outbound to SendGrid / Postmark (after 5+ paid)

Personal Gmail is fine for review-and-send; transactional volume needs proper ESP.

| | SendGrid | Postmark |
|---|---|---|
| Free tier | 100/day forever | None — $15/mo for 10K |
| Saudi inbox delivery | OK | Excellent |
| Setup time | 30 min | 30 min |
| Recommended | Use after 50+ daily sends | If deliverability is critical |

After ESP setup:
1. Add SPF entry: `include:sendgrid.net` or `include:spf.mtasv.net` (Postmark)
2. Verify DKIM in ESP dashboard
3. Add `SENDGRID_API_KEY` (or `POSTMARK_API_TOKEN`) to Railway env
4. Implement a thin adapter alongside Gmail in `auto_client_acquisition/email/sendgrid_send.py`
5. Enable for low-risk emails only (P0/P1 leads, no personal-domain recipients)

## Bounce + spam-complaint handling

Already wired:
- `EmailSendLog.status='bounced'` → `data_suppression_list` row created
- Reply with "STOP" / "OPT OUT" / "إيقاف" → auto-classified as `unsubscribe` → suppression list

Manual additions (when needed):
```
POST /api/v1/data/suppression
body: {"email": "x@example.com", "reason": "manual_complaint_2026_05"}
```

## Anti-patterns (never do)

- ❌ Send 500 emails in one hour (rate limit + spam folder)
- ❌ Use generic "Dear Sir/Madam" copy at scale
- ❌ Send the exact same body to 50 recipients — Gmail dedups + flags as bulk
- ❌ Skip the opt-out line "to feel more personal"
- ❌ Send to scraped LinkedIn emails
- ❌ Reply to STOP requests with "Please confirm" — STOP is final

## Daily monitoring (automated)

`/api/v1/email/status` returns:
- `sent_today`
- `remaining_today`
- `gmail_configured`

If `sent_today > 40` and it's before noon → pause sends until tomorrow (likely spam-trap risk).

## Quarterly: rotate sender names

Saudi B2B prefers consistent senders. Don't rotate email addresses, but DO rotate:
- Subject line patterns (A/B test 3 lines per quarter)
- First-paragraph templates (tracked in `automation/score-tuner/run`)
- Send-time windows (test 9am vs 11am vs 2pm Riyadh)
