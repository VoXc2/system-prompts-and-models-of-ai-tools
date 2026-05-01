# Intelligence Layer Strategy — الشبكة العصبية للنمو
## (Dealix Growth Neural Network)

> **الهدف:** تحويل Dealix من "منصة multi-channel" إلى **شبكة عصبية للنمو** تتعلم من قرارات صاحب النشاط، تستخرج DNA الإيرادات، وتعمل ميشنات نمو ذاتية بدلاً من الانتظار للمستخدم.

---

## 1. لماذا Intelligence Layer؟

Platform Services أعطتنا **القنوات + الأمان + الـledgers**. لكن:
- لا تتذكر ما يفضله المستخدم.
- لا تستخرج رؤى من الفائزين/الخاسرين.
- لا تقترح بطاقات قرار جاهزة كل صباح.
- لا تحاكي قبل ما ترسل.

Intelligence Layer هي الطبقة التي تجعل المنصة "تشتغل لوحدها أثناء نوم المستخدم".

---

## 2. الوحدات (10 modules)

| # | الوحدة | الدور |
|---|--------|------|
| 1 | `growth_brain` | Brain لكل عميل: قطاع، قنوات، أهداف، تفضيلات، مؤشرات. `is_ready_for_autopilot()`. |
| 2 | `command_feed` | بطاقات قرار يومية بالعربي (opportunity / revenue_leak / partner_suggestion / meeting_prep / review_response / competitive_move). |
| 3 | `action_graph` | رسم بياني للنوع: signal → action → outcome (10 أنواع حواف). |
| 4 | `mission_engine` | 7 ميشنات نمو، أهمها **Kill Feature: "10 فرص في 10 دقائق"**. |
| 5 | `decision_memory` | يتعلم من Accept / Skip / Edit / Block ويخرج preferences. |
| 6 | `trust_score` | مقياس مركّب لكل رسالة (source + opt_in + channel + content + freq + approval). |
| 7 | `revenue_dna` | يستخرج: أفضل قناة، أفضل segment، أفضل angle، أكثر اعتراض، متوسط دورة البيع. |
| 8 | `opportunity_simulator` | محاكي إلى الأمام: target_count → expected_replies/meetings/deals/pipeline_sar. |
| 9 | `competitive_moves` | رصد + رد على حركات المنافسين (price_change / new_offer / hire / funding / launch...). |
| 10 | `board_brief` | Founder Shadow Board — موجز أسبوعي: قرارات، فرص، مخاطر، علاقة، تجربة، مؤشر. |

---

## 3. Growth Brain

`build_growth_brain(payload)` يبني سجل لكل عميل:
```
customer_id, sector, regions, channels_connected,
preferred_tone, growth_priorities,
learning_signal_count, accept_rate_30d
```

**الجاهزية للأوتوبايلوت:**
```
ready = (learning_signal_count ≥ 30)
      AND (accept_rate_30d ≥ 0.40)
      AND (≥ 1 قناة موصولة)
```

قبل الجاهزية → **draft + approval فقط**.

---

## 4. Command Feed (يومي)

بطاقات بالعربي مع ≤3 أزرار، 9 أنواع:
```
opportunity, revenue_leak, partner_suggestion,
meeting_prep, review_response, ai_visibility_alert,
competitive_move, customer_reactivation, action_required
```

`build_command_feed_demo()` يرجع 6 بطاقات تجريبية واقعية.

---

## 5. Action Graph

أنواع الحواف الـ10:
```
signal_created_opportunity, message_triggered_reply,
reply_led_to_meeting, meeting_led_to_proposal,
proposal_led_to_payment, partner_suggestion_taken,
review_response_recovered_customer, approval_allowed_send,
blocked_action_prevented_risk, content_generated_lead
```

`what_works_summary(customer_id)` يُرجع: مجموع الحواف + توزيعها بالنوع → "ما الذي يعمل فعلاً".

---

## 6. Mission Engine — 7 ميشنات

| ID | الاسم | ملاحظات |
|----|-------|---------|
| **first_10_opportunities** ⭐ | 10 فرص في 10 دقائق | **Kill Feature** — يبدأ من 0 ويُسلم 10 leads بالعربي قبل أن يعتاد المستخدم على المنصة. |
| revenue_leak_rescue | استعادة الإيرادات المتسربة | عملاء توقفوا، فواتير معلقة. |
| partnership_sprint | سبرنت شراكات | Partner Graph — اقتراحات تكامل. |
| customer_reactivation | إعادة تنشيط عملاء | فترة سكون → رسالة دافئة. |
| meeting_booking_sprint | حجز اجتماعات | drafts للجدولة + اعتماد. |
| ai_visibility_sprint | Answer Engine Optimization | ظهور النشاط في Perplexity / ChatGPT / Gemini. |
| competitive_response | الرد على حركات المنافسين | يُفعّل عند رصد price_change / launch / funding. |

`recommend_missions(brain, limit=3)` يرتّب بحسب توافق القطاع + القنوات + الأولويات.

---

## 7. Decision Memory

يتعلم من 4 قرارات: `accept / skip / edit / block`.

`preferences()` يُرجع:
```
accept_rate, samples,
preferred_channels, preferred_tones, preferred_sectors,
rejected_action_types
```

يستخدمها `mission_engine` لرفع/خفض ترتيب البطاقات → الـ "warm-up" loop.

---

## 8. Trust Score

نتيجة 0..100 + verdict (`safe ≥70` / `needs_review 40-69` / `blocked <40`).

العوامل:
- `source_quality` (customer / opt_in_lead / referral / cold / unknown).
- `opt_in` (boolean).
- `channel` risk (whatsapp risk أعلى من email).
- محتوى الرسالة (عبارات محظورة: "ضمان 100%", "آخر فرصة"...).
- `frequency_count_this_week` vs `weekly_cap`.
- `approval_status`.

تطبيق فوري: قبل أي `tool_gateway.invoke_tool` → بطاقة في الـCommand Feed بدلاً من الإرسال.

---

## 9. Revenue DNA

`extract_revenue_dna(customer_id, won_deals, replies, objections)` يُرجع:
```
best_channel, best_segment, best_message_angle,
common_objection, avg_cycle_days,
deals_observed, next_experiment_ar
```

استعمال: ميشن `revenue_dna_demo` يُري المالك "هذا ما يفوز فعلاً عندك".

---

## 10. Opportunity Simulator

`simulate_opportunity(target_count, sector, avg_deal_value_sar, channel, cold_pct, quality_lift)`:

يُرجع:
```
expected_replies, expected_meetings, expected_deals,
expected_pipeline_sar, risk_score (0..100),
risks_ar, rates_used, approval_required=True
```

9 قطاعات سعودية مهيّأة (real_estate, saas, retail, food, education, healthcare, logistics, fintech, contracting).

**استعمال حرج:** تحاكِ قبل ما تنفّذ → "مع 100 جهة، النتيجة المتوقعة 6 صفقات بقيمة 300K، مخاطرة PDPL متوسطة لو 60% بارد".

---

## 11. Competitive Moves

8 أنواع حركات: `price_change, new_offer, new_hire, funding, launch, partnership, layoffs, expansion`.

`analyze_competitive_move(competitor_name, move_type, payload)` → urgency + Arabic recommended_action + approval_required.

مثال: price_change بـ-25% → urgency `high` + اقتراح بطاقة "أرسل عرض مضاد للعملاء المترددين".

---

## 12. Board Brief — Founder Shadow Board

`build_board_brief()` يُرجع موجز أسبوعي:
```
decisions_required_ar (3),
top_opportunities_ar (3),
top_risks_ar (3),
key_relationship_ar,
experiment_to_run_ar,
metric_to_watch_ar,
money_summary
```

استعمال: ميل أسبوعي يومي الأحد 7:00 ص → "هذا ما يحتاج قراركم هذا الأسبوع، وهذا ما يكشفه الذكاء الاصطناعي".

---

## 13. Endpoints (`/api/v1/intelligence/...`)

```
POST /growth-brain/build
GET  /command-feed/demo
GET  /missions
POST /missions/recommend
POST /trust-score
GET  /revenue-dna/demo
POST /revenue-dna
POST /simulate-opportunity
POST /competitive-move/analyze
GET  /board-brief/demo
POST /decisions/record
GET  /decisions/preferences
```

---

## 14. اختبارات

`tests/unit/test_intelligence_layer.py` — تغطية لكل الوحدات الـ10:
- growth brain autopilot threshold
- command feed Arabic + ≤3 buttons + critical types
- action graph add/summary + unknown edge type raises
- missions list + kill feature + recommend
- decision memory records/aggregates/empty/invalid
- trust score (cold blocked, safe, risky phrases, freq cap lowers)
- revenue DNA best channel + defaults
- simulator pipeline + cold_pct warning + unknown sector default
- competitive move urgency + unknown type + funding action
- board brief structure (3 من كل: قرار/فرصة/مخاطرة)

---

## 15. ما لا تفعله هذه الطبقة

- **لا** ترسل أي شيء فعلياً (تحت سقف tool_gateway).
- **لا** تتجاوز سياسات platform_services.
- **لا** تستخدم بيانات بدون consent.
- **لا** تنفذ ميشن بدون اعتماد المالك (إلا بعد `is_ready_for_autopilot()`).

---

## 16. الاندماج مع Platform Services

```
Platform Services        Intelligence Layer
────────────────         ────────────────────
event_bus           ←→   action_graph (يستهلك الأحداث)
identity            ←→   growth_brain (هوية → سياق)
channel_registry    ←→   simulator (rates_used per channel)
action_policy       ←→   trust_score (verdict → policy gate)
tool_gateway        ←→   command_feed (cards تُنفّذ عبر gateway)
unified_inbox       ←→   command_feed (نفس البنية، طبقة أعلى)
action_ledger       ←→   decision_memory (يقرأ الـledger)
proof_ledger        ←→   board_brief (money_summary مصدره proof)
service_catalog     ←→   mission_engine (الميشنات → خدمات قابلة للبيع)
```

---

## 17. الـ Kill Feature

**"10 فرص في 10 دقائق"** — `first_10_opportunities`:

1. عند بدء العميل، نسأل: قطاع + منطقة + قناة مفضلة.
2. خلال 10 دقائق نُسلم 10 بطاقات `opportunity` بالعربي مع `recommended_action_ar`.
3. كل بطاقة draft → اعتماد → تنفيذ.
4. إذا قبل المالك ≥4 → نزيد signal_count + accept_rate → نقترب من autopilot.

هذه الميزة تكسر "blank canvas problem" وتُري قيمة فورية قبل أن يفتح المستخدم WhatsApp Web.

---

## 18. ما يلي

- ربط `command_feed` بإشارات حقيقية (Gmail / WA Business / GBP / website forms).
- استبدال الـin-memory `_MEMORY` بـ Supabase.
- جدولة `board_brief` يوم الأحد 7 ص (Cron + email/WhatsApp).
- شحن أول 100 عميل تحت "Approval-First" لجمع أول 3,000 قرار → تدريب decision_memory الحقيقي.
