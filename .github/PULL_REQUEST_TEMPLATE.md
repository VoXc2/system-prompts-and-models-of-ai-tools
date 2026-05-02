## PR Title: [Agent/Feature/Fix] Brief Description

### Dealix Paid Beta gate (required when this PR touches `dealix/`)

- **Objective:** what does this PR move forward?
  - [ ] `PAID_BETA_READY` / staging readiness
  - [ ] first payment or written commitment
  - [ ] first Proof Pack
  - [ ] pilot delivery
  - [ ] customer proof / support
  - [ ] other (explain — must align with [`dealix/docs/ops/DEALIX_ACTIVE_COMMAND_BOARD.md`](../dealix/docs/ops/DEALIX_ACTIVE_COMMAND_BOARD.md))

- **Owner:** [ ] Claude Work (docs/sales) [ ] Cursor (engineering) [ ] Human

- **Files changed:** (list)

- **Explicitly not changed (check all that apply):**
  - [ ] no live send enabled
  - [ ] no scraping / LinkedIn automation
  - [ ] no cold WhatsApp
  - [ ] no pricing change
  - [ ] no safety rule change
  - [ ] no `.cursor/plans` change

- **Tests / verification** (paste commands + key results):

```bash
cd dealix
APP_ENV=test pytest -q --no-cov
python scripts/print_routes.py
python scripts/smoke_inprocess.py
python scripts/launch_readiness_check.py
```

- **Risk:** [ ] low [ ] medium [ ] high
- **Merge decision:** [ ] safe to merge [ ] blocked

---

### 1. Business Context & Objective
*لماذا نحتاج هذا التغيير؟ وكيف سيساهم في نمو الإيرادات أو الاستراتيجية (Sovereign OS)؟*
- 

### 2. Linked Initiative / Issues
*أرقام مهام GitHub المرتبطة (Issues)، أو اسم المبادرة في الـ PMO Agent.*
- Closes #

### 3. User & Business Impact
*النتائج المتوقعة من هذا التغيير على المستوى التجاري (أرقام، أداء، أرباح).*
- 

### 4. Technical Architecture & State Impact
*هل يغير هذا الـ PR في (Event Schema, State Machine, Policy Engine)؟ اذكر التفاصيل.*
- 

### 5. Risk Level & Governance (مهم جداً)
*اختر مستوى المخاطرة:*
- [ ] 🔴 **High Risk**: (M&A, المالية, صلاحيات الـ Board) - يتطلب مراجعتين وموافقة.
- [ ] 🟡 **Medium Risk**: (شراكات، نماذج هوامش الربح، أتمتة مبيعات عالية).
- [ ] 🟢 **Low Risk**: (تحديثات واجهة، تقارير داخلية غير مالية).

### 6. Data Privacy & Compliance (PDPL)
- [ ] لا يوجد خطر أو معالجة لبيانات حساسة.
- [ ] تم التحقق من الامتثال لسياسات حفظ ومشاركة البيانات (Data Privacy Policy).

### 7. Rollback Plan
*كيف يمكن التراجع عن هذا التعديل في حال فشله في بيئة الإنتاج מבون التأثير على العقود أو الشركاء؟*
- 

### 8. QA & Observability Updates
*كيف سيتم تتبع نجاح هذا التحديث؟ هل تم إضافة Logging/Events للوحات الـ Sovereign Dashboard؟*
- [ ] تم إضافة/تحديث الـ Unit/Integration Tests.
- [ ] تم التحديث في مصفوفة الـ Execution Matrix إذا استدعى الأمر.
