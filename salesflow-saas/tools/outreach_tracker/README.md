# Outreach Tracker

A zero-dependency CLI to run a focused WhatsApp / LinkedIn / cold-call outreach
campaign. Data lives in a single CSV so you can also open it in Google Sheets.

## Quick start

```bash
cd salesflow-saas/tools/outreach_tracker

# start fresh from the template
cp outreach.template.csv outreach.csv

# add a prospect
python tracker.py add +966500000001 "شركة الرياض للعقار" --contact "محمد العتيبي" --tags real_estate

# mark as contacted after sending the first WhatsApp message
python tracker.py status +966500000001 --to contacted

# they replied
python tracker.py status +966500000001 --to replied
python tracker.py note +966500000001 "طلب مكالمة الأحد ٣م"

# check the pipeline
python tracker.py stats
python tracker.py list --status replied

# see who needs a follow-up TODAY
python tracker.py due
```

## Status machine

```
pending → contacted → replied → qualified → call_booked → closed_won
                           ↘                                ↘
                            closed_lost                      closed_lost
```

`dnc` = do-not-contact (permanent opt-out).

## Follow-up cadence

| Status | Next touch |
|---|---|
| pending | today |
| contacted | +2 days |
| replied | +1 day |
| qualified | +1 day |
| call_booked | day-of |
| closed_won | +30 days (upsell) |
| closed_lost | +90 days (revive) |

Run `python tracker.py due` every morning to get your list for the day.

## Daily discipline

From the War Mode plan:

- **30 WhatsApp** first touches / day
- **20 LinkedIn** / day
- **10 cold calls** / day

At this pace, expect in 14 days:
- ~500 total touches
- ~60–100 replies
- ~15 qualified conversations
- **3–5 paying customers**

## Importing bulk prospects

```bash
python tracker.py import contacts.csv
```

Your CSV needs at minimum a `phone` column; `company`, `contact_name`,
`channel`, and `tags` are optional.

## Google Sheets workflow

1. Upload `outreach.csv` to Google Drive → open with Sheets.
2. Filter by `status` column.
3. Sort by `next_followup_at` ascending — top row = most urgent.
4. Re-download and overwrite `outreach.csv` when done (or just keep using the CLI).

## Environment variables

- `DEALIX_TRACKER_CSV` — override the default `outreach.csv` path.
