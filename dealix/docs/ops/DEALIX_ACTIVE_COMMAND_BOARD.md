# DEALIX_ACTIVE_COMMAND_BOARD

صفحة قيادة واحدة — «الدستور» التشغيلي. حدّث التاريخ والحقول عند تغيير التركيز. أي عمل لا يمر بالسلسلة أدناه يُعتبر **غير معتمد**.

---

## سلسلة الإلزام (بدونها = غير معتمد)

```text
Command Board (هذا الملف)
→ Assigned Owner (Claude Work | Cursor | Human)
→ Allowed Files
→ Acceptance Criteria
→ PR
→ Tests / CI
→ Human Review
→ Merge
→ Runbook Update (إن لزم)
```

---

## North Star

Dealix becomes Paid Beta **real** only when:

```text
PAID_BETA_READY (staging readiness gate)
+ first payment or written commitment
+ first Proof Pack delivered
```

المرجع التنفيذي من الألف للياء: [`../PAID_BETA_FULL_RUNBOOK_AR.md`](../PAID_BETA_FULL_RUNBOOK_AR.md)

---

## Current Stage

| Field | Value |
|--------|--------|
| Stage | Paid Beta execution |
| Protected deploy branch | `ai-company` |
| Active work | فرع صغير لكل مهمة → PR إلى `ai-company` |
| Dealix API CI (مطلوب للحماية عند تفعيلها) | Jobs: **`pytest`**, **`smoke_inprocess`**, **`launch_readiness`** (انظر `.github/workflows/dealix-api-ci.yml`) |

لا commits مباشرة على `ai-company` — PR فقط، CI أخضر.

---

## Do Not Build

- marketplace
- white-label
- LinkedIn scraping
- LinkedIn auto-DM
- cold WhatsApp
- live Gmail send
- live Moyasar charge (استخدم invoice يدوي حسب الـ Runbook)
- enterprise custom features
- أي كود منتج بدون ضغط عميل مدفوع واضح
- Saudi Revenue Graph / patch كبير قبل `PAID_BETA_READY`
- Founder Console واسع قبل أول عميل
- Tenant model + ledger كامل + background jobs (ما لم يُسجّل طلب عميل مرتين أو ألم تشغيلي)

---

## Current Allowed Work

### Claude Work (استراتيجية + مبيعات + توثيق — لا كود منتج)

**Allowed:**

- `dealix/docs/`, sales kit, case study templates
- AEO/SEO plans (docs)
- battlecards, demo scripts, proof pack templates
- customer success playbooks, positioning (ضمن `POSITIONING_LOCK`)

**Forbidden:**

- `dealix/api/`, `dealix/db/`, `dealix/integrations/`, migrations
- workflow files (`.github/workflows/`) ما لم يُطلب صراحة
- تغيير pricing بدون موافقة
- تغيير safety policy بدون موافقة
- لمس `.cursor/plans`

Skill: [`.cursor/skills/dealix-strategy-sales/SKILL.md`](../../../.cursor/skills/dealix-strategy-sales/SKILL.md)

### Cursor (هندسة — أصغر PR ممكن)

**Allowed:**

- staging fixes
- tests
- smoke scripts (`smoke_staging`, `smoke_inprocess`, `launch_readiness_check`)
- API bug fixes
- frontend dashboard صغير **فقط** إن كان الـ endpoint موجوداً مسبقاً

**Forbidden:**

- ميزات كبيرة جديدة
- live sends / scraping / cold WhatsApp
- تغيير pricing أو safety rules
- لمس `.cursor/plans`

Skill: [`.cursor/skills/dealix-cursor-engineering/SKILL.md`](../../../.cursor/skills/dealix-cursor-engineering/SKILL.md)

### الطرفان — حاكم التنفيذ

Skill: [`.cursor/skills/dealix-execution-governor/SKILL.md`](../../../.cursor/skills/dealix-execution-governor/SKILL.md)

---

## Current Priorities (رُتّل حسب الأثر)

1. دمج/استقرار Layer 13 + 14 على `ai-company` (إن وُجد فرع متبقٍ)
2. Branch protection على `ai-company` + required checks: `pytest`, `smoke_inprocess`, `launch_readiness`
3. Railway staging active — Service Root = `dealix`, Start = `uvicorn api.main:app --host 0.0.0.0 --port $PORT`, Health = `/health`
4. Secret `STAGING_BASE_URL` + smoke من CI أو يدوياً (انظر [`STAGING_WORKFLOW_GITHUB.md`](STAGING_WORKFLOW_GITHUB.md))
5. `PAID_BETA_READY` على الـ URL الفعلي
6. Moyasar invoice (يدوي حسب الـ Runbook)
7. 25 outreach
8. أول pilot
9. أول Proof Pack

---

## Definition of Done لأي مهمة

- الملفات الملموسة مذكورة **قبل** العمل
- لا ملفات ممنوعة
- تشغيل tests أو أوامر التحقق المذكورة في المهمة
- المخرجات توضح ماذا تغيّر
- لا live send ولا scraping مضاف
- لا لصق أسرار في PR أو شات
- PR صغير وقابل للمراجعة
- تحديث Runbook إذا غيّر سلوك التشغيل

---

## تقرير مقبول من Claude / Cursor (أي تقرير بدون هذا = مرفوض)

```text
Objective:
Files touched:
Acceptance criteria:
Commands run:
Results:
Risks:
Blocked items:
Next human action:
```

---

## لوحة متابعة يومية (انسخها)

| المحور | السؤال | الحالة |
|--------|--------|--------|
| GitHub | هل `ai-company` محمي والـ checks مطلوبة؟ | ⬜ |
| PR | هل كل PR صغير ومحدد؟ | ⬜ |
| CI | هل `pytest` / `smoke_inprocess` / `launch_readiness` ناجحة؟ | ⬜ |
| Staging | هل Railway Active؟ | ⬜ |
| Readiness | هل `PAID_BETA_READY`؟ | ⬜ |
| Sales | هل 25 تواصل؟ | ⬜ |
| Demo | هل عندك ديمو جاهز؟ | ⬜ |
| Pilot | هل payment/commitment؟ | ⬜ |
| Proof | هل أول Proof Pack؟ | ⬜ |

---

## قاعدة منع التشتت

```text
أي شيء لا يخدم Paid Beta خلال 7 أيام = لا يُبنى الآن
```

---

## روابط سريعة

| موضوع | ملف |
|--------|------|
| أوامر staging → PAID_BETA_READY | [`STAGING_PAID_BETA_READY_ONE_SHOT.md`](STAGING_PAID_BETA_READY_ONE_SHOT.md) |
| Secret + workflow | [`STAGING_WORKFLOW_GITHUB.md`](STAGING_WORKFLOW_GITHUB.md) |
| Claude Work charter | [`DEALIX_CLAUDE_WORK_CHARTER.md`](DEALIX_CLAUDE_WORK_CHARTER.md) |
| Cursor engineering charter | [`DEALIX_CURSOR_ENGINEERING_CHARTER.md`](DEALIX_CURSOR_ENGINEERING_CHARTER.md) |
| إغلاق تجاري (نسخ/قائمة) | [`COMMERCIAL_CLOSE_COPY_CHECKLIST.md`](COMMERCIAL_CLOSE_COPY_CHECKLIST.md) |
| Claude slash commands + hooks | [`EXECUTION_GOVERNANCE_PACK.md`](EXECUTION_GOVERNANCE_PACK.md) |
| GTM يومي (٢٥ لمسة) | [`../sales-kit/DAILY_GTM_CHECKLIST_AR.md`](../sales-kit/DAILY_GTM_CHECKLIST_AR.md) |
| Pilot + Proof Pack | [`../customer-success/PILOT_7_DAY_AND_PROOF_PACK_AR.md`](../customer-success/PILOT_7_DAY_AND_PROOF_PACK_AR.md) |
| بوابات Staging A–D | [`STAGING_HUMAN_GATES_A_D_AR.md`](STAGING_HUMAN_GATES_A_D_AR.md) |
| تحقق PAID_BETA_READY | [`PAID_BETA_READY_VERIFICATION_AR.md`](PAID_BETA_READY_VERIFICATION_AR.md) |
| تقرير قبول PR (قالب) | [`PR_ACCEPTANCE_REPORT_DEALIX_GOVERNANCE_PACK.md`](PR_ACCEPTANCE_REPORT_DEALIX_GOVERNANCE_PACK.md) |

---

*آخر تحديث هيكلي: حزمة الحوكمة (Skills + Commands + PR gate + hooks doc).*
