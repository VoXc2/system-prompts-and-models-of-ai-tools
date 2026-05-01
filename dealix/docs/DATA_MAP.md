# خريطة البيانات — Dealix

> جدول تشغيلي لفرق المنتج والقانون؛ ليس استشارة قانونية.

| فئة البيانات | أين تُخزَّن | الغرض | Controller مقابل Processor | TTL / الاحتفاظ | حذف / تصدير |
|--------------|-------------|--------|---------------------------|----------------|-------------|
| ملف تعريف مستخدم تشغيلي | DB محلي / SaaS IDP لاحقاً | مصادقة وإعدادات | حسب العقد — غالباً العميل Controller لبيانات موظفيه | راجع [`DATA_RETENTION_POLICY.md`](DATA_RETENTION_POLICY.md) | حسب إجراء DSR |
| ملف شركة / ICP | DB، ذاكرة مشروع، مستندات تكوين | تشغيل Revenue OS | العميل Controller؛ Dealix Processor للمعالجة المتفق عليها | راجع سياسة الاحتفاظ | تصدير/حذف عبر مسار DSR |
| Project memory / embeddings chunks | Supabase (`project_chunks`، إلخ) | استرجاع سياق تشغيلي | كما في DPA | TTL بعد انتهاء العقد أو طلب الحذف | حذف صفوف + إيقاف فهرسة |
| رسائل WhatsApp (وارد) | Webhook → pipeline lead؛ سجلات تطبيق | معالجة رسائل العملاء | العميل غالباً Controller للأفراد؛ Dealix وفق DPA | تقصير السجلات؛ لا محتوى حساس في traces | قمع + حذف عند الطلب |
| Gmail / Calendar | مسارات draft فقط في beta؛ OAuth tokens في Secret Manager لاحقاً | إنشاء مسودات بموافقة | العميل Controller | حسب السياسة | قطع OAuth + حذف مسودات غير مرسلة حيث أمكن |
| سجلات موافقة / compliance | `compliance_os`، جداول موافقة | PDPL / إثبات opt-in | العميل Controller؛ Dealix يعالج وفق التعليمات | سنوات التقاضي/العقد حسب المستشار | تصدير للمراجعة؛ حذف عند انتهاء الأساس |
| سجلات الفوترة | Moyasar / يدوي | تحصيل ومحاسبة | Dealix + العميل حسب النموذج | متطلبات محاسبية | وفق سياسة الاسترداد والفوترة |
| Logs / traces | Sentry، Langfuse، منصة السحابة | تشغيل وجودة AI | Dealix Processor؛ تقليل البيانات الشخصية في الرسائل | أيام–أشهر حسب الخطة | تص pseudonymization حيث أمكن |
| Webhook payloads (Hashed) | DLQ / logs مقتضبة | تصحيح وفشل المعالجة | Dealix | قصير؛ لا raw PAN | دورية مسح DLQ |

مراجع: [`SECURITY_PDPL_CHECKLIST.md`](SECURITY_PDPL_CHECKLIST.md)، [`DPA_PILOT_TEMPLATE.md`](DPA_PILOT_TEMPLATE.md)، [`docs/SUPABASE_PROJECT_MEMORY_SETUP.md`](SUPABASE_PROJECT_MEMORY_SETUP.md).
