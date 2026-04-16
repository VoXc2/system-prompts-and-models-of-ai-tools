# الامتثال السعودي وحوكمة الذكاء الاصطناعي
# Saudi Compliance & AI Governance

> **الحالة:** معتمد | **الإصدار:** 1.0 | **التاريخ:** 2026-04-16
>
> يحدد هذا الملف إطار الامتثال التنظيمي السعودي والخليجي لمنصة Dealix، مع التركيز على حماية البيانات وحوكمة الذكاء الاصطناعي.

---

## 1. الإطار التنظيمي

### 1.1 الأنظمة المطبقة

| النظام | الجهة | الحالة في Dealix |
|--------|-------|-----------------|
| **PDPL** — نظام حماية البيانات الشخصية | SDAIA | Implemented (consent engine) |
| **NCA ECC** — ضوابط الأمن السيبراني الأساسية | NCA | Partial (audit + access controls) |
| **NCA DCC** — ضوابط أمن البيانات | NCA | Partial (encryption + tenant isolation) |
| **NCA CCC** — ضوابط الحوسبة السحابية | NCA | Planned |
| **NIST AI RMF** — إطار إدارة مخاطر الذكاء الاصطناعي | NIST | Partial (risk classification) |
| **OWASP LLM Top 10** — أمن نماذج اللغة | OWASP | Partial (prompt injection, data leakage) |
| **ZATCA** — هيئة الزكاة والضريبة والجمارك | ZATCA | Implemented (VAT compliance) |

---

## 2. مصفوفة التحكم الحية (Live Control Matrix)

### 2.1 تصنيف البيانات

| نوع البيانات | مستوى الحساسية | أين تُخزن | مسارات المعالجة | الصلاحيات | الموافقات | الاحتفاظ | مسارات التصدير | ملاحظات AI |
|-------------|---------------|----------|----------------|----------|----------|---------|---------------|-----------|
| **اسم العميل** | عادي | PostgreSQL (tenant-scoped) | CRM, Communication | Tenant admin + sales | Class A | حسب العقد | JSON export via data rights | يُستخدم في personalization |
| **رقم الجوال** | حساس | PostgreSQL (encrypted at rest) | WhatsApp, SMS | Tenant admin + sales (with consent) | Class B (outbound) | PDPL consent expiry (12 شهر) | With consent only | يحتاج consent check قبل أي استخدام |
| **البريد الإلكتروني** | حساس | PostgreSQL (encrypted at rest) | Email campaigns | Tenant admin + sales (with consent) | Class B (outbound) | PDPL consent expiry | With consent only | يحتاج consent check |
| **العنوان** | حساس | PostgreSQL (tenant-scoped) | Delivery, localization | Tenant admin | Class A (read) | حسب العقد | JSON export | لا يُستخدم في AI |
| **المعلومات المالية** | حرج | PostgreSQL + Stripe (tokenized) | Billing, invoicing | Finance admin only | Class B | 7 سنوات (ZATCA) | لا يُصدّر مباشرة | لا يمر عبر AI |
| **بيانات الشركة** | عادي | PostgreSQL (tenant-scoped) | CRM, analytics, AI | Tenant users | Class A | حسب العقد | JSON export | يُستخدم في scoring + profiling |
| **تسجيلات المكالمات** | حساس | Object storage (encrypted) | Voice analysis | Tenant admin + AI | Class B (analysis) | 90 يوم | مع موافقة | transcript فقط للـ AI |
| **سجلات المحادثات** | حساس | PostgreSQL (tenant-scoped) | AI analysis, QA | Tenant admin + AI | Class A (internal) | حسب العقد | مع الحذف | يُستخدم في conversation intelligence |
| **بيانات الموافقات** | حرج | PostgreSQL (immutable) | Compliance audit | Compliance admin | لا تعديل | 5 سنوات بعد انتهاء العلاقة | كامل | لا تُعدّل أو تُحذف |
| **سجلات التدقيق** | حرج | PostgreSQL (immutable) | Compliance, forensics | Compliance admin | لا تعديل | 5 سنوات | كامل | للمراجعة فقط |

### 2.2 مصفوفة المخاطر

| الخطر | الاحتمال | الأثر | التخفيف | الحالة |
|-------|---------|------|---------|--------|
| **تسرب بيانات شخصية** | منخفض | حرج (SAR 5M) | Tenant isolation + encryption + audit | Implemented |
| **رسالة بدون موافقة** | متوسط | حرج (SAR 5M) | Consent check before every outbound | Implemented |
| **نقل بيانات عبر الحدود** | منخفض | حرج | Whitelist: {SA, AE, BH, KW, OM, QA} | Implemented |
| **وصول غير مصرح** | منخفض | عالي | RBAC + JWT + tenant scoping | Implemented |
| **AI hallucination in customer comms** | متوسط | عالي | Approval gate for outbound + QA reviewer | Implemented |
| **Prompt injection** | متوسط | عالي | Input sanitization + output validation | Partial |
| **انتهاء صلاحية الموافقة** | متوسط | حرج | Auto-expiry after 12 months | Implemented |
| **فشل حذف البيانات** | منخفض | عالي | Data rights workflow + audit | Implemented |
| **إساءة استخدام AI للبيانات** | منخفض | حرج | Scoped memory + tenant isolation | Implemented |

---

## 3. PDPL — نظام حماية البيانات الشخصية

### 3.1 متطلبات ما قبل الإطلاق

| # | المتطلب | الحالة | الدليل |
|---|---------|--------|--------|
| 1 | تسجيل الموافقة قبل المعالجة | Implemented | `ConsentManager.grant_consent()` |
| 2 | الغرض محدد لكل موافقة | Implemented | `purpose` field in consent |
| 3 | القناة مسجلة | Implemented | `channel` field in consent |
| 4 | انتهاء تلقائي بعد 12 شهر | Implemented | `expires_at` + auto-check |
| 5 | سجل تدقيق كامل | Implemented | `PDPLConsentAudit` table |
| 6 | حق الوصول (30 يوم) | Implemented | `DataRights.handle_access()` |
| 7 | حق التصحيح (30 يوم) | Implemented | `DataRights.handle_correction()` |
| 8 | حق الحذف (30 يوم) | Implemented | `DataRights.handle_deletion()` |
| 9 | حق الاعتراض | Implemented | `ConsentManager.revoke_consent()` |
| 10 | إشعار الاختراق (72 ساعة) | Documented | Runbook exists |
| 11 | تسجيل لدى SDAIA | Planned | Pre-launch requirement |
| 12 | تقييم الأثر (DPIA) | Planned | Pre-launch requirement |
| 13 | مسؤول حماية بيانات (DPO) | Planned | Role to be assigned |

### 3.2 العقوبات

| المخالفة | العقوبة | الحد الأقصى |
|---------|---------|------------|
| معالجة بدون موافقة | غرامة | SAR 5,000,000 |
| عدم الإبلاغ عن اختراق | غرامة | SAR 5,000,000 |
| نقل عبر الحدود بدون موافقة | سجن + غرامة | سنة + SAR 5,000,000 |
| تكرار المخالفة | مضاعفة | SAR 10,000,000 |

---

## 4. NCA — الهيئة الوطنية للأمن السيبراني

### 4.1 ECC — ضوابط الأمن السيبراني الأساسية

| الضابط | المتطلب | الحالة في Dealix |
|--------|---------|-----------------|
| **Governance** | سياسة أمن سيبراني معتمدة | Partial (policy.py + AGENTS.md) |
| **Asset Management** | جرد الأصول الرقمية | Partial (module-map.md) |
| **Access Control** | تحكم وصول قائم على الأدوار | Implemented (RBAC + JWT) |
| **Cryptography** | تشفير البيانات الحساسة | Implemented (TLS 1.3 + at-rest) |
| **Network Security** | حماية الشبكة | Partial (Docker network isolation) |
| **App Security** | أمن التطبيقات | Partial (input validation, CORS) |
| **Incident Response** | خطة استجابة للحوادث | Documented (runbooks) |
| **Business Continuity** | استمرارية الأعمال | Partial (backup + rollback guide) |
| **Compliance** | الامتثال التنظيمي | Implemented (PDPL engine) |
| **Third-party Security** | أمن الأطراف الثالثة | Partial (facade pattern) |

### 4.2 DCC — ضوابط أمن البيانات

| الضابط | المتطلب | الحالة |
|--------|---------|--------|
| تصنيف البيانات | مستويات حساسية محددة | Implemented (see §2.1) |
| تشفير البيانات | At-rest + in-transit | Implemented |
| التحكم بالوصول | Role-based + tenant-scoped | Implemented |
| النسخ الاحتياطي | Automated backups | Documented (deployment guide) |
| حذف آمن | Soft delete + anonymization | Implemented |
| مراقبة | Audit logging | Implemented |

---

## 5. حوكمة الذكاء الاصطناعي

### 5.1 NIST AI RMF — إطار إدارة مخاطر AI

| الوظيفة | المتطلب | التطبيق في Dealix | الحالة |
|---------|---------|------------------|--------|
| **GOVERN** | حوكمة AI على مستوى المؤسسة | Policy classes (A/B/C) + approval gates | Implemented |
| **MAP** | تحديد سياق ومخاطر AI | Agent registry + risk classification | Implemented |
| **MEASURE** | قياس أداء ومخاطر AI | QA reviewer + accuracy metrics | Partial |
| **MANAGE** | إدارة المخاطر المحددة | Self-improvement loop + canary tenants | Implemented |

### 5.2 OWASP LLM Top 10

| # | التهديد | التخفيف | الحالة |
|---|---------|---------|--------|
| LLM01 | Prompt Injection | Input sanitization + system prompt hardening | Partial |
| LLM02 | Insecure Output Handling | Output validation + structured schemas | Implemented |
| LLM03 | Training Data Poisoning | No fine-tuning on user data | Implemented |
| LLM04 | Model Denial of Service | Rate limiting + timeout | Implemented |
| LLM05 | Supply Chain Vulnerabilities | Pinned versions + `repo-hygiene.yml` | Partial |
| LLM06 | Sensitive Information Disclosure | Tenant isolation + scoped memory | Implemented |
| LLM07 | Insecure Plugin Design | Facade pattern + sandbox | Implemented |
| LLM08 | Excessive Agency | Policy gate (Class B/C) + HITL | Implemented |
| LLM09 | Overreliance | Disclaimers + human review for high-risk | Partial |
| LLM10 | Model Theft | API key rotation + provider abstraction | Implemented |

---

## 6. مصفوفة الامتثال الشاملة

| المتطلب | PDPL | NCA ECC | NCA DCC | NIST AI | OWASP LLM | ZATCA | الحالة |
|---------|------|---------|---------|---------|-----------|-------|--------|
| Consent management | ✅ | — | — | — | — | — | Implemented |
| Data classification | ✅ | ✅ | ✅ | ✅ | — | — | Implemented |
| Access control (RBAC) | ✅ | ✅ | ✅ | — | — | — | Implemented |
| Encryption (at-rest + transit) | ✅ | ✅ | ✅ | — | — | — | Implemented |
| Audit logging | ✅ | ✅ | ✅ | ✅ | — | — | Implemented |
| Data subject rights | ✅ | — | ✅ | — | — | — | Implemented |
| Tenant isolation | ✅ | ✅ | ✅ | ✅ | ✅ | — | Implemented |
| AI output validation | — | — | — | ✅ | ✅ | — | Implemented |
| Approval workflows | ✅ | — | — | ✅ | ✅ | — | Implemented |
| Incident response | ✅ | ✅ | — | — | — | — | Documented |
| VAT compliance | — | — | — | — | — | ✅ | Implemented |
| Prompt injection defense | — | — | — | ✅ | ✅ | — | Partial |
| SDAIA registration | ✅ | — | — | — | — | — | Planned |
| DPIA | ✅ | ✅ | — | ✅ | — | — | Planned |

---

## 7. سرد التدقيق (Audit Narrative)

### 7.1 القصة

Dealix مصمم **بالامتثال من البداية** وليس كإضافة لاحقة:

1. **كل رسالة صادرة** تُفحص ضد PDPL consent engine
2. **كل تعديل بيانات** يُسجل في audit log مع IP وتفاصيل التغيير
3. **كل قرار AI** يمر عبر policy gate قبل التنفيذ
4. **كل بيانات مالية** تُعالج عبر Stripe tokenization (لا تُخزن محلياً)
5. **كل tenant** معزول تماماً بـ tenant_id على كل جدول
6. **كل موافقة** لها تاريخ انتهاء وسجل تدقيق مستقل

### 7.2 سرد الثقة (Trust Narrative)

> "نحن لا نفترض الثقة — نبنيها. كل فعل في Dealix مصنف (A/B/C)، وكل فعل حساس يحتاج موافقة بشرية، وكل تنفيذ يولد إيصال تحقق، وكل بيانات شخصية محمية بنظام موافقات متوافق مع PDPL."

### 7.3 سرد الحوكمة (Governance Narrative)

> "الذكاء الاصطناعي في Dealix لا يعمل بشكل مستقل. يقترح، لكن لا يلتزم. الالتزام يتم عبر workflows حتمية تمر عبر بوابات سياسة وموافقة وتدقيق. هذا ليس ضعفاً — هذا تصميم. نريد AI يخدم العميل تحت إشراف الإنسان."

---

## 8. الفجوات والأولويات

| الفجوة | الأثر | المالك | معايير الإغلاق | الأولوية |
|--------|------|--------|---------------|---------|
| تسجيل SDAIA | قانوني | Compliance lead | تأكيد التسجيل | P0 (pre-launch) |
| DPIA لخدمات AI | قانوني | DPO | وثيقة معتمدة | P0 (pre-launch) |
| تعيين DPO | قانوني | HR | تعيين رسمي | P1 |
| خطة اختراق (72h) | تنظيمي | Security lead | خطة مختبرة | P1 |
| Prompt injection defense | أمني | Engineering | Test suite passing | P1 |
| NCA CCC compliance | تنظيمي | Ops lead | Assessment complete | P2 |

---

## الروابط

- المرجع الأعلى: [`MASTER_OPERATING_PROMPT.md`](../../MASTER_OPERATING_PROMPT.md)
- نسيج الثقة: [`trust-fabric.md`](trust-fabric.md)
- PDPL checklist: [`memory/security/pdpl-checklist.md`](../../memory/security/pdpl-checklist.md)
- Legal docs: [`docs/legal/`](../legal/)
