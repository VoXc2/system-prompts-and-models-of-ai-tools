# Follow-up Automation

Reads the outreach tracker CSV and produces a **prioritized daily action list** — so every morning you know exactly who to message, who to call, and who to ignore.

## Quick start

```bash
cd salesflow-saas/tools/follow_up_automation

# show top 10 actions for today
python prioritize.py

# top 25 as JSON (for piping into another tool)
python prioritize.py --top 25 --json

# export today's action list to CSV
python prioritize.py --export today.csv

# use a custom tracker CSV path
python prioritize.py --csv /path/to/outreach.csv
```

## Scoring model (0–100)

| Component | Max | What it measures |
|---|---:|---|
| **Funnel stage** | 30 | Closer to closing = higher. `qualified` > `replied` > `contacted` > `pending`. |
| **Recency** | 30 | 1–3 days stale = highest (sweet spot). Today = low (don't annoy). >14 days = fading. |
| **Engagement** | 25 | `reply_count / touches` ratio. Prospects who reply often get boosted. |
| **Tier** | 15 | Tag-based. `enterprise` > `mid_market` > `smb`. Customize in `prioritize.py`. |

Terminal statuses (`closed_won`, `closed_lost`, `dnc`) are excluded automatically.

## Action mapping

| Status | Suggested action |
|---|---|
| `pending` | 🚀 Send WA-01 (first touch) |
| `contacted` | ⏰ Send WA-02 (48h follow-up) — *unless* <48h since last touch |
| `replied` | 💬 Manual reply + qualification |
| `qualified` | 📞 Book call today — ready to close |
| `call_booked` | 🎯 Call reminder + prep offer |

## Example output

```
▶ Top 10 priority actions for today

#   SCORE   STATUS        STALE   COMPANY                       ACTION
──────────────────────────────────────────────────────────────────────────────────
1   87      qualified     2d      شركة الرياض للعقار              📞 احجز مكالمة اليوم — جاهز للإغلاق
2   78      replied       1d      مكتب جدة                        💬 رد يدوي + تأهيل الليد
3   72      contacted     3d      شركة الشرقية                    ⏰ أرسل WA-02 (متابعة ٤٨ ساعة)
4   65      pending       —       مكتب الدمام                     🚀 أرسل WA-01 (الرسالة الأولى)
...

Focus: complete the top 10 before lunch.
```

## Daily ritual

```bash
# morning (8–9am):
python prioritize.py --export ~/Desktop/today.csv

# afternoon check-in (1pm):
python ../outreach_tracker/tracker.py stats

# end of day: update statuses for whoever you touched
python ../outreach_tracker/tracker.py status +966XXXXXXXX --to replied
```

## Customizing

Edit `prioritize.py`:

- **`FUNNEL_WEIGHTS`** — raise/lower the importance of each pipeline stage
- **`TIER_WEIGHTS`** — add your own tags (e.g. `"vip": 20`)
- **`ACTION_TEMPLATES`** — change the wording of suggested actions
- **`score_prospect()`** — tune the recency curve (currently 1–3d stale = max)

## Integration

This is a dumb CSV reader by design — zero dependencies, runs anywhere Python 3.10+ runs. If you later want to wire it to the Dealix backend directly, call:

```python
from prioritize import load_csv, prioritize
actions = prioritize(load_csv(Path("outreach.csv")))
```

...and push `actions` into `backend/app/services/ai/lead_scoring.py` as a batch update.
