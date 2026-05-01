# Service Tower Strategy — برج الخدمات الذاتي

> **الفكرة:** كل قدرة في Dealix تتحول إلى **Productized Service** بمواصفات: target customer + outcome + inputs + workflow + deliverables + pricing + risk + proof + upgrade path.

---

## 1. القاعدة الذهبية

**العميل لا يشتري ميزة. يشتري نتيجة منظمة.**

كل خدمة تمشي في نفس الـ pipeline:
```
Goal → Intake → Data Check → Risk Check → Strategy →
Drafts → Approval → Execution/Export → Tracking → Proof → Upsell
```

---

## 2. الـ12 خدمة (Productized)

| # | الخدمة | المدخلات | المخرجات | السعر |
|---|--------|----------|---------|-------|
| 1 | Free Growth Diagnostic | sector/city/offer/goal | 3 فرص + رسالة + مخاطر + خطة Pilot | 0 |
| 2 | List Intelligence | CSV + channels | تنظيف + أفضل 50 + رسائل | 499–1,500 |
| 3 | First 10 Opportunities Sprint | sector/city/offer/goal | 10 فرص + رسائل + Proof Pack | 499–1,500 |
| 4 | Self-Growth Operator | company profile + goals | Daily brief + drafts + reports | 999/شهر |
| 5 | Growth OS Monthly | channels + team_size | المنصة الكاملة شهرياً | 2,999/شهر |
| 6 | Email Revenue Rescue | gmail label + ICP | استخراج فرص ضائعة + drafts | 1,500–5,000 |
| 7 | Meeting Booking Sprint | prospects + calendar | invitations + briefs + follow-ups | 1,500–5,000 |
| 8 | Partner Sprint | sector + partner goal | 20 شريك + رسائل + 5 اجتماعات | 3,000–7,500 |
| 9 | Agency Partner Program | agency profile | بيع Dealix لعملاء الوكالة | 10,000–50,000 |
| 10 | WhatsApp Compliance Setup | contact list + practice | audit + opt-in templates + ledger | 1,500–4,000 |
| 11 | LinkedIn Lead Gen Setup | ICP + offer + ad budget | حملة Lead Form + ربط CRM | 2,000–7,500 |
| 12 | Executive Growth Brief | company profile | موجز يومي 3+3+3 | 499–999/شهر |

---

## 3. الـ Wizard

```
العميل يجيب:
- نوع الشركة
- الهدف
- هل عندك قائمة؟
- ما القنوات المتاحة؟
- الميزانية

النظام يوصي بخدمة واحدة + يبرر القرار.
```

ترتيب القرارات:
1. وكالة → Partner Sprint / Agency Program.
2. عنده قائمة → List Intelligence.
3. مؤسس → Self-Growth Operator.
4. CEO → Executive Growth Brief.
5. واتساب → Compliance Setup.
6. هدف rescue → Email Revenue Rescue.
7. هدف اجتماعات → Meeting Booking Sprint.
8. هدف شراكات → Partner Sprint.
9. ميزانية شهرية ≥ 2999 → Growth OS.
10. الافتراضي → First 10 Opportunities.

---

## 4. WhatsApp CEO Control

كل قرار يصل المؤسس عبر واتساب كـ كرت:
- Daily Service Brief (≤3 buttons).
- Service Approval Card (`اعتمد / عدّل / ارفض`).
- Risk Alert Card.
- End-of-Day Report.

---

## 5. Pricing Engine

ضرّابات السعر:
- `company_size`: micro 0.8x, small 1.0x, medium 1.3x, large 1.7x.
- `urgency`: normal 1.0x, rush 1.3x, asap 1.5x.
- `channels_count`: +15% لكل قناة إضافية.

Setup fee = month-equivalent للـ monthly services. السنوي بخصم 15%.

---

## 6. Upgrade Paths

```
Free Diagnostic → First 10 Opportunities → Growth OS Monthly → Agency Partner
List Intelligence → Growth OS Monthly
Self-Growth Operator → Growth OS Monthly
Email Revenue Rescue → Growth OS Monthly
Partner Sprint → Agency Partner Program
```

كل upgrade path له upsell message عربي جاهز.

---

## 7. Endpoints (`/api/v1/services/...`)

```
GET  /catalog
GET  /summary
POST /recommend
GET  /{id}/intake-questions
POST /{id}/start
GET  /{id}/workflow
GET  /{id}/deliverables
GET  /{id}/proof-pack-template
GET  /{id}/client-report-outline
GET  /{id}/operator-checklist
POST /{id}/quote
GET  /{id}/setup-fee
GET  /{id}/monthly-offer
POST /{id}/scorecard
GET  /{id}/upgrade-path
GET  /{id}/post-service-plan
GET  /ceo/daily-brief
POST /ceo/approval-card
GET  /ceo/risk-alert/demo
GET  /ceo/end-of-day/demo
```

---

## 8. اختبارات

`tests/unit/test_service_tower.py` — 38 اختبار:
- Catalog ≥12 خدمة + critical services.
- Pricing + proof metrics + deliverables موجودة.
- Wizard recommendations (agency, list, founder, CEO, budget).
- Workflow includes approval.
- Quote scaling by size.
- CEO cards ≤3 buttons + لا live send.
- Upgrade paths.
