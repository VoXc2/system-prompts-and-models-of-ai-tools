# Dealix — تقرير الإطلاق الشامل (100٪ جاهزية) — مرجع رئيسي

> هذا المستند يجمع: الحالة، الفجوات، المنعطفات، والخطط 30/90 يوماً، وأين ينفّذ كل عمل (Cursor / Claude / Supabase / السحابة / واتساب / Google).

## 1. الحالة الحالية

فرع `dealix-v3-autonomous-revenue-os` مع أساس v3 + Personal Operator + وثائق + اختبارات + طبقة أعمال وAPI (`/api/v1/business/*`).

## 2. ما بُني

Revenue memory تجريبية، وكلاء آمنون، رادار، امتثال، علوم إيرادات، ذاكرة مشروع (هجرة + فهرسة محلية)، مشغّل عربي، بطاقات واتساب (payload فقط)، تقارير جاهزية، نموذج أعمال ووثائق GTM.

## 3. الناقص تقنياً

OAuth كامل، إرسال واتساب فعلي، رفع embeddings إنتاجي، فوترة self-serve كاملة، بعض مسارات onboarding كـ API.

## 4. ما يمنع البيتا الخاصة

غياب بيئة staging ثابتة + تجربة واتساب موقعة + 3–5 عملاء باتفاق واضح.

## 5. ما يمنع الإطلاق العام

PDPL تشغيلية، فوترة، دعم، SLOs، أمان مستقل، صفحة تسعير عامة متسقة مع الشروط القانونية.

## 6. قائمة إطلاق تقني

اختبارات، مراقبة، نسخ احتياطي، RLS مراجَأ، مفاتيح service role معزولة.

## 7. قائمة إطلاق منتج

onboarding، proof pack تلقائي، قنوات، سياسات، لقطات UI.

## 8. قائمة إطلاق أعمال

تسعير، عقود أداء، شركاء، قصص نجاح.

## 9. قائمة إطلاق GTM

قائمة 10، محتوى، webinars، إحالات.

## 10. قائمة امتثال

سجل موافقات، تصدير/حذف، قمع، سياسة واتساب.

## 11. نموذج مالي (مبدئي)

اشتراكات + إعداد + أداء (عقدي) — أرقام توضيحية في `/api/v1/business/unit-economics/demo`.

## 12. التسعير

`docs/PRICING_STRATEGY.md` + `/api/v1/business/pricing`.

## 13. أول 10 عملاء

`docs/GTM_PLAYBOOK.md` + `/api/v1/business/gtm/first-10`.

## 14. أول 100 عميل

`/api/v1/business/gtm/first-100`.

## 15. سكربتات مبيعات

`/api/v1/business/sales-script`.

## 16. سكربت تجربة (Demo)

Command center + رادار + فرصة + مسودة + موافقة.

## 17. عرض pilot

7 أيام أو أسبوعان مع proof pack — انظر كتيب GTM.

## 18. مقاييس النجاح

`/api/v1/business/metrics`.

## 19. سجل المخاطر

امتثال واتساب، توقعات AI، جودة البيانات، تعقيد المنتج، منافسة، تعقيد الشراكات.

## 20. خطة 30 يوماً

أسبوع 1: staging + 5 مكالمات اكتشاف.  
أسبوع 2: 3 pilots موقعة.  
أسبوع 3: proof packs.  
أسبوع 4: قرار التوسع أو تصحيح ICP.

## 21. خطة 90 يوماً

10 عملاء، قصص، تكامل واتساب إنتاجي بحذر، embeddings، تحسين المنتج.

## 22. ماذا يفعل سامي على الكمبيوتر

Cursor + GitHub + Supabase + Railway/Render + Postman/Bruno + إعداد Meta WhatsApp + Google Cloud للـ OAuth.

## 23. ماذا يبقى في محادثات الاستراتيجية (ChatGPT وغيره)

عصف ذهني للرسائل، مراجعة شرائح، سيناريوهات تفاوض — **من دون** تعديل الكود.

## 24. ماذا في Cursor

تنفيذ، refactor آمن، اختبارات، وثائق ريبو، PRs.

## 25. ماذا في Claude Code (إن استخدمته)

مهام طويلة موازية أو مسودات وثائق خارج الريبو — مع مزامنة يدوية للريبو.

## 26. ماذا في Supabase

هجرة، RLS، jobs للـ embeddings، بيئات منفصلة.

## 27. ماذا في Railway/Render

نشر API، secrets، مراقبة أساسية.

## 28. ماذا في WhatsApp Cloud

أرقام هوية، قوالب، webhook، توقيع، اختبار sandbox.

## 29. ماذا في Google Cloud

OAuth Gmail/Calendar، حصص، سياسات.

## 30. درجة الجاهزية الإجمالية

استدعِ `GET /api/v1/personal-operator/launch-report` — الرقم ديناميكي من النموذج الحالي؛ **لا يُعتبر ضماناً تنبؤياً** حتى تُربط ببيانات إنتاج وCI.

## 31. Innovation Roadmap (طبقة «Autonomous Growth Factory»)

**ما يُنفَّذ الآن في الريبو (MVP موثّق + API تجريبية deterministic):**

- وثيقة [`INNOVATION_STRATEGY.md`](INNOVATION_STRATEGY.md) — ٢٠ مفهوماً مع MVP مقابل تأجيل ومقاييس ومخاطر، ومقارنة موجزة مع Gong/Clari/People.ai.
- مسارات تحت `GET|POST /api/v1/innovation/*`: Command Feed **demo** و**live** (من DB مع fallback)، Growth Missions، **ten-in-ten**، AEO radar **demo**، Experiments (مع `past_experiments`)، Proof Ledger **demo** + **أحداث دائمة** + **تقرير أسبوعي**، Deal Room analyze — منطق في `auto_client_acquisition/innovation/` بدون LLM داخل هذه الطبقة وبدون إرسال حي من مسارات الابتكار.

**مراحل التمييز (معايير جاهزية):**

| مرحلة | مخرجات | معيار «جاهز للعرض» |
|--------|---------|---------------------|
| **A — تمييز قابل للعرض** | `POST .../opportunities/ten-in-ten`، `GET .../aeo/radar/demo`، فقرة مقارنة عالمية في الوثيقة | يعمل في staging مع `pytest` أخضر |
| **B — ذاكرة تشغيلية** | جدول `proof_ledger_events`، `GET .../proof-ledger/events`، `GET .../proof-ledger/report/week`، `GET .../command-feed/live` | أحداث تُسجَّل وتظهر في الـ feed أو التقرير لعميل pilot |
| **C — تخصيص** | `past_experiments` في `POST .../experiments/recommend` | على الأقل قاعدة قواعد تنعكس في التوصيات من تاريخ عميل واحد |

**ما يُؤجَّل إلى ما بعد البيانات والتشغيل:**

- AEO حقيقي (استعلامات خارجية دورية)، Deal Graph كامل في DB، مسارات LangGraph متينة، MCP gateway، Partner Marketplace خارجي، تقارير PDF مؤتمتة من الـ Ledger.

### Kill feature — «10 فرص في 10 دقائق»

وعد منتجي مركزي: من مدخلات شركة/قطاع/مدينة/عرض/هدف إلى قائمة ١٠ فرص مع Why Now ومستوى مخاطرة ومسودات عربية **بانتظار الموافقة فقط** — **`POST /api/v1/innovation/opportunities/ten-in-ten`**؛ وصف المهمة في `GET /api/v1/innovation/growth-missions`؛ الاستراتيجية في [`INNOVATION_STRATEGY.md`](INNOVATION_STRATEGY.md)؛ الإطار التشغيلي بجانب `GET /api/v1/business/gtm/first-10` عند التوسع.

---

**الخلاصة:** المنتج **قوي كأساس سوقي وتقني**؛ الإطلاق العام يحتاج تشغيلاً وامتثالاً وتجربة عميل مغلقة أولاً.
