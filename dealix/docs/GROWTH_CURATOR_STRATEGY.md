# Growth Curator Strategy — مدير التحسين الذاتي للنمو

> **الفكرة (مستلهمة من Hermes Curator):** كل أسبوع، Dealix يراجع ما كتبه ونفذه، يدمج المتشابه، يأرشف الضعيف، ويقترح المهمة التالية. لا يحتاج المالك أن يفكر كل أسبوع "ماذا أحسّن؟".

## 1. الوحدات

| الوحدة | الدور |
|--------|------|
| `message_curator` | يقيّم كل رسالة عربية (0..100) ويحدد publish/needs_edit/reject. يكشف العبارات المخاطرة + يقترح صيغة بديلة. |
| `playbook_curator` | يقيّم playbooks بناءً على outcomes (accept/reply/meeting/deal) ويُصنّف winner/promising/needs_work/candidate_archive. |
| `mission_curator` | يقيّم نتائج الميشن (TTV, opportunities, drafts, meetings, revenue) ويقرر ship_it_widely/iterate/rework. |
| `skill_inventory` | فهرس deterministic لكل قدرات Dealix (20+ skill عبر 5 طبقات). |
| `curator_report` | تقرير عربي أسبوعي يجمع الكل. |

## 2. Message Grading

`grade_message(text, sector, channel)` يفحص:
- محتوى عربي (≥30%).
- طول معقول (12-80 كلمة).
- خلوّ من 8 عبارات محظورة (ضمان 100%, آخر فرصة، ...).
- إشارات أسلوب طبيعي سعودي (تحية + لاحظت/شفت + يناسبك/تحب).
- WhatsApp: لا "عميل عزيز" ولا "لجميع العملاء".
- bonus لذكر القطاع.

## 3. Playbook Scoring

```
score = 100 * (
  0.10 * accept_rate
+ 0.20 * reply_rate
+ 0.30 * meeting_rate
+ 0.40 * deal_rate
)
```

تيرز:
- ≥70: **winner**
- ≥40: **promising**
- ≥20: **needs_work**
- <20: **candidate_archive**

استراتيجية الـrecommend: **promising أولاً** (winners مشبعة)، ثم winner، ثم بقية الـtiers.

## 4. Mission Scoring

`score_mission` يجمع:
- opportunities × 2 (max 20)
- drafts_approved × 4 (max 20)
- meetings_booked × 5 (max 20)
- revenue / 5,000 (max 20)
- risks_blocked × 5 (max 10)
- TTV ≤10min: +10، ≤60min: +5

## 5. Mission Recommender

- لو ما شُغّل `first_10_opportunities` → ابدأ به.
- لو الأولوية `fill_pipeline` → `meeting_booking_sprint`.
- لو `rescue_lost_revenue` → `revenue_leak_rescue`.
- لو `expand_partners` → `partnership_sprint`.
- الافتراضي: `customer_reactivation`.

## 6. Weekly Curator Report

`build_weekly_curator_report(messages, playbooks, missions, sector)` يُرجع:

```json
{
  "summary_ar": [
    "تمت مراجعة 24 رسالة، 5 playbook، و2 مهمة هذا الأسبوع.",
    "تم اقتراح أرشفة 4 رسالة ضعيفة الجودة.",
    "تم اكتشاف 3 أزواج رسائل متشابهة (للدمج).",
  ],
  "messages": {"total", "publishable", "needs_edit", "to_archive", "duplicate_pairs"},
  "playbooks": {"total", "winners", "promising", "to_merge_groups"},
  "missions":  {"total", "ship_it_widely", "iterate", "rework_or_retire"},
  "next_playbook": {"recommended_id", "title_ar", "reason_ar"},
  "recommended_next_action_ar": "..."
}
```

## 7. Endpoints

```
GET  /api/v1/growth-curator/skills/inventory
POST /api/v1/growth-curator/messages/grade
POST /api/v1/growth-curator/messages/improve
POST /api/v1/growth-curator/messages/duplicates
POST /api/v1/growth-curator/missions/next
POST /api/v1/growth-curator/report/weekly
GET  /api/v1/growth-curator/report/demo
```

## 8. حدود

- لا يصدر LLM call.
- لا يحذف playbooks تلقائياً — يقترح فقط.
- لا يدمج بدون موافقة.
- التقرير يبقى actionable: ≤7 أسطر summary.
