# مصفوفة التنفيذ النهائية — برنامج الإغلاق (Completion Program)

**المنتج:** Dealix — من مرجعية Tier-1 إلى تشغيل enterprise-grade  
**الصيغة:** Workstream → Deliverables → Owner → Evidence Gate → Exit Criteria → Dependencies → Risk → SLA  
**الحالة:** مصفوفة تشغيلية قابلة للتتبع أسبوعًا بأسبوع (تُحدَّث مع كل تغيير في نطاق أو مالك)

---

## كيفية استخدام المصفوفة

| العمود | المعنى |
|--------|--------|
| **Workstream** | مسار عمل رئيسي في برنامج الإغلاق |
| **Deliverables** | مخرجات ملموسة (كود، سياسات، لوحات، عقود) |
| **Owner** | دور مسؤول (يُستبدل باسم فردي عند التعيين) |
| **Evidence Gate** | ما الذي يُقبل كدليل لا يُنازع (ارتباط PR، لقطة شاشة لوحة، تقرير اختبار، سجل تدقيق) |
| **Exit Criteria** | شروط إغلاق المسار دون غموض |
| **Dependencies** | ما يجب أن يكون جاهزًا قبل الاعتماد |
| **Risk** | الخطر الرئيسي إن لم يُدار |
| **SLA** | التزام تشغيلي/جودة متفق عليه لهذا المسار أو المخرج |

**مبدأ:** لا توسع في الشعارات؛ كل صف يجب أن ينتهي بدليل قابل للمراجعة.

---

## 1) إغلاق المنتج والمعمارية (Productization & Architecture Closure)

| Workstream | Deliverables | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|------------|--------------|-------|---------------|---------------|--------------|------|-----|
| سجل current vs target | سجل معماري لكل subsystem بحالات: Current / Partial / Pilot / Production | Chief Architect + PM | ملف `architecture-register` في المستودع + جدول في لوحة داخلية | لا يوجد subsystem بدون حالة واحدة محددة | خريطة المستودع الحالية، قائمة الخدمات | تجاهل المكونات الوراثية في Celery/الوكلاء | تحديث أسبوعي إلزامي |
| قفل الطبقات الخمس | وثيقة قفل: Decision / Execution / Trust / Data / Operating Planes | Chief Architect | ADR أو وثيقة `PLANES_LOCKED` مع توقيع مراجعة | خمس طبقات مع حدود مسؤولية وواجهات بينها | سجل المعمارية أعلاه | طبقات متداخلة بدون واجهات | موافقة لجنة معمارية واحدة/ربع |
| قفل المسارات الستة للأعمال | مصفوفة مسارات أعمال مع مالك منتج لكل مسار | PM Enterprise | ربط كل مسار بـ OKR ووثيقة scope | كل مسار له entry/exit واضح | تسجيل العملاء المستهدفين | تضارب أولويات بين المسارات | مراجعة شهرية |
| أدوار الوكلاء | قفل: Observer / Recommender / Executor + سياسات ترقية الدور | AI Platform Lead | جدول في كود أو policy repo | لا تنفيذ حساس بدون دور ومصعد واضح | Trust Fabric مسودة | تجاوز صلاحيات الوكيل | انتهاك سياسة = حظر تلقائي في الـ pilot |
| بيانات وصفية للإجراءات | Approval / Reversibility / Sensitivity / Provenance / Freshness على كل إجراء حساس | Security + Backend Lead | JSON schema + تطبيق في مسار واحد على الأقل | 100% من إجراءات الـ pilot تحمل الحقول | نموذج بيانات موحد | حقول اختيارية تُترك فارغة | تغطية اختبار ≥ لمسار الـ pilot |

---

## 2) تقوية طبقة القرار (Decision Plane Hardening)

| Workstream | Deliverables | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|------------|--------------|-------|---------------|---------------|--------------|------|-----|
| توحيد المخرجات المنظمة | Schemas إلزامية: `memo_json`, `evidence_pack_json`, `risk_register_json`, `approval_packet_json`, `execution_intent_json` | AI Platform Lead | JSON Schema في المستودع + اختبارات parse | لا مخرج تشغيلي حر نصيًا في المسارات الحرجة | مكتبة Pydantic / validators | رفض مزود LLM للـ schema | fallback مسموح فقط مع تسجيل سبب |
| Structured Outputs | سياسة إلزام Structured Outputs لمسارات محددة + تكامل Responses API | AI Engineer | تكوين مزود + لوجات التزام schema | معدل فشل schema = 0 في بيئة staging لمدة أسبوعين | مفاتيح API، حصص | تكلفة زمن استجابة أعلى | p95 إضافي متفق عليه (يُسجل رقميًا) |
| Evidence pack generator | مولد حزمة أدلة مرتبط بمصادر داخلية | AI + Knowledge | عينة حزمة + روابط مصادر | كل توصية حرجة مرفقة بحزمة | KnowledgeService، pgvector | أدلة سطحية | مراجعة عينة 20 حالة/أسبوع |
| Decision memo ثنائي اللغة | قالب memo AR/EN + compiler | Product + AI | ملفات عينة موقعة | موافقة قانون/منتج على القالب | قالب العلامة | ترجمة آلية خاطئة | مراجعة بشرية لكل إصدار قالب |
| درجات الجودة | provenance / freshness / confidence scores مع تعريفات | Data Science Lead | ورقة تعريفات + حساب في كود واحد | الدرجات تظهر في API response للـ pilot | خط أنابيب بيانات | تعريفات غامضة | إصدار تعريفات versioned |

---

## 3) تقوية طبقة التنفيذ (Execution Plane Hardening)

| Workstream | Deliverables | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|------------|--------------|-------|---------------|---------------|--------------|------|-----|
| جرد سير العمل | قائمة بكل workflows مع تصنيف: short / medium / long-lived | Platform Engineer | CSV أو DB table + رابط في docs | لا workflow >15 دقيقة أو متعدد الأنظمة بدون تصنيف long-lived | مراقبة Celery، logs | فجوات في الجرد | اكتمال الجرد = gate لأي pilot جديد |
| قاعدة النقل إلى Temporal | معيار: >15 د أو >2 أنظمة أو يحتاج compensation → Temporal | Chief Architect | ADR + قائمة مرشحين | مسار واحد على الأقل في Temporal في staging | بيئة Temporal، SDK | تعقيد تشغيلي | وقت تشغيل workflow pilot ضمن SLO مسجل |
| Pilot دائم | partner approval أو DD room كـ workflow حتمي | Backend + Workflow | فيديو/سجل تشغيل + trace IDs | إكمال ناجح مع إعادة تشغيل worker دون فقدان حالة | Decision schemas، idempotency | أخطاء versioning | idempotency keys إلزامية في الـ pilot |
| سياسة التعويض | compensation + saga notes في وثيقة وكود pilot | Backend Lead | اختبار تعويض مسجل | سيناريو فشل يُعالج بدون بيانات يتيمة | نموذج بيانات المعاملات | تعويض جزئي | اختبار تدميري واحد على الأقل قبل الإنتاج |

---

## 4) تقوية طبقة الثقة (Trust Fabric Hardening)

| Workstream | Deliverables | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|------------|--------------|-------|---------------|---------------|--------------|------|-----|
| جرد السياسات | policy inventory مع مصدر الحقيقة لكل سياسة | Security Lead | جدول + روابط OPA/Rego عند التوفر | لا سياسة حرجة خارج الـ inventory | خريطة API | سياسات مكررة في الكود | مراجعة ربع سنوية |
| OPA policy packs | حزم سياسات لمسارات حساسة | Security Engineer | `opa test` في CI | فشل build عند كسر سياسة | JSON input موحد من التطبيق | تأخير CI | وقت تشغيل OPA في CI < حد متفق |
| OpenFGA model | مسودة نموذج علاقات + أمثلة tuples | IAM Lead | ملف model + اختبارات Check | كل إجراء executor يمر على Check | Keycloak/service IDs | تعقيد النموذج | Check p95 مسجل |
| Vault / Keycloak | خطط تكامل + pilot secrets/SSO | DevOps + IAM | runbook + لقطات تكوين (بدون أسرار) | خدمة pilot تستخدم secret ديناميكي | بنية تحتية | تعطل SSO | RTO/RPO مسجلين في الـ runbook |
| Tool verification ledger v1 | سجل: intended / claimed / actual / side_effects / contradiction | AI Security | جدول DB + API قراءة | 100% أدوات الـ pilot مسجلة | Decision plane metadata | سجلات غير مكتملة | تدقيق أسبوعي على عينة عشوائية |
| لوحة التناقضات | عرض حالات contradiction != none | Product + Sec | لقطة لوحة أو URL داخلي | SLA مراجعة بشري للحالات الحرجة | Ledger، alerting | ضوضاء تنبيهات | فلترة حسب خطورة |

---

## 5) طبقة البيانات والموصلات (Data & Connector Fabric)

| Workstream | Deliverables | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|------------|--------------|-------|---------------|---------------|--------------|------|-----|
| واجهات موصلات versioned | facade لكل vendor رئيسي (HubSpot، Salesforce، …) مع semver داخلي | Integrations Lead | حزمة `connectors/` + CHANGELOG | لا استدعاء خام من الوكلاء للـ vendor API | مفاتيح sandbox | كسر عند تغيير API الطرف | سياسة إهلاك إصدار + إشعار 30 يوم |
| سياسات الشبكة | retry / timeout / idempotency موحدة | Backend Lead | middleware أو مكتبة مشتركة | جميع الموصلات تستخدم المكتبة | مراقبة | زمن انتظار لانهائي | حدود timeout في الـ CI |
| غلاف الأحداث | envelope موحد (مثلاً CloudEvents fields + AsyncAPI doc) | Platform Architect | مستند AsyncAPI في المستودع | كل حدث حرج يطابق الـ envelope | schema registry | انحراف غير مكتشف | فحص schema في CI للأحداث المسجلة |
| جودة البيانات | Great Expectations أو ما يعادله على مجموعات حرجة | Data Engineer | تقرير GE في artifact | بوابة إصدار تفشل عند كسر توقع حرج | مستودع بيانات | توقعات هشة | تشغيل يومي في staging |
| طبقة مقاييس دلالية | قاموس مقاييس + طبقة استعلام | Analytics Lead | جدول تعريفات + dashboard واحد | لا لوحة تنفيذية بدون تعريف مقياس | مستودع BI | تعريفات متضاربة | نسخة قاموس لكل إصدار منتج |

---

## 6) تسليم المؤسسات (Enterprise Delivery Fabric)

| Workstream | Deliverables | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|------------|--------------|-------|---------------|---------------|--------------|------|-----|
| GitHub rulesets | rulesets على الفروع الحساسة + CODEOWNERS | DevOps Lead | لقطة إعدادات (screenshot) أو Terraform | دمج إلى main بدون checks = مستحيل | GitHub plan (Enterprise إن لزم) | قيود الخطة الخاصة | توثيق بديل (عمليات يدوية موقعة) إن تعذر الميزة |
| البيئات | dev / staging / canary / prod مع حماية نشر | DevOps | قائمة environments في docs | نشر prod يتطلب موافقة | OIDC ready | تسرب إلى prod | سجل موافقة لكل نشر prod |
| OIDC + attestations | هوية workload للنشر + attestations حيث متاح | Security + DevOps | runbook + مثال workflow | لا أسرار طويلة العمر في CI | مزود سحابي | تعقيد التكوين | تدوير مفاتيح OIDC حسب جدول |
| تدفق audit خارجي | تدفق سجلات GitHub/منصة إلى SIEM/warehouse | SecOps | ربط فعلي أو تذكرة مع موعد | لا اعتماد على retention الافتراضي وحده | SIEM | فقدان أحداث | فقدان < 1 ساعة (هدف) |

---

## 7) الجاهزية السعودية للمؤسسات (Saudi Enterprise Readiness)

| Workstream | Deliverables | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|------------|--------------|-------|---------------|---------------|--------------|------|-----|
| مصفوفة PDPL | تصنيف بيانات + سجل معالجة | DPO / Compliance | جدول مراجعة قانونية | كل نوع بيانات شخصية له أساس قانوني | سياسات المنتج | فجوات في الموافقات | تحديث عند كل ميزة تلمس PII |
| ECC / NCA | سجل فجوات جاهزية مقابل ECC 2-2024 | Security | checklist مع حالة لكل بند | لا go-live مؤسسي بدون مراجعة ECC | بنية الشبكة والتشفير | تفسير خاطئ للمتطلبات | مراجعة خارجية عند الحاجة |
| حوكمة AI | ربط ضوابط NIST AI RMF + OWASP LLM Top 10 ببوابات الإصدار | AI Governance Lead | مصفوفة ربط في المستودع | كل إصدار يمر checklist OWASP للسطح الوكيلي | Decision/Trust planes | checklist شكلية فقط | توقيع أمني على الإصدار |
| الإقامة والنقل | flags في policy engine للإقامة/النقل | Backend + Legal | اختبار سياسة + سجل قرار | قرار رفض نقل غير مصرح مسجل وقابل للتدقيق | OPA/FGA | تعارض مع مزود سحابة | اختبار سيناريو شهريًا |

---

## 8) الجاهزية التنفيذية والعميل (Executive & Customer Readiness)

| Workstream | Deliverables | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|------------|--------------|-------|---------------|---------------|--------------|------|-----|
| Executive room | لوحة حية: memo، evidence، موافقات، مخاطر | Product + Frontend | URL staging + لقطات | المدير التنفيذي يكمل جولة في <10 دقائق | كل الطبقات أعلاه | لوحة بدون بيانات حقيقية | بيانات معقمة real-shaped |
| مركز الموافقات | صفحة/تدفق موافقات موحد | Product | تسجيل شاشة لمسار كامل | لا إجراء حساس بدون سجل موافقة | Trust + Execution | ازدواجية مع أدوات خارجية | وقت رد موافقة مسجل |
| لوحات المخاطر والشركاء | heatmaps، scorecards، actual vs forecast | Analytics | dashboard مربوط بمصادر | أرقام قابلة للتتبع إلى trace/query | Data plane | مؤشرات مضللة | تعريفات مقاييس موقعة |

---

## تعريف الإنجاز (Definition of Done) — مرتبط بالمصفوفة

| الشرط | Evidence Gate المقترح |
|--------|------------------------|
| توصيات حرجة منظمة + مدعومة بأدلة | عينة توصيات + `evidence_pack_json` + مراجعة |
| التزامات طويلة عبر workflow حتمي | تشغيل Temporal/Celery مع إعادة تشغيل دون فقدان |
| إجراءات حساسة مع بيانات وصفية كاملة | فحص schema على API |
| موصلات versioned مع retry/idempotency/audit | اختبارات تكامل + CHANGELOG |
| إصدارات مع rulesets + OIDC + provenance | pipeline + سجل نشر |
| OTel + correlation IDs | trace كامل عبر خدمة pilot |
| مراجعة أمنية + red-team للسطح الوكيلي | تقرير موقّع أو تذكرة مغلقة مع ملخص |
| مسارات حساسة سعوديًا | مصفوفة PDPL/NCA مكتملة للمسار |

---

## ترتيب الأولوية التنفيذي (ملخص)

1. **التحكم والثقة** قبل توسيع الوكلاء.  
2. **التنفيذ الدائم** قبل زيادة الاستقلالية.  
3. **واجهات الموصلات** قبل زيادة استدعاءات الأدوات.  
4. **المقاييس الدلالية** قبل لوحات إضافية.  
5. **الحوكمة السعودية** قبل التوسع المؤسسي الخارجي.  
6. **غرفة الإدارة** قبل التوسع التجاري الواسع.

---

## ربط بالمستودع

| المورد | الغرض |
|--------|--------|
| `salesflow-saas/docs/ULTIMATE_EXECUTION_MASTER_AR.md` | الرؤية والمبادئ والمقاييس |
| `salesflow-saas/docs/ARCHITECTURE.md` | مرجع معماري للتطبيق الحالي |
| `salesflow-saas/AGENTS.md` | حدود الوكلاء والامتثال التشغيلي |

---

*آخر تحديث: يُحدَّث عند تعيين المالكين الفعليين وربط كل Evidence Gate بأداة (Linear/Jira/GitHub Projects).*
