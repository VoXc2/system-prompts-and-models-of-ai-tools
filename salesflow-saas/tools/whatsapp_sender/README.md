# WhatsApp Message Sender

Sends WhatsApp messages via the Meta Cloud API and auto-logs every send into the outreach tracker.

## Setup

```bash
export WA_ACCESS_TOKEN="your_permanent_meta_token"
export WA_PHONE_NUMBER_ID="100000000000000"
```

## Usage

```bash
# Free-text message
python sender.py send +966500000001 "مرحبا! حبيت أسألك عن..."

# Pre-defined template (WA-01 through WA-05)
python sender.py template +966500000001 WA-01

# Bulk send WA-01 to all pending prospects (max 30)
python sender.py blast WA-01 --status pending --limit 30

# Dry run — see what would be sent without actually sending
python sender.py blast WA-01 --status pending --dry-run
```

## Templates

| ID | Purpose | When |
|---|---|---|
| WA-01 | First cold outreach | Day 0 |
| WA-02 | 48h follow-up (no reply) | Day 2 |
| WA-03 | After positive reply — explain offering | After reply |
| WA-04 | Pre-call reminder | Day before call |
| WA-05 | Post-call offer summary | After call |

## Tracker integration

Every send auto-updates the outreach tracker:
- Sets status to `contacted`
- Adds a note: `Sent WA-01 via WhatsApp sender`

## Rate limiting

Blast mode sleeps 1.5s between messages (~40/min), well within Meta's standard throughput tier.
