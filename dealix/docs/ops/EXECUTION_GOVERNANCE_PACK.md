# Dealix — حزمة الحوكمة التنفيذية

ربط Skills و Claude Commands و PR template وسكربتات الحماية بلوحة القيادة.

## 1. لوحة القيادة

- [`DEALIX_ACTIVE_COMMAND_BOARD.md`](DEALIX_ACTIVE_COMMAND_BOARD.md)

## 2. Cursor Agent Skills (مشروع — داخل الريبو)

| Skill | المسار |
|--------|--------|
| Execution Governor (الطرفان) | `.cursor/skills/dealix-execution-governor/SKILL.md` |
| Claude Work — استراتيجية ومبيعات | `.cursor/skills/dealix-strategy-sales/SKILL.md` |
| Cursor — هندسة | `.cursor/skills/dealix-cursor-engineering/SKILL.md` |

## 3. Claude Code — Slash commands

من جذر الريبو:

- `.claude/commands/dealix/plan.md` → `/dealix-plan` (حسب إعداد Claude Code لمجلد الأوامر)
- `.claude/commands/dealix/review.md` → `/dealix-review`
- `.claude/commands/dealix/ship.md` → `/dealix-ship`

مرجع Anthropic: [Slash commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands)

## 4. Hooks (اختياري — دمج يدوي)

- مثال إعداد + تعليمات: [`CLAUDE_CODE_HOOKS_SETUP.md`](CLAUDE_CODE_HOOKS_SETUP.md)
- سكربتات: `dealix/scripts/guard_dealix_changes.py`, `dealix/scripts/guard_dealix_bash.py`

مرجع Anthropic: [Hooks](https://docs.anthropic.com/en/docs/claude-code/hooks)

## 5. PR template

- جذر الريبو: `.github/PULL_REQUEST_TEMPLATE.md` — يتضمن قسم **Dealix Paid Beta** عند تغيير `dealix/`

## 6. أربع طبقات ضمان + ثلاث بوابات جودة

**ضمان التنفيذ:**

1. Skill يحدد السلوك  
2. Command Board يحدد الأولوية  
3. PR Template يفرض الدليل  
4. Branch Protection يمنع الدمج بدون CI ناجح  

**بوابات الجودة:**

1. `PAID_BETA_READY`  
2. payment / commitment  
3. Proof Pack مسلّم  

## 7. مسارات يومية (GTM + Pilot + Staging)

| الملف | الغرض |
|--------|--------|
| [`../sales-kit/DAILY_GTM_CHECKLIST_AR.md`](../sales-kit/DAILY_GTM_CHECKLIST_AR.md) | ٢٥ لمسة + متابعات + مواد Layer ١٤ |
| [`../customer-success/PILOT_7_DAY_AND_PROOF_PACK_AR.md`](../customer-success/PILOT_7_DAY_AND_PROOF_PACK_AR.md) | أسبوع pilot + قالب Proof Pack |
| [`STAGING_HUMAN_GATES_A_D_AR.md`](STAGING_HUMAN_GATES_A_D_AR.md) | تشيك سريع لبوابات GitHub + Railway + smoke + CI |
| [`PAID_BETA_READY_VERIFICATION_AR.md`](PAID_BETA_READY_VERIFICATION_AR.md) | أوامر `GO_PRIVATE_BETA` مقابل `PAID_BETA_READY` |
| [`PR_ACCEPTANCE_REPORT_DEALIX_GOVERNANCE_PACK.md`](PR_ACCEPTANCE_REPORT_DEALIX_GOVERNANCE_PACK.md) | قالب تقرير قبول للـ PR |
