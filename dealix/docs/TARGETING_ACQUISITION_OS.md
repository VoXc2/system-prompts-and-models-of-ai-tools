# Targeting & Acquisition OS — نظام الاستهداف الذكي

> **القاعدة:** Dealix لا يجمع كل شيء من كل مكان. يستهدف بذكاء، عبر مصادر مصرّح بها، مع موافقات بشرية، ومراقبة سمعة، وتعلّم يومي.

---

## 1. لماذا Targeting OS؟

أي أداة تستطيع جمع أرقام بالـ scraping. القوة الحقيقية:
- **Account-first**: ابحث عن الشركات قبل الأشخاص.
- **Buying Committee**: من غالباً يقرر داخل كل شركة؟
- **Contactability Gate**: هل التواصل مسموح؟
- **Channel Strategy**: ما القناة الأفضل لكل مصدر؟
- **Reputation Guard**: إذا تدهورت السمعة → أوقف القناة تلقائياً.
- **Daily Autopilot**: brief يومي + actions + Proof.
- **Self-Growth Mode**: Dealix يستهدف عملاءه بنفس النظام.

---

## 2. الوحدات (16 module)

| الوحدة | الدور |
|--------|------|
| `account_finder` | يحدد 10-25 شركة مناسبة لكل (sector, city). |
| `buyer_role_mapper` | 14 دور + خرائط buying committee حسب القطاع. |
| `contact_source_policy` | 12 مصدر، كل واحد له risk_score + channels مسموحة + retention. |
| `contactability_matrix` | 5 action modes: suggest_only / draft_only / approval_required / approved_execute / blocked. |
| `linkedin_strategy` | Lead Forms + Ads + Manual فقط. **لا scraping/auto-DM/auto-connect**. |
| `email_strategy` | Drafts + unsubscribe + pacing حسب domain reputation. |
| `whatsapp_strategy` | Opt-in only؛ rejects cold + risky phrases. |
| `social_strategy` | Listening + drafts فقط؛ لا auto-publish. |
| `outreach_scheduler` | Day-by-day plan + daily limits + opt-out enforcement. |
| `reputation_guard` | Bounce/complaint/opt-out thresholds → healthy/watch/pause. |
| `daily_autopilot` | Daily brief + 7 today actions + EOD report. |
| `acquisition_scorecard` | Pipeline / meetings / risks / productivity score. |
| `self_growth_mode` | Dealix ICP focus + daily brief + weekly learning. |
| `free_diagnostic` | Free 5-section Arabic diagnostic → paid pilot offer. |
| `contract_drafts` | Pilot/DPA/Referral/Agency/SOW outlines (legal review required). |
| `service_offers` | 7 targeting-tier offers + pricing + recommend. |

---

## 3. القنوات والقواعد

### LinkedIn
**الممنوع** (encoded in `linkedin_do_not_do()`):
- `scrape_profiles, auto_connect, auto_dm, browser_automation, fake_engagement, download_contacts_from_linkedin, buy_scraped_leads, use_unauthorized_extensions`.

**المسموح**:
- LinkedIn Lead Gen Forms (أساسي).
- LinkedIn Ads.
- البحث اليدوي المعتمد (manual research task).
- Connection requests يدوية بمسودات Dealix.

### WhatsApp
- لا cold بدون opt-in واضح.
- opt-in template يحتاج: اسم النشاط + الغرض + خيار الانسحاب.
- double opt-in موصى به.

### Email
- سياق واضح + unsubscribe.
- Pacing حسب `domain_reputation`: fresh/warmed/trusted/damaged.
- إيقاف على bounce ≥ 5%.

### Social
- API رسمية فقط.
- Listening مسموح.
- Replies = drafts بموافقة.

---

## 4. مصادر الـ Contacts (12)

| Source | Risk | Status الافتراضي |
|--------|------|-----------------|
| `crm_customer` | 5 | safe |
| `inbound_lead` | 5 | safe |
| `website_form` | 10 | safe |
| `linkedin_lead_form` | 10 | safe |
| `event_lead` | 20 | needs_review |
| `referral` | 25 | needs_review |
| `partner_intro` | 25 | needs_review |
| `manual_research` | 50 | needs_review |
| `uploaded_list` | 60 | needs_review |
| `unknown_source` | 80 | needs_review |
| `cold_list` | 95 | blocked (waتساب)/needs_review (إيميل) |
| `opt_out` | 100 | blocked (كل القنوات) |

---

## 5. Daily Operating Loop

```
صباحاً:
- 10 شركات جديدة مناسبة
- 5 رسائل drafts للموافقة
- 3 leads متأخرة (>72h)
- 1 فرصة شريك
- 1 خطر سمعة

ظهراً:
- اعتماد + إرسال 5 emails
- مراجعة 12 رقم بدون مصدر
- ديمو شريك

مساءً:
- 32 حساب تم تحليله
- 6 مسودات معتمدة
- 2 ردود إيجابية
- 1 اجتماع مجدول
- 8 مخاطر منعت
```

---

## 6. Self-Growth Mode

5 ICP focuses لـ Dealix نفسه:
1. وكالات تسويق B2B في الرياض.
2. شركات تدريب B2B في الرياض.
3. شركات استشارات نمو.
4. SaaS سعودية صغيرة-متوسطة.
5. وسطاء عقار B2B في جدة.

كل صباح: 10 شركات + 5 رسائل + اعتماد المؤسس.

أهداف شهرية: 30 Free Diagnostic، 6 Paid Pilots، 3 Growth OS، 1 وكالة شريكة.

---

## 7. Endpoints (`/api/v1/targeting/...`)

```
POST /accounts/recommend
POST /buying-committee/map
POST /contacts/evaluate
POST /uploaded-list/analyze
POST /outreach/plan
GET  /daily-autopilot/demo
GET  /self-growth/demo
POST /self-growth/targets
POST /self-growth/weekly-report
GET  /reputation/status
POST /reputation/recovery
POST /linkedin/strategy
POST /drafts/email
POST /drafts/whatsapp
POST /drafts/email-followup
POST /drafts/role-angle
POST /free-diagnostic
GET  /services
POST /services/recommend
GET  /contracts/templates
```

---

## 8. اختبارات

`tests/unit/test_targeting_os.py` — 47 اختبار:
- Account finder + Arabic + safe sources.
- Buying committee + role-based angles.
- Source classification + 12 sources.
- Contactability (opt-out, cold WA, inbound safe, unknown review).
- LinkedIn (لا scraping/auto-DM).
- Email risk + unsubscribe + 3-step follow-up.
- WhatsApp risk + opt-in templates.
- Outreach plan + daily limits.
- Reputation guard + recovery.
- Self-growth + free diagnostic + uploaded list preview.
- Contracts (legal review + PDPL).
- Acquisition scorecard.

---

## 9. ما لا تفعله

- لا scraping LinkedIn/social.
- لا auto-DM في أي منصة.
- لا cold WhatsApp.
- لا charge بدون تأكيد.
- لا scraping ToS-مخالف.
- لا وعود بنتائج مضمونة.
- لا تخزين بطاقات.
