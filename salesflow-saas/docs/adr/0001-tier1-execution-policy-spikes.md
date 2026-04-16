# ADR-0001: Tier 1 Execution Policy Spikes — بوابات Temporal/OPA/OpenFGA

> **الحالة:** مقبول | **التاريخ:** 2026-04-16 | **المقرر:** Architecture Team

---

## السياق

Dealix يحتاج قرارات معمارية حاسمة حول 3 تقنيات حوكمة متقدمة:

1. **Temporal** — Durable workflow orchestration
2. **OPA (Open Policy Agent)** — External policy evaluation
3. **OpenFGA / Cedar** — Fine-grained authorization

هذه التقنيات مذكورة في الأدبيات كـ "best practice" لمنصات AI مؤسسية، لكن تبنيها بدون تقييم يعني تعقيد غير مبرر.

---

## القرار

### اعتماد نموذج Spike-before-Adopt:

> **لا تقنية تنتقل من ASSESS إلى TRIAL بدون spike مكتمل + ADR معتمد.**

---

## Spike 1: Temporal vs OpenClaw Durable Flows

### المشكلة
نحتاج durable workflow orchestration مع checkpointing, resume, timeout, compensation.

### الحالة الحالية
- **OpenClaw Durable Flows** مطبق بالفعل (`backend/app/openclaw/durable_flow.py`)
- Checkpoint-based persistence في SQLite
- Resume on restart يعمل
- Task ledger موجود

### البدائل

| البديل | المزايا | العيوب |
|--------|---------|--------|
| **OpenClaw (الحالي)** | يعمل الآن، بسيط، لا infrastructure إضافي | SQLite backend، لا clustering، لا visibility UI |
| **Temporal** | Production-grade، visibility UI، clustering، retry/timeout builtin | Infrastructure ثقيل (Temporal server + Cassandra/PG)، learning curve |
| **Inngest** | Serverless-friendly، بسيط | أقل مرونة، SaaS dependency |

### القرار
**HOLD on Temporal** — OpenClaw Durable Flows كافية لـ Phase 0-1. Temporal يُقيّم في Phase 2 إذا:
- عدد الـ tenants تجاوز 100
- الـ flows تحتاج clustering
- SQLite لم يعد يكفي

### معايير إعادة التقييم
- [ ] >100 tenant نشط
- [ ] >1000 flow execution/day
- [ ] Recovery time >5 seconds

---

## Spike 2: OPA (Open Policy Agent)

### المشكلة
سياسات الأفعال (Class A/B/C) محددة في Python code (`policy.py`). هل نحتاج external policy engine؟

### الحالة الحالية
- **3 فئات أفعال** (A/B/C) محددة في `openclaw/policy.py`
- القوائم hardcoded في Python sets
- التعديل يحتاج deploy جديد

### البدائل

| البديل | المزايا | العيوب |
|--------|---------|--------|
| **Hardcoded Python (الحالي)** | بسيط، سريع، لا infrastructure | لا runtime changes، يحتاج deploy |
| **OPA + Rego** | Runtime policy updates، rich policy language، audit | Infrastructure إضافي، Rego learning curve |
| **Cedar** | AWS-backed، أبسط من Rego | أقل نضجاً، AWS coupling |
| **Casbin** | Lightweight، multiple adapters | أقل مرونة من OPA |

### القرار
**ASSESS** — نبقى على hardcoded Python لـ Phase 0-1. OPA spike يُنفذ في Phase 1 إذا:
- عدد السياسات تجاوز 50
- العملاء يحتاجون custom policies per tenant
- التعديل المتكرر يبطئ الـ deploy cycle

### معايير إعادة التقييم
- [ ] >50 policy rule
- [ ] Tenant-specific policy request from customer
- [ ] >1 policy change per week average

---

## Spike 3: OpenFGA / Cedar

### المشكلة
الصلاحيات حالياً role-based (admin/user). هل نحتاج fine-grained authorization؟

### الحالة الحالية
- **RBAC بسيط**: admin, sales, viewer roles
- JWT token يحمل role + tenant_id
- `Depends(get_current_user)` على كل route

### البدائل

| البديل | المزايا | العيوب |
|--------|---------|--------|
| **Simple RBAC (الحالي)** | بسيط، كافي الآن | لا granularity (e.g., "can edit own deals only") |
| **OpenFGA** | Zanzibar-model، fine-grained، Google-backed | Infrastructure + learning curve |
| **Cedar (AWS)** | Simpler than OpenFGA، policy language | AWS coupling، less ecosystem |
| **Casbin** | Lightweight ABAC | Less expressive than OpenFGA |

### القرار
**ASSESS** — RBAC كافي لـ Phase 0-1. OpenFGA spike يُنفذ في Phase 2 إذا:
- عملاء مؤسسيون يحتاجون granular permissions
- نحتاج "can edit own deals only" type rules
- Compliance يتطلب fine-grained access control

### معايير إعادة التقييم
- [ ] Enterprise customer requiring granular permissions
- [ ] >5 roles needed (current: 3)
- [ ] Compliance requirement for fine-grained access logging

---

## الملخص

| التقنية | القرار | الحلقة | إعادة التقييم |
|---------|--------|--------|--------------|
| Temporal | HOLD | — | Phase 2 (>100 tenants) |
| OPA | ASSESS | — | Phase 1 (>50 rules) |
| OpenFGA/Cedar | ASSESS | — | Phase 2 (enterprise request) |

---

## العواقب

### إيجابية
- لا infrastructure overhead في Phase 0-1
- تركيز على القيمة (Revenue OS) بدل البنية التحتية
- قرارات قابلة للعكس — يمكن التبني لاحقاً

### سلبية
- Policy changes تحتاج deploy
- RBAC بسيط قد لا يكفي لعملاء مؤسسيين
- OpenClaw durability أقل من Temporal في scale

### المخاطر
- إذا جاء عميل مؤسسي كبير يحتاج fine-grained auth → يحتاج sprint طوارئ
- إذا فشل SQLite-backed durability → migration مطلوب

---

## الروابط

- رادار التقنية: [`governance/technology-radar-tier1.md`](../governance/technology-radar-tier1.md)
- مصفوفة 90 يوم: [`execution-matrix-90d-tier1.md`](../execution-matrix-90d-tier1.md)
- OpenClaw config: [`openclaw/openclaw-config.yaml`](../../openclaw/openclaw-config.yaml)
